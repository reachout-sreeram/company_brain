"""Deterministic, scoped resolution; every finding retains assertion/source IDs."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from .models import Caller, Scope, aware

DEPENDENCIES = {"RUNS_ON", "DEPENDS_ON", "REQUIRES"}


class Brain:
    def __init__(self, store, caller: Caller = Caller(), max_depth=8, max_results=128, freshness_days=7):
        if not 1 <= max_depth <= 16 or not 1 <= max_results <= 1024:
            raise ValueError("invalid traversal budget")
        self.store, self.caller = store, caller
        self.max_depth, self.max_results = max_depth, max_results
        self.freshness = timedelta(days=freshness_days)

    def view(self, scope=None):
        rev, bundle, hidden = self.store.read_view(self.caller.groups, scope)
        entities = {e.id:e for e in bundle.entities if self.caller.can_read(e.visibility)}
        sources = {s.key:s for s in bundle.sources if not s.revoked and self.caller.can_read(s.visibility)}
        assertions = {a.id:a for a in bundle.assertions if a.source_key in sources and a.subject_id in entities and (not a.object_id or a.object_id in entities) and (not a.target_service_id or a.target_service_id in entities)}
        return rev, bundle, entities, sources, assertions, hidden

    def find_entities(self, query: str, kind: str | None = None):
        if not query.strip() or len(query) > 200:
            raise ValueError("query must contain 1–200 characters")
        rev, _, entities, _, _, _ = self.view()
        q = query.strip().casefold()
        matches = [e.model_dump(mode="json") for e in entities.values() if (not kind or e.kind == kind) and any(q in x.casefold() for x in [e.id,e.name,*e.aliases])]
        return {"graph_revision":rev,"candidates":sorted(matches,key=lambda e:e["id"])[:self.max_results],"ambiguous":len(matches)>1,"truncated":len(matches)>self.max_results}

    def get_evidence(self, source_id: str, version: str, span_id: str | None = None):
        rev, _, _, sources, assertions, _ = self.view()
        source = sources.get(f"{source_id}@{version}")
        if not source:
            raise ValueError("source unavailable")
        result = {"graph_revision":rev,"source":source.model_dump(mode="json")}
        if span_id:
            a = assertions.get(span_id)
            if not a or a.source_key != source.key:
                raise ValueError("evidence span unavailable")
            result["span"] = {"assertion_id":a.id,"start":a.span_start,"end":a.span_end,"quote":a.quote}
        return result

    def get_history(self, entity_id: str, scope: Scope):
        rev, _, entities, _, assertions, _ = self.view(scope)
        if entity_id not in entities or entities[entity_id].scope != scope:
            raise ValueError("entity unavailable")
        rows = []
        for a in sorted(assertions.values(),key=lambda x:(x.effective_from,x.id)):
            if a.scope == scope and entity_id in {a.subject_id,a.object_id}:
                row = a.model_dump(mode="json")
                row["supersedes"] = [i for i in a.supersedes if i in assertions]
                rows.append(row)
        return {"graph_revision":rev,"entity_id":entity_id,"assertions":rows}

    def assess_retirement(self, service_id: str, scope: Scope, planned_at: datetime, *, known_at: datetime | None = None):
        planned_at = aware(planned_at)
        demo_time = os.getenv("COMPANY_BRAIN_KNOWN_AT")
        known_at = aware(known_at or (datetime.fromisoformat(demo_time.replace("Z", "+00:00")) if demo_time else datetime.now(timezone.utc)))
        rev, bundle, entities, sources, visible, hidden = self.view(scope)
        result = {"service_id":service_id,"scope":scope.model_dump(),"planned_at":planned_at.isoformat(),"known_at":known_at.isoformat(),"graph_revision":rev,"disposition":"clarification_needed","affected_workflows":[],"dependency_paths":[],"blockers":[],"conflicts":[],"owners":[],"decisions":[],"coverage":{"gaps":[],"truncated":False},"evidence":[]}
        service = entities.get(service_id)
        if not service or service.kind != "Service" or service.scope != scope:
            result["coverage"]["gaps"].append("service and scope require clarification")
            return result
        active = self.store.resolved(rev, scope, planned_at, known_at, self.caller.groups)
        def fresh(a):
            return bool(a.observed_at and timedelta(0) <= known_at-a.observed_at <= self.freshness)
        evidence_ids = set()
        gaps = result["coverage"]["gaps"]
        def record(a):
            evidence_ids.add(a.id)
        def gap(message):
            if message not in gaps:
                gaps.append(message)
        by_subject = {}
        for a in active.values():
            by_subject.setdefault(a.subject_id,[]).append(a)
        paths = self.store.dependency_paths(rev, service_id, scope, planned_at, known_at,
                                            self.caller.groups, self.max_depth, self.max_results+1)
        affected, reached, confirmed_dependencies = set(), set(), []
        if len(paths)>self.max_results:
            result["coverage"]["truncated"] = True
            gap("dependency traversal budget exhausted")
        for path in paths[:self.max_results]:
            ids, nodes = path["assertion_ids"], path["entity_ids"]
            if len(ids)>self.max_depth:
                result["coverage"]["truncated"] = True
                gap("dependency traversal budget exhausted")
                continue
            if len(nodes)!=len(set(nodes)):
                gap("dependency cycle requires verification")
                continue
            consumer = nodes[0]
            reached.add(consumer)
            for aid in ids: record(active[aid])
            path_fresh = all(fresh(active[i]) for i in ids)
            result["dependency_paths"].append({"consumer_id":consumer,"assertion_ids":ids,"fresh":path_fresh})
            if not path_fresh:
                gap(f"stale dependency evidence: {consumer}")
            elif entities[consumer].kind in {"Job","Service","Workflow"}:
                confirmed_dependencies.append(ids[0])
            if entities[consumer].kind == "Workflow": affected.add(consumer)
        result["affected_workflows"] = sorted(affected)
        result["blockers"] = [{"kind":"active_dependency","assertion_ids":[aid],"entity_id":active[aid].subject_id} for aid in sorted(set(confirmed_dependencies))]
        related = set(reached)
        context_paths = [(nodes, aids) for path in paths[:self.max_results]
                         for nodes, aids in zip(path.get("context_nodes",[]),path.get("context_assertions",[]))]
        tasks = set()
        for nodes, aids in context_paths:
            if len(aids)>self.max_depth:
                gap("migration traversal budget exhausted"); result["coverage"]["truncated"]=True
                continue
            if len(nodes)!=len(set(nodes)):
                gap("migration cycle requires verification")
            for aid in aids: record(active[aid])
            tasks.update(nodes[1:]); related.update(nodes[1:])
        if len(tasks)>self.max_results:
            gap("migration traversal budget exhausted"); result["coverage"]["truncated"]=True
        for task in sorted(tasks)[:self.max_results]:
            facts = by_subject.get(task,[])
            statuses = [a for a in facts if a.predicate == "STATUS"]
            for a in statuses: record(a)
            values = {a.value for a in statuses}
            if len(values)>1:
                result["conflicts"].append({"kind":"task_status_conflict","entity_id":task,"assertion_ids":sorted(a.id for a in statuses)})
            if not statuses:
                gap(f"missing migration state: {task}")
            if statuses and ("complete" not in values or len(values)>1):
                result["blockers"].append({"kind":"migration_prerequisite","entity_id":task,"assertion_ids":sorted(a.id for a in statuses)})
            for status in statuses:
                if status.value != "complete": continue
                for consumer in reached:
                    if any(a.predicate=="MIGRATION_TRACKED_BY" and a.object_id==task for a in by_subject.get(consumer,[])):
                        usage = [a for a in by_subject.get(consumer,[]) if a.predicate in DEPENDENCIES and a.object_id==service_id and fresh(a) and a.observed_at >= (status.observed_at or status.effective_from)]
                        for a in usage:
                            result["conflicts"].append({"kind":"completion_vs_usage","entity_id":consumer,"assertion_ids":[status.id,a.id]})
                            record(a)
        for entity_id in sorted(related):
            owner_facts = [a for a in by_subject.get(entity_id,[]) if a.predicate=="OWNED_BY"]
            for a in owner_facts:
                record(a); result["owners"].append({"entity_id":entity_id,"owner_id":a.object_id,"assertion_id":a.id})
            if entities[entity_id].kind in {"Job","MigrationTask"} and not owner_facts:
                gap(f"current owner missing: {entity_id}")
            if len({a.object_id for a in owner_facts})>1:
                result["conflicts"].append({"kind":"ownership_conflict","entity_id":entity_id,"assertion_ids":sorted(a.id for a in owner_facts)})
        for a in active.values():
            if a.predicate=="PERMITS_USE" and a.object_id in reached:
                record(a); result["decisions"].append({"decision_id":a.subject_id,"assertion_id":a.id,"permits_consumer_id":a.object_id,
                    "effective_until":a.effective_until.isoformat() if a.effective_until else None})
                for blocker in result["blockers"]:
                    if blocker["kind"]=="active_dependency" and blocker["entity_id"]==a.object_id:
                        blocker.setdefault("permissions", []).append({"decision_id":a.subject_id,"assertion_id":a.id,
                            "until":a.effective_until.isoformat() if a.effective_until else None})
        inventories = [i for i in bundle.inventories if i.service_id==service_id and i.scope==scope and i.source_key in sources and sources[i.source_key].recorded_at<=known_at]
        if not inventories:
            gap("inventory coverage cannot be established")
        for inv in inventories:
            source=sources[inv.source_key]
            if not inv.complete or known_at-source.recorded_at>self.freshness:
                gap("declared inventory is incomplete or stale")
            result["coverage"]["inventory_source"] = inv.source_key
            result["coverage"]["declared_consumer_count"] = len(inv.consumer_ids) if all(i in entities for i in inv.consumer_ids) else None
            for consumer in inv.consumer_ids:
                if consumer not in entities:
                    gap("inventory coverage cannot be established"); continue
                facts=by_subject.get(consumer,[])
                checks=[]
                for a in facts:
                    if not fresh(a): continue
                    relevant_path = a.predicate in DEPENDENCIES and (a.object_id==service_id or a.subject_id in reached)
                    scoped_clear = a.predicate=="VERIFIED_CLEAR" and a.target_service_id==service_id
                    verified_migration = a.predicate in DEPENDENCIES and any(prior in visible and visible[prior].subject_id==consumer and visible[prior].object_id==service_id and a.observed_at > (visible[prior].observed_at or visible[prior].effective_from) for prior in a.supersedes)
                    if relevant_path or scoped_clear or verified_migration: checks.append(a)
                if not checks:
                    gap(f"consumer verification missing or stale: {consumer}")
                for a in checks: record(a)
        if hidden:
            gap("assessment coverage is incomplete for this caller")
        if result["conflicts"]:
            gap("conflicting evidence requires verification")
        result["disposition"] = "blocked" if result["blockers"] else "needs_verification" if gaps else "no_known_blockers"
        if len(evidence_ids)>self.max_results or any(len(result[key])>self.max_results for key in
                ("dependency_paths","blockers","conflicts","owners","decisions","affected_workflows")):
            result["coverage"]["truncated"] = True
            gap("response evidence budget exhausted")
            if result["disposition"]=="no_known_blockers": result["disposition"]="needs_verification"
        kept = set(sorted(evidence_ids)[:self.max_results])
        for key in ("dependency_paths","blockers","conflicts","owners","decisions"):
            result[key] = [row for row in result[key] if
                set(row.get("assertion_ids",[row["assertion_id"]] if "assertion_id" in row else [])) <= kept][:self.max_results]
        result["affected_workflows"] = result["affected_workflows"][:self.max_results]
        result["coverage"]["gaps"] = gaps[:self.max_results]
        for aid in sorted(kept):
            a=active[aid]; source=sources[a.source_key]
            result["evidence"].append({"assertion_id":aid,"source_id":source.id,"version":source.version,"content_hash":source.content_hash,"span_start":a.span_start,"span_end":a.span_end,"quote":a.quote,"method":a.method,"observed_at":a.observed_at.isoformat() if a.observed_at else None})
        return result
