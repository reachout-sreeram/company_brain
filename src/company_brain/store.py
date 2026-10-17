"""FalkorDB revision store. Graph publication uses an atomic compare-and-set query."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from .models import Bundle
from .ingestion import merge_bundle, validate_bundle


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
            data = [{"id":key(row), "payload":row.model_dump_json()} for row in rows]
            self.query(f"UNWIND $rows AS row MERGE (n:{label} {{rev:$rev,id:row.id}}) SET n.payload=row.payload", {"rev":revision,"rows":data}, write=True)
        for a in bundle.assertions:
            params = {"rev":revision,"aid":a.id,"sid":a.subject_id,"source":a.source_key,"oid":a.object_id or a.subject_id,"predicate":a.predicate}
            # All facts are assertion nodes, including scalar values. No model-generated Cypher.
            self.query("MATCH (s:Entity {rev:$rev,id:$sid}), (o:Entity {rev:$rev,id:$oid}), (a:Assertion {rev:$rev,id:$aid}), (e:Source {rev:$rev,id:$source}) MERGE (s)-[:SUBJECT]->(a) MERGE (a)-[:OBJECT]->(o) MERGE (a)-[:EVIDENCE]->(e) SET a.predicate=$predicate",params,write=True)
        for a in bundle.assertions:
            for prior in a.supersedes:
                self.query("MATCH (a:Assertion {rev:$rev,id:$aid}), (b:Assertion {rev:$rev,id:$prior}) MERGE (a)-[:SUPERSEDES]->(b)", {"rev":revision,"aid":a.id,"prior":prior},write=True)
        # Staging failures never move the head. Concurrent stale writers cannot replace it.
        rows = self.query("MERGE (m:Meta {id:'head'}) WITH m WHERE coalesce(m.rev,'')=$expected MATCH (r:Revision {id:$rev}) OPTIONAL MATCH (m)-[old:CURRENT]->() DELETE old SET m.rev=$rev MERGE (m)-[:CURRENT]->(r) RETURN r.id", {"expected":expected,"rev":revision}, write=True)
        if not rows:
            raise StoreUnavailable("graph changed during ingestion; retry from current revision")
        return revision

    def incoming(self, revision: str, target: str, allowed: list[str], limit: int) -> list[str]:
        if not allowed:
            return []
        rows = self.query("MATCH (s:Entity {rev:$rev})-[:SUBJECT]->(a:Assertion {rev:$rev})-[:OBJECT]->(o:Entity {rev:$rev,id:$target}) WHERE a.id IN $allowed RETURN a.id ORDER BY a.id LIMIT $limit", {"rev":revision,"target":target,"allowed":allowed,"limit":limit})
        return [row[0] for row in rows]

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
