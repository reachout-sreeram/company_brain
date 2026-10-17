"""Deterministic, scoped resolution; every finding retains assertion/source IDs."""
from __future__ import annotations

from collections import deque
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

    def view(self):
        rev, bundle = self.store.snapshot()
        entities = {e.id:e for e in bundle.entities if self.caller.can_read(e.visibility)}
        sources = {s.key:s for s in bundle.sources if not s.revoked and self.caller.can_read(s.visibility)}
        assertions = {a.id:a for a in bundle.assertions if a.source_key in sources and a.subject_id in entities and (not a.object_id or a.object_id in entities) and (not a.target_service_id or a.target_service_id in entities)}
        return rev, bundle, entities, sources, assertions

    def find_entities(self, query: str, kind: str | None = None):
        if not query.strip() or len(query) > 200:
            raise ValueError("query must contain 1–200 characters")
        rev, _, entities, _, _ = self.view()
        q = query.strip().casefold()
        matches = [e.model_dump(mode="json") for e in entities.values() if (not kind or e.kind == kind) and any(q in x.casefold() for x in [e.id,e.name,*e.aliases])]
        return {"graph_revision":rev,"candidates":sorted(matches,key=lambda e:e["id"])[:self.max_results],"ambiguous":len(matches)>1,"truncated":len(matches)>self.max_results}

    def get_evidence(self, source_id: str, version: str, span_id: str | None = None):
        rev, _, _, sources, assertions = self.view()
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
        rev, _, entities, _, assertions = self.view()
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
        known_at = aware(known_at or datetime.now(timezone.utc))
        rev, bundle, entities, sources, visible = self.view()
        result = {"service_id":service_id,"scope":scope.model_dump(),"planned_at":planned_at.isoformat(),"known_at":known_at.isoformat(),"graph_revision":rev,"disposition":"clarification_needed","affected_workflows":[],"dependency_paths":[],"blockers":[],"conflicts":[],"owners":[],"decisions":[],"coverage":{"gaps":[],"truncated":False},"evidence":[]}
        service = entities.get(service_id)
        if not service or service.kind != "Service" or service.scope != scope:
            result["coverage"]["gaps"].append("service and scope require clarification")
            return result
        applicable = {a.id:a for a in visible.values() if a.scope == scope and a.status == "approved" and a.effective_from <= planned_at and (a.predicate not in DEPENDENCIES|{"VERIFIED_CLEAR"} or a.effective_from <= known_at) and (not a.effective_until or planned_at < a.effective_until) and sources[a.source_key].recorded_at <= known_at and (not a.observed_at or a.observed_at <= known_at)}
        superseded = {old for a in applicable.values() for old in a.supersedes}
        active = {i:a for i,a in applicable.items() if i not in superseded}
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
        allowed = sorted(i for i,a in active.items() if a.predicate in DEPENDENCIES)
        queue = deque([(service_id,[],frozenset({service_id}))])
        affected = set()
        reached = set()
        confirmed_dependencies = []
        steps = 0
        while queue:
            target,path,seen = queue.popleft()
            ids = self.store.incoming(rev,target,allowed,self.max_results+1)
            if len(ids)>self.max_results or (len(path)>=self.max_depth and ids):
                result["coverage"]["truncated"] = True
                gap("dependency traversal budget exhausted")
                if len(path)>=self.max_depth:
                    continue
            for aid in ids[:self.max_results]:
                steps += 1
                if steps>self.max_results:
                    result["coverage"]["truncated"] = True
                    gap("dependency traversal budget exhausted")
                    queue.clear()
                    break
                a = active[aid]
                new_path = [aid,*path]
                record(a)
                reached.add(a.subject_id)
                if a.subject_id in seen:
                    gap("dependency cycle requires verification")
                    continue
                path_fresh = all(fresh(active[i]) for i in new_path)
                result["dependency_paths"].append({"consumer_id":a.subject_id,"assertion_ids":new_path,"fresh":path_fresh})
                if not path_fresh:
                    gap(f"stale dependency evidence: {a.subject_id}")
                elif entities[a.subject_id].kind in {"Job","Service","Workflow"}:
                    confirmed_dependencies.append(a.id)
                if entities[a.subject_id].kind == "Workflow":
                    affected.add(a.subject_id)
                queue.append((a.subject_id,new_path,seen|{a.subject_id}))
        result["affected_workflows"] = sorted(affected)
        result["blockers"] = [{"kind":"active_dependency","assertion_ids":[aid],"entity_id":active[aid].subject_id} for aid in sorted(set(confirmed_dependencies))]
        related = set(reached)
        task_queue = deque()
        for entity_id in sorted(reached):
            for a in by_subject.get(entity_id,[]):
                if a.predicate == "MIGRATION_TRACKED_BY":
                    record(a); task_queue.append(a.object_id); related.add(a.object_id)
        visited_tasks = set()
        while task_queue:
            task = task_queue.popleft()
            if task in visited_tasks:
                continue
            if len(visited_tasks)>=self.max_results:
                gap("migration traversal budget exhausted"); result["coverage"]["truncated"]=True; break
            visited_tasks.add(task)
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
            for a in facts:
                if a.predicate=="BLOCKED_BY":
                    record(a); task_queue.append(a.object_id); related.add(a.object_id)
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
                record(a); result["decisions"].append({"decision_id":a.subject_id,"assertion_id":a.id,"permits_consumer_id":a.object_id})
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
        if result["conflicts"]:
            gap("conflicting evidence requires verification")
        result["disposition"] = "blocked" if result["blockers"] else "needs_verification" if gaps else "no_known_blockers"
        for aid in sorted(evidence_ids):
            a=active[aid]; source=sources[a.source_key]
            result["evidence"].append({"assertion_id":aid,"source_id":source.id,"version":source.version,"content_hash":source.content_hash,"span_start":a.span_start,"span_end":a.span_end,"quote":a.quote,"method":a.method,"observed_at":a.observed_at.isoformat() if a.observed_at else None})
        return result
