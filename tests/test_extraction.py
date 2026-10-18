import json

import httpx
import pytest

from company_brain.extraction import (
    ExtractionError, MockExtractor, OpenRouterConfig, OpenRouterExtractor, RawSource,
)


@pytest.fixture
def source():
    return RawSource(source_id="decision-1", version="1", text="job-export RUNS_ON legacy-runner in production/us-east-1 at 2026-10-17T12:00:00Z")


@pytest.fixture
def candidate(source):
    return {"subject_id": "job-export", "predicate": "RUNS_ON", "object_id": "legacy-runner",
            "scope": {"environment": "production", "region": "us-east-1"},
            "effective_from": "2026-10-17T12:00:00Z", "span_start": 0,
            "span_end": len(source.text), "quote": source.text}


def extractor(handler, **overrides):
    config = {"model": "test/model", "api_key": "SECRET_TEST_KEY", "allow_live": True}
    config.update(overrides)
    return OpenRouterExtractor(OpenRouterConfig(**config), transport=httpx.MockTransport(handler))


def success(payload, finish_reason="stop"):
    return httpx.Response(200, json={"model":"test/model","usage":{"prompt_tokens":120,"completion_tokens":50,"cost":"0.000037"},"choices": [{"finish_reason": finish_reason, "message": {"content": json.dumps(payload)}}]})


def test_openrouter_contract(source, candidate):
    requests = []

    def handler(request):
        requests.append(request)
        assert str(request.url) == "https://openrouter.ai/api/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer SECRET_TEST_KEY"
        body = json.loads(request.content)
        assert body["model"] == "test/model"
        assert body["temperature"] == 0
        assert body["max_tokens"] == 3000
        assert body["response_format"]["type"] == "json_schema"
        assert body["response_format"]["json_schema"]["strict"] is True
        assert body["provider"]["allow_fallbacks"] is False
        assert json.loads(body["messages"][1]["content"]) == source.model_dump()
        assert "untrusted" in body["messages"][0]["content"]
        return success({"assertions": [candidate]})

    result = extractor(handler).extract(source)
    assert result[0].object_id == "legacy-runner"
    assert len(requests) == 1


def test_default_is_off(source):
    def forbidden(request):
        pytest.fail("disabled adapter must not call transport")
    with pytest.raises(ExtractionError, match="disabled"):
        extractor(forbidden, allow_live=False).extract(source)


def test_missing_credentials(source):
    with pytest.raises(ExtractionError, match="configured"):
        extractor(lambda _: pytest.fail("unexpected network"), api_key="").extract(source)


@pytest.mark.parametrize("status", [301, 401, 403, 429, 500, 503])
def test_status_errors_are_redacted(source, status):
    with pytest.raises(ExtractionError) as caught:
        extractor(lambda _: httpx.Response(status, text="SECRET_TEST_KEY private source text")).extract(source)
    assert str(status) in str(caught.value)
    assert "SECRET_TEST_KEY" not in str(caught.value)
    assert "private source" not in str(caught.value)


@pytest.mark.parametrize("error,message", [(httpx.ReadTimeout, "timed out"), (httpx.ConnectError, "network request failed")])
def test_network_errors_are_redacted(source, error, message):
    def handler(request):
        raise error("SECRET_TEST_KEY private source text", request=request)
    with pytest.raises(ExtractionError, match=message) as caught:
        extractor(handler).extract(source)
    assert "SECRET_TEST_KEY" not in str(caught.value)
    assert caught.value.__suppress_context__


@pytest.mark.parametrize("body", [None, {}, {"choices": []}, {"choices": [{}]}, {"choices": [{"finish_reason": "stop", "message": {"content": "not json"}}]}])
def test_malformed_response(source, body):
    with pytest.raises(ExtractionError, match="malformed"):
        extractor(lambda _: httpx.Response(200, json=body)).extract(source)


@pytest.mark.parametrize("finish_reason", ["length", "content_filter", "error", None])
def test_incomplete_output_is_rejected(source, finish_reason):
    with pytest.raises(ExtractionError, match="did not finish"):
        extractor(lambda _: success({"assertions": []}, finish_reason)).extract(source)


