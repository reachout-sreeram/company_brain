"""Operator-only validation and immutable-source merge. No model controls trust."""
from __future__ import annotations

from hashlib import sha256
from .models import Assertion, Bundle

RELATIONS = {
    "RUNS_ON": ({"Job", "Service"}, {"Service"}),
    "DEPENDS_ON": ({"Service", "Job", "Workflow"}, {"Service", "Job", "Workflow"}),
    "REQUIRES": ({"Workflow", "Job"}, {"Job", "Service", "Workflow"}),
    "OWNED_BY": ({"Service", "Job", "Workflow", "MigrationTask", "Decision"}, {"Team", "Person"}),
    "MIGRATION_TRACKED_BY": ({"Job", "Service"}, {"MigrationTask"}),
    "BLOCKED_BY": ({"MigrationTask"}, {"MigrationTask"}),
    "PERMITS_USE": ({"Decision"}, {"Job", "Service"}),
}


def unique(rows, key):
    result = {}
    for row in rows:
        k = key(row)
        if k in result:
            raise ValueError(f"duplicate identity: {k}")
        result[k] = row
    return result


def validate_bundle(bundle: Bundle) -> None:
    entities = unique(bundle.entities, lambda x: x.id)
    sources = unique(bundle.sources, lambda x: x.key)
    assertions = unique(bundle.assertions, lambda x: x.id)
    unique(bundle.inventories, lambda x: (x.service_id, x.scope.environment, x.scope.region))
    for a in bundle.assertions:
        if a.subject_id not in entities or (a.object_id and a.object_id not in entities):
            raise ValueError(f"unknown entity in {a.id}")
        source = sources.get(a.source_key)
        if not source:
            raise ValueError(f"unknown source in {a.id}")
        if not (0 <= a.span_start < a.span_end <= len(source.text)) or source.text[a.span_start:a.span_end] != a.quote:
            raise ValueError(f"unsupported evidence span in {a.id}")
        if a.scope != source.scope or a.scope != entities[a.subject_id].scope:
            raise ValueError(f"scope mismatch in {a.id}")
        if a.object_id and a.scope != entities[a.object_id].scope:
            raise ValueError(f"object scope mismatch in {a.id}")
        if a.status == "approved" and a.predicate not in source.authority:
            raise ValueError(f"source lacks predicate authority for {a.id}")
        if a.predicate != "VERIFIED_CLEAR" and a.target_service_id:
            raise ValueError("target_service_id only applies to clearance")
        if a.predicate in RELATIONS:
            subjects, objects = RELATIONS[a.predicate]
            if not a.object_id or entities[a.subject_id].kind not in subjects or entities[a.object_id].kind not in objects:
                raise ValueError(f"invalid relationship types in {a.id}")
        elif a.predicate == "STATUS":
            if entities[a.subject_id].kind != "MigrationTask" or a.value not in {"open", "complete"}:
                raise ValueError(f"invalid task status in {a.id}")
        elif a.predicate == "VERIFIED_CLEAR":
            if not a.target_service_id or a.target_service_id not in entities or entities[a.target_service_id].kind != "Service" or entities[a.target_service_id].scope != a.scope:
                raise ValueError("clearance needs scoped target service")
            if entities[a.subject_id].kind not in {"Job", "Service"} or a.value != "verified" or not a.observed_at:
                raise ValueError(f"invalid clearance in {a.id}")
        if a.predicate in {"RUNS_ON", "DEPENDS_ON", "REQUIRES"} and not a.observed_at:
            raise ValueError(f"dependency observation time missing in {a.id}")
        if a.observed_at and a.observed_at > source.recorded_at:
            raise ValueError(f"observation newer than source in {a.id}")
        for prior_id in a.supersedes:
            prior = assertions.get(prior_id)
            if not prior or prior.id == a.id:
                raise ValueError(f"unknown superseded assertion in {a.id}")
            allowed = prior.predicate == a.predicate or (a.predicate == "VERIFIED_CLEAR" and prior.predicate in {"RUNS_ON", "DEPENDS_ON"})
            if not allowed or prior.subject_id != a.subject_id or prior.scope != a.scope or prior.effective_from > a.effective_from:
                raise ValueError(f"invalid scoped supersession in {a.id}")
            if a.status != "approved":
                raise ValueError("proposals cannot supersede active facts")
            if a.predicate == "VERIFIED_CLEAR" and prior.object_id != a.target_service_id:
                raise ValueError("clearance cannot supersede dependency on another service")
            if a.predicate == "VERIFIED_CLEAR" and a.observed_at <= (prior.observed_at or prior.effective_from):
                raise ValueError("clearance must be newer than dependency")
    # A supersession cycle would erase all evidence; fail ingestion instead.
    def walk(node, chain):
        if node in chain:
            raise ValueError("supersession cycle")
        for old in assertions[node].supersedes:
            walk(old, chain | {node})
    for node in assertions:
        walk(node, set())
    for inv in bundle.inventories:
        if inv.service_id not in entities or entities[inv.service_id].kind != "Service":
            raise ValueError("inventory service is invalid")
        source = sources.get(inv.source_key)
        if not source or source.scope != inv.scope or "VERIFIED_CLEAR" not in source.authority:
            raise ValueError("inventory needs trusted verification source")
        if any(i not in entities or entities[i].scope != inv.scope or entities[i].kind not in {"Job", "Service"} for i in inv.consumer_ids):
            raise ValueError("invalid inventory consumer")


def merge_bundle(old: Bundle, incoming: Bundle) -> Bundle:
    def merge(left, right, key, revoke=False):
        rows = {key(x): x for x in left}
        for row in right:
            k = key(row)
            if k in rows and rows[k] != row:
                if not (revoke and row.revoked and rows[k].model_copy(update={"revoked": True}) == row):
                    raise ValueError(f"immutable identity changed: {k}")
            rows[k] = row
        return list(rows.values())
    inventories = {(x.service_id, x.scope.environment, x.scope.region): x for x in old.inventories}
    for inv in incoming.inventories:
        inventories[(inv.service_id, inv.scope.environment, inv.scope.region)] = inv
    result = Bundle(
        entities=merge(old.entities, incoming.entities, lambda x: x.id),
        sources=merge(old.sources, incoming.sources, lambda x: x.key, revoke=True),
        assertions=merge(old.assertions, incoming.assertions, lambda x: x.id),
        inventories=list(inventories.values()),
    )
    validate_bundle(result)
    return result


def extract_bundle(manifest: Bundle, adapter) -> Bundle:
    """Trusted metadata comes from manifest; extraction produces candidates only."""
    from .extraction import RawSource
    assertions = list(manifest.assertions)
    for source in manifest.sources:
        for candidate in adapter.extract(RawSource(source_id=source.id, version=source.version, text=source.text)):
            fields = candidate.model_dump(mode="json")
            identity = sha256((source.key + candidate.model_dump_json()).encode()).hexdigest()[:24]
            assertions.append(Assertion(
                **fields, id=f"extract-{identity}", source_id=source.id, source_version=source.version,
                method=adapter.method, status="approved" if candidate.predicate in source.authority else "proposal",
            ))
    result = manifest.model_copy(update={"assertions": assertions})
    validate_bundle(result)
    return result
