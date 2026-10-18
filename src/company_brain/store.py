"""FalkorDB revision store. Graph publication uses an atomic compare-and-set query."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from .models import Bundle, Entity, Source, Assertion, Inventory
from .ingestion import MAX_SUPERSESSION_DEPTH, merge_bundle, validate_bundle


# Both active-fact resolution and traversal run in FalkorDB, at a pinned revision.
# Unix epoch values avoid timezone-dependent lexical comparisons.
def eligible(alias, *, include_end=True):
    until = f"\n      AND ({alias}.effective_until IS NULL OR $planned < {alias}.effective_until)" if include_end else ""
    return f"""{alias}.status='approved' AND {alias}.environment=$environment
      AND {alias}.region=$region AND {alias}.effective_from <= $planned{until}
      AND {alias}.recorded_at <= $known
      AND ({alias}.approved_at IS NULL OR {alias}.approved_at <= $known)
      AND ({alias}.observed_at IS NULL OR {alias}.observed_at <= $known)
      AND (NOT {alias}.predicate IN ['RUNS_ON','DEPENDS_ON','REQUIRES','VERIFIED_CLEAR']
           OR {alias}.time_basis='validity' OR {alias}.effective_from <= $known)
      AND {alias}.revoked=false
      AND {alias}.source_visibility IN $groups AND {alias}.subject_visibility IN $groups
      AND {alias}.object_visibility IN $groups AND {alias}.target_visibility IN $groups"""


ACTIVE_MATCH = f"""MATCH (a:Assertion {{rev:$rev}})
WHERE {eligible('a')}
OPTIONAL MATCH lineage=(new:Assertion {{rev:$rev}})-[:SUPERSEDES*1..{MAX_SUPERSESSION_DEPTH}]->(a)
WHERE {eligible('new')}
  AND all(member IN nodes(lineage) WHERE member.rev=$rev AND member.subject_id=a.subject_id
      AND {eligible('member', include_end=False)})
WITH a, count(new) AS replacements WHERE replacements=0
"""


def dependency_query(depth):
    if not 1 <= depth <= 16:
        raise ValueError('invalid traversal depth')
    # One extra hop exposes depth exhaustion; one extra row exposes result exhaustion.
    return ACTIVE_MATCH + f"""WITH collect(a.id) AS active_ids
MATCH p=(consumer:Entity {{rev:$rev}})-[:RUNS_ON|DEPENDS_ON|REQUIRES*1..{depth+1}]->(target:Entity {{rev:$rev,id:$target}})
WHERE all(edge IN relationships(p) WHERE edge.assertion_id IN active_ids)
WITH active_ids, p, consumer
OPTIONAL MATCH q=(consumer)-[:MIGRATION_TRACKED_BY|BLOCKED_BY*1..{depth+1}]->(:Entity {{rev:$rev}})
WHERE all(edge IN relationships(q) WHERE edge.assertion_id IN active_ids)
RETURN p, [node IN nodes(p) | node.id], [edge IN relationships(p) | edge.assertion_id],
       collect([node IN nodes(q) | node.id]), collect([edge IN relationships(q) | edge.assertion_id]), consumer.id AS consumer_id
