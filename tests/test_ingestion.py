"""Independent input-contract checks; no database or external API required."""
from pathlib import Path
import json

import pytest
from pydantic import ValidationError

from company_brain.models import Bundle
from company_brain.ingestion import merge_bundle, validate_bundle

FIXTURES = Path(__file__).resolve().parents[1] / "data" / "synthetic"


def load(name="initial.json"):
    return Bundle.model_validate_json((FIXTURES / name).read_text())


def changed(bundle, collection, index, **updates):
    rows = list(getattr(bundle, collection))
    rows[index] = rows[index].model_copy(update=updates)
    return bundle.model_copy(update={collection: rows})


def test_fixture_sequence_and_duplicate_idempotence():
    initial = load()
    validate_bundle(initial)
    assert merge_bundle(initial, initial).revision == initial.revision
    current = initial
    for filename in ["completion.json", "migration.json", "clear.json"]:
        current = merge_bundle(current, load(filename))
        validate_bundle(current)
    ids = {a.id for a in current.assertions}
    assert {"run-invoice-legacy", "run-invoice-v2", "run-report-legacy", "clear-report"} <= ids
    assert len(current.inventories) == 1
    assert current.inventories[0].complete


@pytest.mark.parametrize("updates", [
    {"subject_id": "unknown-job"},
    {"object_id": "unknown-service"},
    {"source_id": "missing-source"},
    {"source_version": "missing-version"},
    {"quote": "unsupported fabricated evidence"},
    {"span_end": 999999},
])
def test_reject_unsupported_assertion(updates):
    with pytest.raises((ValueError, ValidationError)):
        validate_bundle(changed(load(), "assertions", 0, **updates))


def test_authority_cannot_be_inferred_from_source_text():
    bundle = load()
    source = bundle.sources[0]
    with pytest.raises((ValueError, ValidationError)):
        validate_bundle(changed(bundle, "sources", 0, authority=[]))
    assert source.authority == ["RUNS_ON"]


def test_scope_mismatch_rejected():
    from company_brain.models import Scope
    with pytest.raises((ValueError, ValidationError)):
        validate_bundle(changed(load(), "assertions", 0, scope=Scope(environment="staging", region="eu")))


def test_source_version_is_immutable():
    original = load()
    changed_source = changed(original, "sources", 0, authority=[])
    with pytest.raises((ValueError, ValidationError)):
        merge_bundle(original, changed_source)
    assert original.sources[0].authority == ["RUNS_ON"]


def test_entity_identity_is_immutable():
    original = load()
    with pytest.raises((ValueError, ValidationError)):
        merge_bundle(original, changed(original, "entities", 0, name="Different service"))


def test_assertion_identity_is_immutable():
    original = load()
    with pytest.raises((ValueError, ValidationError)):
        merge_bundle(original, changed(original, "assertions", 0, method="mock"))


def test_source_revocation_preserves_history():
    original = load()
    update = Bundle(sources=[original.sources[0].model_copy(update={"revoked": True})])
    merged = merge_bundle(original, update)
    assert merged.sources[0].revoked
    assert merged.assertions == original.assertions
    assert not original.sources[0].revoked


def test_model_checks_hash_and_timezone():
    data = json.loads((FIXTURES / "initial.json").read_text())
    data["sources"][0]["text"] = "tampered"
    with pytest.raises(ValidationError, match="hash"):
        Bundle.model_validate(data)
    data = json.loads((FIXTURES / "initial.json").read_text())
    data["assertions"][0]["observed_at"] = "2026-10-17T09:00:00"
    with pytest.raises(ValidationError, match="timezone"):
        Bundle.model_validate(data)


def test_supersession_must_reference_known_assertion():
    with pytest.raises((ValueError, ValidationError)):
        validate_bundle(changed(load(), "assertions", 0, supersedes=["missing-assertion"]))


def test_unsupported_proposal_is_retained_without_approval():
    original = load()
    proposal = original.assertions[0].model_copy(update={"status": "proposal"})
    sources = [original.sources[0].model_copy(update={"authority": []}), *original.sources[1:]]
    candidate = original.model_copy(update={"assertions": [proposal, *original.assertions[1:]], "sources": sources})
    validate_bundle(candidate)
    assert candidate.assertions[0].status == "proposal"


def test_duplicate_input_ids_are_rejected():
    original = load()
    for collection in ["entities", "sources", "assertions", "inventories"]:
        rows = list(getattr(original, collection))
        with pytest.raises((ValueError, ValidationError)):
            validate_bundle(original.model_copy(update={collection: rows + [rows[0]]}))


def test_unrelated_assertion_cannot_supersede_dependency():
    original = load()
    index = next(i for i, a in enumerate(original.assertions) if a.id == "owns-invoice")
    with pytest.raises((ValueError, ValidationError)):
        validate_bundle(changed(original, "assertions", index, supersedes=["run-invoice-legacy"]))


def test_failed_merge_keeps_old_revision_readable():
    original = load()
    revision = original.revision
    bad = Bundle(assertions=[original.assertions[0].model_copy(update={"id": "bad-reference", "subject_id": "missing"})])
    with pytest.raises((ValueError, ValidationError)):
        merge_bundle(original, bad)
    assert original.revision == revision
    validate_bundle(original)


def test_clearance_targets_the_explicit_service():
    clear = load("clear.json")
    assert clear.assertions[0].target_service_id == "legacy-runner"
    original = merge_bundle(load(), load("completion.json"))
    original = merge_bundle(original, load("migration.json"))
    validate_bundle(merge_bundle(original, clear))


def test_clearance_without_target_service_is_rejected():
    original = merge_bundle(load(), load("completion.json"))
    original = merge_bundle(original, load("migration.json"))
    clear = load("clear.json")
    with pytest.raises((ValueError, ValidationError)):
        merge_bundle(original, changed(clear, "assertions", 0, target_service_id=None))


def test_non_clearance_cannot_carry_target_service():
    with pytest.raises((ValueError, ValidationError)):
        validate_bundle(changed(load(), "assertions", 0, target_service_id="legacy-runner"))


def test_clearance_cannot_supersede_another_service_dependency():
    original = merge_bundle(load(), load("completion.json"))
    original = merge_bundle(original, load("migration.json"))
    clear = load("clear.json")
    with pytest.raises((ValueError, ValidationError)):
        merge_bundle(original, changed(clear, "assertions", 0, target_service_id="runner-v2"))
