"""Assessment contract tests with an explicit test double, not a graph backend.

These tests exercise deterministic reasoning only. FalkorDB integration lives in
separate opt-in tests; no extraction provider is called here.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import pytest

from company_brain.assessment import Brain
from company_brain.ingestion import merge_bundle, validate_bundle
from company_brain.models import Bundle, Scope

FIXTURES = Path(__file__).resolve().parents[1] / "data" / "synthetic"
NOW = datetime(2026, 10, 17, 12, tzinfo=timezone.utc)
SCOPE = Scope(environment="production", region="eu")


class InMemoryAssessmentTestDouble:
    """Tiny repository protocol double; never used by production code."""
    def __init__(self, bundle):
        self.bundle = bundle
        self.incoming_calls = []

    def read_view(self, groups, scope=None):
        from company_brain.models import Caller
        caller=Caller(groups=groups)
        entities={e.id:e for e in self.bundle.entities if caller.can_read(e.visibility) and (not scope or e.scope==scope)}
        sources={s.key:s for s in self.bundle.sources if not s.revoked and caller.can_read(s.visibility) and (not scope or s.scope==scope)}
        assertions=[a for a in self.bundle.assertions if a.source_key in sources and a.subject_id in entities
                    and (not a.object_id or a.object_id in entities) and (not a.target_service_id or a.target_service_id in entities)]
        hidden=any((not scope or a.scope==scope) and a not in assertions and
                   not next(s for s in self.bundle.sources if s.key==a.source_key).revoked for a in self.bundle.assertions)
        return self.bundle.revision, Bundle(entities=list(entities.values()),sources=list(sources.values()),assertions=assertions,
            inventories=[i for i in self.bundle.inventories if i.source_key in sources and (not scope or i.scope==scope)]), hidden

    def resolved(self, revision, scope, planned_at, known_at, groups):
        from company_brain.models import Caller
        caller = Caller(groups=groups)
        sources = {s.key:s for s in self.bundle.sources if not s.revoked and caller.can_read(s.visibility)}
        entities = {e.id:e for e in self.bundle.entities if caller.can_read(e.visibility)}
        lineage = {a.id:a for a in self.bundle.assertions if a.source_key in sources
            and a.subject_id in entities and (not a.object_id or a.object_id in entities)
            and (not a.target_service_id or a.target_service_id in entities)
            and a.scope==scope and a.status=='approved' and a.effective_from<=planned_at
            and (a.predicate not in {'RUNS_ON','DEPENDS_ON','REQUIRES','VERIFIED_CLEAR'} or a.effective_from<=known_at)
            and (not a.approved_at or a.approved_at<=known_at)
            and sources[a.source_key].recorded_at<=known_at and (not a.observed_at or a.observed_at<=known_at)}
        applicable={i:a for i,a in lineage.items() if not a.effective_until or planned_at<a.effective_until}
        superseded=set()
        # Test-only reference semantics; production lineage expansion stays in Cypher.
        def ancestors(node,subject,depth):
            if depth>16 or node not in lineage or lineage[node].subject_id!=subject: return
            superseded.add(node)
            for prior in lineage[node].supersedes: ancestors(prior,subject,depth+1)
        for a in applicable.values():
            for prior in a.supersedes: ancestors(prior,a.subject_id,1)
        return {i:a for i,a in applicable.items() if i not in superseded}

    def dependency_paths(self, revision, target, scope, planned_at, known_at, groups, depth, limit):
        # Test-only enumeration. Production must use the actual Cypher path query.
        active = self.resolved(revision,scope,planned_at,known_at,groups)
        paths=[]
        def expand(target, nodes, ids):
            if len(ids)>=depth+1: return
            for a in active.values():
                if a.predicate not in {'RUNS_ON','DEPENDS_ON','REQUIRES'} or a.object_id!=target or a.id in ids: continue
                row={'entity_ids':[a.subject_id,*nodes], 'assertion_ids':[a.id,*ids]}
                paths.append(row)
                expand(a.subject_id,row['entity_ids'],row['assertion_ids'])
        expand(target,[target],[])
        for path in paths:
            path['context_nodes'], path['context_assertions'] = [], []
            def context(node, nodes, aids):
                if len(aids)>=depth+1: return
                for a in active.values():
                    if a.subject_id!=node or a.predicate not in {'MIGRATION_TRACKED_BY','BLOCKED_BY'} or a.id in aids: continue
                    ns, ids = [*nodes,a.object_id], [*aids,a.id]
                    path['context_nodes'].append(ns); path['context_assertions'].append(ids)
                    context(a.object_id,ns,ids)
            context(path['entity_ids'][0],[path['entity_ids'][0]],[])
        return sorted(paths,key=lambda p:(len(p['assertion_ids']),p['entity_ids'][0]))[:limit]


def scenario(*stages):
    bundle = Bundle.model_validate_json((FIXTURES / "initial.json").read_text())
    for stage in stages:
        bundle = merge_bundle(bundle, Bundle.model_validate_json((FIXTURES / f"{stage}.json").read_text()))
    validate_bundle(bundle)
    return bundle


def assess(bundle, **options):
    return Brain(InMemoryAssessmentTestDouble(bundle), **options).assess_retirement(
        "legacy-runner", SCOPE, NOW, known_at=NOW)


def test_billing_dependency_path_blockers_owners_and_exact_evidence():
    bundle = scenario()
    result = assess(bundle)
    assert result["disposition"] == "blocked"
    assert "monthly-billing" in result["affected_workflows"]
    assert any(p["assertion_ids"] == ["requires-billing-invoice", "run-invoice-legacy"]
               for p in result["dependency_paths"])
    assert any(b["entity_id"] == "network-approval" for b in result["blockers"])
    assert any(o["entity_id"] == "network-approval" and o["owner_id"] == "security"
               for o in result["owners"])
    assert result["decisions"][0]["decision_id"] == "temporary-exception"
    sources = {s.key: s for s in bundle.sources}
    for evidence in result["evidence"]:
        source = sources[f'{evidence["source_id"]}@{evidence["version"]}']
        assert source.text[evidence["span_start"]:evidence["span_end"]] == evidence["quote"]
        assert evidence["content_hash"] == source.content_hash


def test_claimed_completion_cannot_override_runtime_usage():
    result = assess(scenario("completion"))
    assert result["disposition"] == "blocked"
    assert {c["kind"] for c in result["conflicts"]} >= {"task_status_conflict", "completion_vs_usage"}
    assert "run-invoice-legacy" in {e["assertion_id"] for e in result["evidence"]}
    assert "unapproved-chat" not in json.dumps(result)


def test_verified_migration_removes_billing_but_preserves_reporting_gap_and_history():
    bundle = scenario("completion", "migration")
    result = assess(bundle)
    assert result["disposition"] == "needs_verification"
    assert result["blockers"] == []
    assert "monthly-billing" not in result["affected_workflows"]
    assert "monthly-reporting" in result["affected_workflows"]
    assert any("report-job" in gap for gap in result["coverage"]["gaps"])
    assert "run-invoice-v2" in {e["assertion_id"] for e in result["evidence"]}
    history = Brain(InMemoryAssessmentTestDouble(bundle)).get_history("invoice-export", SCOPE)
    rows = {a["id"]: a for a in history["assertions"]}
    assert {"run-invoice-legacy", "run-invoice-v2"} <= rows.keys()
    assert rows["run-invoice-v2"]["supersedes"] == ["run-invoice-legacy"]


def test_complete_scoped_verification_yields_no_known_blockers():
    result = assess(scenario("completion", "migration", "clear"))
    assert result["disposition"] == "no_known_blockers"
    assert result["blockers"] == result["conflicts"] == result["coverage"]["gaps"] == []
    assert result["affected_workflows"] == []
    assert {"run-invoice-v2", "clear-report"} <= {e["assertion_id"] for e in result["evidence"]}


def test_revoked_source_cannot_support_clearance_or_be_retrieved():
    bundle = scenario("completion", "migration", "clear")
    sources = [s.model_copy(update={"revoked": True}) if s.id == "source-clear-report" else s
               for s in bundle.sources]
    bundle = bundle.model_copy(update={"sources": sources})
    assert assess(bundle)["disposition"] == "needs_verification"
    brain = Brain(InMemoryAssessmentTestDouble(bundle))
    with pytest.raises(ValueError, match="source unavailable"):
        brain.get_evidence("source-clear-report", "1")
    assert "clear-report" not in {a["id"] for a in brain.get_history("report-job", SCOPE)["assertions"]}


def test_inaccessible_inventory_consumer_has_generic_gap_without_identity_leak():
    bundle = scenario("completion", "migration", "clear")
    secret_id = "secret-payroll-consumer"
    entities = [e.model_copy(update={"id": secret_id, "name": "Hidden payroll", "visibility": "restricted"})
                if e.id == "report-job" else e for e in bundle.entities]
    assertions = [a.model_copy(update={"subject_id": secret_id}) if a.subject_id == "report-job"
                  else a.model_copy(update={"object_id": secret_id}) if a.object_id == "report-job"
                  else a for a in bundle.assertions]
    inventories = [i.model_copy(update={"consumer_ids": [secret_id if c == "report-job" else c for c in i.consumer_ids]})
                   for i in bundle.inventories]
    bundle = bundle.model_copy(update={"entities": entities, "assertions": assertions, "inventories": inventories})
    result = assess(bundle)
    assert result["disposition"] == "needs_verification"
    assert result["coverage"]["declared_consumer_count"] is None
    assert "inventory coverage cannot be established" in result["coverage"]["gaps"]
    assert secret_id not in json.dumps(result)
    assert "Hidden payroll" not in json.dumps(result)


def test_wrong_scope_requests_clarification_and_find_is_explicitly_ambiguous():
    brain = Brain(InMemoryAssessmentTestDouble(scenario()))
    result = brain.assess_retirement("legacy-runner", Scope(environment="staging", region="eu"), NOW, known_at=NOW)
    assert result["disposition"] == "clarification_needed"
    assert result["evidence"] == []
    found = brain.find_entities("runner", kind="Service")
    assert found["ambiguous"]
    assert {c["id"] for c in found["candidates"]} == {"legacy-runner", "runner-v2"}


def test_stale_or_missing_coverage_never_becomes_clear():
    bundle = scenario("completion", "migration", "clear")
    result = Brain(InMemoryAssessmentTestDouble(bundle)).assess_retirement(
        "legacy-runner", SCOPE, NOW, known_at=datetime(2026, 11, 1, 12, tzinfo=timezone.utc))
    assert result["disposition"] == "needs_verification"
    assert any("stale" in gap for gap in result["coverage"]["gaps"])
    assert assess(bundle.model_copy(update={"inventories": []}))["disposition"] == "needs_verification"


def test_cycles_and_traversal_budget_are_reported():
    bundle = scenario()
    original = next(a for a in bundle.assertions if a.id == "run-invoice-legacy")
    reverse = original.model_copy(update={"id": "cycle-reverse", "subject_id": "legacy-runner", "predicate": "DEPENDS_ON", "object_id": "invoice-export"})
    cyclic = bundle.model_copy(update={"assertions": [*bundle.assertions, reverse]})
    assert "dependency cycle requires verification" in assess(cyclic)["coverage"]["gaps"]
    result = assess(bundle, max_depth=1)
    assert result["coverage"]["truncated"]
    assert "dependency traversal budget exhausted" in result["coverage"]["gaps"]
    assert result["disposition"] != "no_known_blockers"


def test_database_failure_propagates_instead_of_producing_an_empty_success():
    class OfflineStore:
        def read_view(self, *args):
            raise ConnectionError("FalkorDB unavailable")
    with pytest.raises(ConnectionError, match="FalkorDB unavailable"):
        Brain(OfflineStore()).assess_retirement("legacy-runner", SCOPE, NOW, known_at=NOW)


def test_assessment_does_not_invoke_extraction(monkeypatch):
    import company_brain.ingestion as ingestion
    def forbidden(*args, **kwargs):
        raise AssertionError("assessment must not extract or call an LLM")
    monkeypatch.setattr(ingestion, "extract_bundle", forbidden)
    assert assess(scenario())["disposition"] == "blocked"


def test_known_time_does_not_use_future_migration_information():
    bundle = scenario("completion", "migration", "clear")
    before = datetime(2026, 10, 17, 10, 30, tzinfo=timezone.utc)
    result = Brain(InMemoryAssessmentTestDouble(bundle)).assess_retirement(
        "legacy-runner", SCOPE, NOW, known_at=before)
    assert result["disposition"] == "blocked"
    assert "run-invoice-v2" not in {e["assertion_id"] for e in result["evidence"]}


def test_evidence_span_must_belong_to_requested_source():
    brain = Brain(InMemoryAssessmentTestDouble(scenario()))
    evidence = brain.get_evidence("source-run-invoice-legacy", "1", "run-invoice-legacy")
    assert evidence["span"]["assertion_id"] == "run-invoice-legacy"
    with pytest.raises(ValueError, match="evidence span unavailable"):
        brain.get_evidence("source-run-invoice-legacy", "1", "owns-invoice")


def test_fresh_unrelated_binding_does_not_prove_legacy_consumer_clear():
    bundle = scenario("completion", "migration")
    old = next(a for a in bundle.assertions if a.id == "run-report-legacy")
    unrelated = old.model_copy(update={"id": "unrelated-fresh-report", "object_id": "runner-v2", "observed_at": NOW})
    bundle = bundle.model_copy(update={"assertions": [a for a in bundle.assertions if a.id != old.id] + [unrelated]})
    result = assess(bundle)
    assert result["disposition"] == "needs_verification"
    assert any("report-job" in gap for gap in result["coverage"]["gaps"])


def test_clearance_for_another_service_cannot_clear_target_inventory():
    bundle = scenario("completion", "migration", "clear")
    assertions = [a.model_copy(update={"target_service_id": "runner-v2", "supersedes": []})
                  if a.id == "clear-report" else a for a in bundle.assertions if a.id != "run-report-legacy"]
    result = assess(bundle.model_copy(update={"assertions": assertions}))
    assert result["disposition"] == "needs_verification"
    assert any("report-job" in gap for gap in result["coverage"]["gaps"])


def test_direct_workflow_dependency_is_a_confirmed_retirement_blocker():
    bundle = scenario("completion", "migration", "clear")
    sample = next(a for a in bundle.assertions if a.id == "requires-billing-invoice")
    text = "Monthly billing requires legacy-runner in production/eu."
    source = next(s for s in bundle.sources if s.key == sample.source_key).model_copy(update={
        "id": "workflow-direct-source", "text": text, "content_hash": sha256(text.encode()).hexdigest()})
    direct = sample.model_copy(update={"id": "workflow-direct-service", "object_id": "legacy-runner",
        "source_id": source.id, "quote": text, "span_start": 0, "span_end": len(text)})
    bundle = bundle.model_copy(update={"sources": [*bundle.sources, source], "assertions": [*bundle.assertions, direct]})
    validate_bundle(bundle)
    result = assess(bundle)
    assert result["disposition"] == "blocked"
    assert any(b["entity_id"] == "monthly-billing" for b in result["blockers"])


def test_missing_migration_status_is_unknown_rather_than_a_confirmed_blocker():
    bundle = scenario()
    stale = datetime(2026, 9, 1, 9, tzinfo=timezone.utc)
    assertions = [a.model_copy(update={"observed_at": stale}) if a.id == "run-invoice-legacy" else a
                  for a in bundle.assertions if a.predicate != "STATUS"]
    result = assess(bundle.model_copy(update={"assertions": assertions}))
    assert result["disposition"] == "needs_verification"
    assert result["blockers"] == []
    assert any("missing migration state" in gap for gap in result["coverage"]["gaps"])