ORDER BY length(p), consumer_id LIMIT $limit"""


class StoreUnavailable(RuntimeError):
    pass


class FalkorStore:
    def __init__(self, db, graph_name: str, writable: bool = False):
        if not re.fullmatch(r"company_brain_(demo|test)_[a-zA-Z0-9_-]{1,60}", graph_name):
            raise ValueError("only explicitly named company_brain_demo_* or company_brain_test_* graphs are supported")
        self.db = db
        self.graph_name = graph_name
        self.graph = db.select_graph(graph_name)
        self.writable = writable

    def query(self, statement, params=None, *, write=False):
        if write and not self.writable:
            raise PermissionError("read-only store")
        try:
            fn = self.graph.query if write else self.graph.ro_query
            return fn(statement, params or {}, timeout=1500).result_set
        except Exception:
            raise StoreUnavailable("FalkorDB query failed; no assessment available") from None

    def snapshot(self) -> tuple[str, Bundle]:
        rows = self.query("MATCH (m:Meta {id:'head'})-[:CURRENT]->(r:Revision) RETURN r.id, r.payload")
        if not rows:
            return "", Bundle()
        return rows[0][0], Bundle.model_validate_json(rows[0][1])

    def ingest(self, delta: Bundle) -> str:
        if not self.writable:
            raise PermissionError("ingestion requires operator store")
        self.query("MERGE (:Meta {id:'head'})", write=True)
        expected, old = self.snapshot()
        bundle = merge_bundle(old, delta)
        validate_bundle(bundle)
        revision = bundle.revision
        if revision == expected:
            return revision
        self.query("MERGE (r:Revision {id:$rev}) SET r.payload=$payload", {"rev": revision, "payload": bundle.model_dump_json()}, write=True)
        for label, rows, key in (("Entity", bundle.entities, lambda x:x.id), ("Source", bundle.sources, lambda x:x.key), ("Assertion", bundle.assertions, lambda x:x.id)):
            if not rows:
                continue
            entities = {e.id:e for e in bundle.entities}
            sources = {s.key:s for s in bundle.sources}
            data = []
            for row in rows:
                props = {"payload":row.model_dump_json(), "environment":row.scope.environment,
                         "region":row.scope.region}
                if label == "Entity":
                    props.update(name=row.name, kind=row.kind, visibility=row.visibility)
                if label == "Source":
                    props.update(visibility=row.visibility, revoked=row.revoked, recorded_at=row.recorded_at.timestamp())
                if label == "Assertion":
                    source = sources[row.source_key]
                    props.update(predicate=row.predicate, status=row.status, time_basis=row.time_basis, subject_id=row.subject_id,
                        object_id=row.object_id, target_service_id=row.target_service_id,
                        effective_from=row.effective_from.timestamp(),
                        effective_until=row.effective_until.timestamp() if row.effective_until else None,
                        observed_at=row.observed_at.timestamp() if row.observed_at else None,
                        approval_id=row.approval_id, approval_kind=row.approval_kind, approved_at=row.approved_at.timestamp() if row.approved_at else None,
                        source_id=row.source_id, source_version=row.source_version, source_key=row.source_key,
                        recorded_at=source.recorded_at.timestamp(), revoked=source.revoked,
                        source_visibility=source.visibility, subject_visibility=entities[row.subject_id].visibility,
                        object_visibility=entities[row.object_id].visibility if row.object_id else "public",
                        target_visibility=entities[row.target_service_id].visibility if row.target_service_id else "public")
                data.append({"id":key(row), "props":props})
            self.query(f"UNWIND $rows AS row MERGE (n:{label} {{rev:$rev,id:row.id}}) SET n += row.props",
                       {"rev":revision,"rows":data}, write=True)
        for review in bundle.reviews:
            self.query('MERGE (r:ProposalReview {rev:$rev,id:$id}) SET r.payload=$payload, r.actor=$actor, r.actor_kind=$kind, r.reviewed_at=$at',
                {'rev':revision,'id':review.id,'payload':review.model_dump_json(),'actor':review.actor,'kind':review.actor_kind,'at':review.reviewed_at.timestamp()},write=True)
            for selected in review.selections:
                self.query('MATCH (r:ProposalReview {rev:$rev,id:$review}), (a:Assertion {rev:$rev,id:$approved}), (p:Assertion {rev:$rev,id:$proposal}) MERGE (r)-[:APPROVES]->(a) MERGE (a)-[:REVIEWED_FROM]->(p)',
                    {'rev':revision,'review':review.id,'approved':selected.approved_id,'proposal':selected.proposal_id},write=True)
        for inv in bundle.inventories:
            self.query("MATCH (s:Source {rev:$rev,id:$source}) MERGE (i:Inventory {rev:$rev,payload:$payload}) MERGE (i)-[:INVENTORY_EVIDENCE]->(s)", {"rev":revision,"payload":inv.model_dump_json(),"source":inv.source_key},write=True)
        for a in bundle.assertions:
            params = {"rev":revision,"aid":a.id,"sid":a.subject_id,"source":a.source_key,"oid":a.object_id or a.subject_id,"predicate":a.predicate}
            # All facts are assertion nodes, including scalar values. No model-generated Cypher.
            self.query("MATCH (s:Entity {rev:$rev,id:$sid}), (o:Entity {rev:$rev,id:$oid}), (a:Assertion {rev:$rev,id:$aid}), (e:Source {rev:$rev,id:$source}) MERGE (s)-[:SUBJECT]->(a) MERGE (a)-[:OBJECT]->(o) MERGE (a)-[:EVIDENCE]->(e) SET a.predicate=$predicate",params,write=True)
        from .ingestion import RELATIONS
        for a in bundle.assertions:
            if a.predicate in RELATIONS:
                # Predicate is constrained by the typed schema, never arbitrary input.
                self.query(f"MATCH (s:Entity {{rev:$rev,id:$sid}}), (o:Entity {{rev:$rev,id:$oid}}), (a:Assertion {{rev:$rev,id:$aid}}) MERGE (s)-[edge:{a.predicate} {{assertion_id:$aid}}]->(o) SET edge += properties(a)",
                    {"rev":revision,"sid":a.subject_id,"oid":a.object_id,"aid":a.id},write=True)
        for a in bundle.assertions:
            for prior in a.supersedes:
                self.query("MATCH (a:Assertion {rev:$rev,id:$aid}), (b:Assertion {rev:$rev,id:$prior}) MERGE (a)-[:SUPERSEDES]->(b)", {"rev":revision,"aid":a.id,"prior":prior},write=True)
        # Derived readable projection is staged separately from immutable evidence entities.
        self.query("MATCH (e:Entity {rev:$rev}) MERGE (p:ProjectionEntity {rev:$rev,id:e.id}) SET p += properties(e)", {"rev":revision},write=True)
        configured_time = os.getenv("COMPANY_BRAIN_KNOWN_AT")
        projection_time = datetime.fromisoformat(configured_time.replace("Z", "+00:00")) if configured_time else datetime.now(timezone.utc)
        from .models import aware
        aware(projection_time)
        groups = frozenset({"public", *[e.visibility for e in bundle.entities], *[s.visibility for s in bundle.sources]})
        for scope in {e.scope for e in bundle.entities}:
            params = self.parameters(revision,scope,projection_time,projection_time,groups)
            for predicate in RELATIONS:
                self.query(ACTIVE_MATCH + f"WITH a WHERE a.predicate='{predicate}' MATCH (s:ProjectionEntity {{rev:$rev,id:a.subject_id}}), (o:ProjectionEntity {{rev:$rev,id:a.object_id}}) MERGE (s)-[edge:{predicate} {{assertion_id:a.id}}]->(o) SET edge += properties(a)",params,write=True)
        # Staging failures never move the head. Concurrent stale writers cannot replace it.
        rows = self.query("MERGE (m:Meta {id:'head'}) WITH m WHERE coalesce(m.rev,'')=$expected MATCH (r:Revision {id:$rev}) OPTIONAL MATCH (m)-[old:CURRENT]->() DELETE old SET m.rev=$rev MERGE (m)-[:CURRENT]->(r) WITH r OPTIONAL MATCH (previous:CurrentEntity) REMOVE previous:CurrentEntity SET previous:HistoricalEntity WITH DISTINCT r MATCH (current:ProjectionEntity {rev:$rev}) REMOVE current:HistoricalEntity SET current:CurrentEntity RETURN DISTINCT r.id", {"expected":expected,"rev":revision}, write=True)
        if not rows:
            raise StoreUnavailable("graph changed during ingestion; retry from current revision")
        return revision

    def read_view(self, groups, scope=None):
        """Authorized evidence rows for answer assembly; no revision JSON read."""
        rows = self.query("MATCH (m:Meta {id:'head'})-[:CURRENT]->(r:Revision) RETURN r.id")
        rev = rows[0][0] if rows else ""
        params = {"rev":rev,"groups":sorted(groups|{"public"}),"scoped":scope is not None,
                  "environment":scope.environment if scope else "", "region":scope.region if scope else ""}
        scoped = "(NOT $scoped OR (n.environment=$environment AND n.region=$region))"
        values = {}
        filters = {
            "Entity":"n.visibility IN $groups",
            "Source":"n.visibility IN $groups AND n.revoked=false",
            "Assertion":"n.source_visibility IN $groups AND n.subject_visibility IN $groups AND n.object_visibility IN $groups AND n.target_visibility IN $groups AND n.revoked=false",
        }
        for label, key, model in (("Entity","entities",Entity),("Source","sources",Source),
                                  ("Assertion","assertions",Assertion)):
            values[key] = [model.model_validate_json(row[0]) for row in self.query(
                f"MATCH (n:{label} {{rev:$rev}}) WHERE {scoped} AND {filters[label]} RETURN n.payload ORDER BY n.payload",params)]
        values["inventories"] = [Inventory.model_validate_json(row[0]) for row in self.query(
            "MATCH (i:Inventory {rev:$rev})-[:INVENTORY_EVIDENCE]->(n:Source {rev:$rev}) "
            f"WHERE {scoped} AND n.visibility IN $groups AND n.revoked=false RETURN i.payload",params)]
        hidden = self.query(f"MATCH (n:Assertion {{rev:$rev}}) WHERE {scoped} AND n.revoked=false AND NOT ({filters['Assertion']}) RETURN count(n)>0",params)[0][0]
        return rev, Bundle(**values), hidden

    def resolved(self, revision, scope, planned_at, known_at, groups):
        params = self.parameters(revision, scope, planned_at, known_at, groups)
        return {a.id:a for a in (Assertion.model_validate_json(row[0]) for row in
                self.query(ACTIVE_MATCH + "RETURN a.payload ORDER BY a.id", params))}

    @staticmethod
    def parameters(revision, scope, planned_at, known_at, groups):
        return {"rev":revision,"environment":scope.environment,"region":scope.region,
                "planned":planned_at.timestamp(),"known":known_at.timestamp(),"groups":sorted(groups|{"public"})}

    def dependency_paths(self, revision, target, scope, planned_at, known_at, groups, depth, limit):
        params = self.parameters(revision, scope, planned_at, known_at, groups)
        params.update(target=target, limit=limit)
        return [{"entity_ids":row[1],"assertion_ids":row[2],"context_nodes":row[3],"context_assertions":row[4]} for row in
                self.query(dependency_query(depth), params)]

    def reset(self, confirmation: str) -> None:
        if not self.writable or confirmation != self.graph_name:
            raise PermissionError("reset requires operator access and exact isolated graph name")
        try:
            # Never FLUSHDB: only the explicitly named isolated graph is removed.
            if self.graph_name in self.db.list_graphs():
                self.graph.delete()
                self.graph = self.db.select_graph(self.graph_name)
        except Exception:
            raise StoreUnavailable("isolated graph reset failed") from None


def connect(*, writable=False) -> FalkorStore:
    graph = os.getenv("COMPANY_BRAIN_GRAPH", "company_brain_demo_retirement")
    lite_path = os.getenv("COMPANY_BRAIN_LITE_PATH")
    try:
        if lite_path:
            from redislite.falkordb_client import FalkorDB
            path = Path(lite_path).resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
            db = FalkorDB(str(path))
        else:
            from falkordb import FalkorDB
            db = FalkorDB(unix_socket_path=os.getenv("FALKORDB_SOCKET"),host=os.getenv("FALKORDB_HOST", "127.0.0.1"), port=int(os.getenv("FALKORDB_PORT", "6379")), username=os.getenv("FALKORDB_USERNAME"), password=os.getenv("FALKORDB_PASSWORD"), socket_timeout=3, socket_connect_timeout=3)
    except ImportError:
        raise StoreUnavailable("FalkorDB runtime dependency missing; install the documented dependencies") from None
    except Exception:
        raise StoreUnavailable("FalkorDB connection failed; verify runtime, socket permissions and trusted configuration") from None
    return FalkorStore(db, graph, writable=writable)
