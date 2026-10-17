"""CLI guardrails must fail without connecting or starting paid extraction."""
import sys
from company_brain.cli import main


def test_live_extraction_requires_explicit_opt_in(monkeypatch,capsys):
    monkeypatch.setattr(sys,"argv",["company-brain","extract-ingest","data/raw_demo/manifest.json"])
    assert main()==1
    assert "rejected" in capsys.readouterr().err


def test_missing_input_has_sanitized_cli_failure(monkeypatch,capsys):
    monkeypatch.setattr(sys,"argv",["company-brain","validate","/nonexistent/company-brain-input.json"])
    assert main()==1
    assert "Traceback" not in capsys.readouterr().err


def test_initial_fixture_validates_without_database(monkeypatch,capsys):
    monkeypatch.setattr(sys,"argv",["company-brain","validate","data/synthetic/initial.json"])
    assert main()==0
    assert '"valid": true' in capsys.readouterr().out