def test_provider_error_is_redacted(source):
    with pytest.raises(ExtractionError, match="provider error") as caught:
        extractor(lambda _: httpx.Response(200, json={"error": {"message": "SECRET_TEST_KEY"}})).extract(source)
    assert "SECRET_TEST_KEY" not in str(caught.value)


@pytest.mark.parametrize("change", [
    {"authority": "approved"}, {"status": "active"}, {"predicate": "APPROVE_SHUTDOWN"},
    {"scope": {"environment": "production"}}, {"effective_from": "2026-10-17"},
    {"effective_until": "2026-10-16T00:00:00Z"}, {"object_id": None},
    {"span_start": "0"}, {"span_start": -1}, {"span_end": 0},
    {"object_id": None, "value": True},
    {"predicate": "STATUS", "object_id": None, "value": "approved"},
    {"predicate": "VERIFIED_CLEAR", "object_id": None, "value": "complete"},
    {"predicate": "VERIFIED_CLEAR", "object_id": None, "value": "verified"},
    {"target_service_id": "legacy-runner"},
])
def test_invalid_candidates_rejected(source, candidate, change):
    with pytest.raises(ExtractionError, match="invalid candidate"):
        extractor(lambda _: success({"assertions": [{**candidate, **change}]})).extract(source)


def test_fabricated_quote_rejected(source, candidate):
    with pytest.raises(ExtractionError, match="quote"):
        extractor(lambda _: success({"assertions": [{**candidate, "quote": "invented"}]})).extract(source)


def test_clearance_is_bound_to_target(source, candidate):
    payload = {**candidate, "predicate": "VERIFIED_CLEAR", "object_id": None,
               "value": "verified", "target_service_id": "legacy-runner"}
    result = extractor(lambda _: success({"assertions": [payload]})).extract(source)
    assert result[0].target_service_id == "legacy-runner"


def test_no_partial_candidates_after_bad_span(source, candidate):
    with pytest.raises(ExtractionError):
        extractor(lambda _: success({"assertions": [candidate, {**candidate, "span_end": len(source.text) + 1}]})).extract(source)


def test_mock_is_explicit_and_checks_versions(source, candidate):
    mock = MockExtractor({("decision-1", "1"): [candidate]})
    assert mock.method == "mock"
    assert mock.extract(source)[0].predicate == "RUNS_ON"
    with pytest.raises(ExtractionError, match="No deterministic"):
        mock.extract(source.model_copy(update={"version": "2"}))


def test_env_is_opt_in_and_config_hides_key(monkeypatch):
    monkeypatch.setenv("OPENROUTER_MODEL", "test/model")
    monkeypatch.setenv("OPENROUTER_API_KEY", "SECRET_TEST_KEY")
    monkeypatch.delenv("COMPANY_BRAIN_ALLOW_OPENROUTER", raising=False)
    config = OpenRouterConfig.from_env()
    assert config.allow_live is False
    assert "SECRET_TEST_KEY" not in repr(config)
    assert "SECRET_TEST_KEY" not in config.model_dump_json()
    monkeypatch.setenv("COMPANY_BRAIN_ALLOW_OPENROUTER", "1")
    assert OpenRouterConfig.from_env().allow_live is True


# --- Lean model output: the model supplies semantics; code supplies scope, spans and defaults.

CATALOG = [{"id": "invoice-export", "kind": "Job", "name": "Invoice export"},
           {"id": "legacy-runner", "kind": "Service", "name": "Legacy runner"},
           {"id": "invoice-migration", "kind": "MigrationTask", "name": "Invoice runner migration"},
           {"id": "temporary-exception", "kind": "Decision", "name": "Temporary invoice exception"}]


def contextual(text):
    return RawSource(source_id="rec", version="1", text=text, scope={"environment": "production", "region": "eu"},
                     recorded_at="2026-10-17T10:00:00+00:00", entities=CATALOG)


def lean(**fields):
    base = {"subject_id": "invoice-export", "predicate": "RUNS_ON", "object_id": "legacy-runner", "value": None,
            "target_service_id": None, "quote": "invoice-export runs on legacy-runner", "effective_from": None,
            "effective_until": None, "observed_at": None}
    return {**base, **fields}


