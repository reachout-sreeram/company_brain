"""Offline contract regressions using retained actual MCP responses. No API calls."""
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from luna_client import finish_schema, validate_final, TOOLS


@pytest.fixture
def retrieved_case():
    root = Path(__file__).parent
    saved = root / "luna-pre-exact-transcript.json"
    if not saved.exists():
        saved = root / "luna-transcript.json"
    raw = json.loads(saved.read_text())
    response = next(c["response"] for c in raw["mcp_calls"] if c["name"] == "assess_retirement")
    assessment = response.get("structuredContent") or json.loads(response["content"][0]["text"])
    answer = copy.deepcopy(raw["final_answer"])
    # Construct only the offline positive-control input from the real MCP response.
    # This is never substituted into a live model transcript or final answer.
    answer["permissions"] = [copy.deepcopy(p) for b in assessment["blockers"] for p in b.get("permissions", [])]
    return answer, assessment, raw["final_answer"]


def test_retained_real_permission_rename_is_rejected(retrieved_case):
    _, assessment, original = retrieved_case
    errors = validate_final(original, assessment, TOOLS)
    assert any("until" in error for error in errors)
    assert original["permissions"][0].get("effective_until")
    assert "until" not in original["permissions"][0]


def test_exact_response_contract_is_accepted(retrieved_case):
    answer, assessment, _ = retrieved_case
    assert validate_final(answer, assessment, TOOLS) == []


@pytest.mark.parametrize("mutation", ["expiry", "disposition", "quote", "gap", "duplicate", "extra_permission_field"])
def test_material_contract_drift_rejected(retrieved_case, mutation):
    answer, assessment, _ = retrieved_case
    if mutation == "expiry": answer["permissions"][0]["until"] = "2099-01-01T00:00:00Z"
    if mutation == "disposition": answer["disposition"] = "no_known_blockers"
    if mutation == "quote": answer["citations"][0]["quote"] = "unsupported quotation"
    if mutation == "gap": answer["coverage"]["gaps"] = []
    if mutation == "duplicate": answer["citations"].append(copy.deepcopy(answer["citations"][0]))
    if mutation == "extra_permission_field": answer["permissions"][0]["effective_until"] = answer["permissions"][0]["until"]
    assert validate_final(answer, assessment, TOOLS)


def test_strict_schema_closes_every_object():
    schema = finish_schema()
    Draft202012Validator.check_schema(schema)
    def visit(value):
        if isinstance(value, dict):
            if value.get("type") == "object":
                assert value["additionalProperties"] is False
                assert set(value["required"]) == set(value["properties"])
            for item in value.values(): visit(item)
        if isinstance(value, list):
            for item in value: visit(item)
    visit(schema)
