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
    return httpx.Response(200, json={"choices": [{"finish_reason": finish_reason, "message": {"content": json.dumps(payload)}}]})


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
        assert body["response_format"] == {"type": "json_object"}
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