def test_lean_output_is_completed_from_trusted_context():
    source = contextual("Configuration observation 2026-10-17T09:00:00Z: invoice-export runs on legacy-runner in production/eu.")
    result = extractor(lambda _: success({"assertions": [lean(observed_at="2026-10-17T09:00:00Z")]})).extract(source)[0]
    assert result.scope == {"environment": "production", "region": "eu"}
    assert source.text[result.span_start:result.span_end] == result.quote
    assert result.observed_at == "2026-10-17T09:00:00Z" and result.effective_from == "2026-10-17T09:00:00Z"


def test_lean_undated_dependency_does_not_turn_recording_into_observation():
    source = contextual("invoice-export runs on legacy-runner in production/eu.")
    with pytest.raises(ExtractionError,match="explicit observation"):
        extractor(lambda _: success({"assertions": [lean()]})).extract(source)


@pytest.mark.parametrize("change,message", [
    ({"quote": "invoice-export runs on new-runner"}, "quote"),
    ({"object_id": "made-up-service"}, "catalog"),
])
def test_lean_rejections(change, message):
    source = contextual("invoice-export runs on legacy-runner in production/eu.")
    with pytest.raises(ExtractionError, match=message):
        extractor(lambda _: success({"assertions": [lean(observed_at="2026-10-17T09:00:00Z",**change)]})).extract(source)


def test_lean_ambiguous_quote_rejected():
    source = contextual("invoice-export runs on legacy-runner. Again: invoice-export runs on legacy-runner.")
    with pytest.raises(ExtractionError, match="ambiguous"):
        extractor(lambda _: success({"assertions": [lean()]})).extract(source)


def test_lean_requires_trusted_context():
    source = RawSource(source_id="rec", version="1", text="invoice-export runs on legacy-runner.")
    with pytest.raises(ExtractionError, match="trusted source scope"):
        extractor(lambda _: success({"assertions": [lean()]})).extract(source)


def test_prompt_carries_catalog_metadata_and_example():
    seen = {}
    def handler(request):
        seen.update(json.loads(request.content)); return success({"assertions": []})
    extractor(handler).extract(contextual("Nothing here."))
    system, user = seen["messages"][0]["content"], json.loads(seen["messages"][1]["content"])
    assert "PERMITS_USE" in system and "untrusted" in system and "Example" in system
    assert user["scope"] == {"environment": "production", "region": "eu"}
    assert {e["id"] for e in user["entities"]} >= {"invoice-export", "legacy-runner"}


def test_ideal_lean_outputs_satisfy_narrative_gold():
    from pathlib import Path
    from company_brain.evaluation import score_narrative
    gold = {c["source_key"]: c["expected"] for c in json.loads(Path("evals/gold/narrative.json").read_text())["cases"]}
    permit = contextual("Decision record for temporary-exception in production/eu: from 2026-10-01T00:00:00Z until 2026-11-01T00:00:00Z, invoice-export may continue using its current runner while network approval is outstanding.")
    out = lean(subject_id="temporary-exception", predicate="PERMITS_USE", object_id="invoice-export",
               quote="from 2026-10-01T00:00:00Z until 2026-11-01T00:00:00Z, invoice-export may continue using its current runner",
               effective_from="2026-10-01T00:00:00Z", effective_until="2026-11-01T00:00:00Z")
    got = extractor(lambda _: success({"assertions": [out]})).extract(permit)
    assert score_narrative(got, gold["source-permits-invoice@1"])["true_positive"] == 1
    claim = contextual("Ticket invoice-migration claims complete in production/eu as of 2026-10-16T12:00:00Z. This ticket is not a runtime verification.")
    out = lean(subject_id="invoice-migration", predicate="STATUS", object_id=None, value="complete",
               quote="invoice-migration claims complete in production/eu as of 2026-10-16T12:00:00Z", effective_from="2026-10-16T12:00:00Z")
    got = extractor(lambda _: success({"assertions": [out]})).extract(claim)
    assert score_narrative(got, gold["source-status-migration-claimed-complete@1"])["true_positive"] == 1
