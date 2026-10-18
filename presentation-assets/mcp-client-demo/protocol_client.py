"""Actual MCP SDK stdio client. No LLM, credentials, or application edits."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).resolve().parent
REPO = next(parent for parent in HERE.parents if (parent / "pyproject.toml").is_file() and (parent / "src/company_brain").is_dir())
AT = "2026-10-17T12:00:00Z"
SCOPE = {"environment": "production", "region": "eu"}
TOOLS = {"find_entities", "assess_retirement", "get_evidence", "get_history"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report(assessment):
    """Faithful scripted rendering; no generated claims or shutdown approval."""
    lines = ["# Scripted protocol-client result", "",
             "This is deterministic rendering of real MCP responses, not a model conversation.", "",
             f"Disposition: **{assessment['disposition']}**",
             f"Service: {assessment['service_id']}; scope: production/eu; planned: {assessment['planned_at']}.",
             f"Known at: {assessment['known_at']}; revision: `{assessment['graph_revision']}`.",
             "No disposition authorizes shutdown.", ""]
    for key in ("affected_workflows", "dependency_paths", "blockers", "conflicts", "owners", "decisions", "coverage"):
        lines.extend([f"## {key}", "", "```json", json.dumps(assessment[key], indent=2), "```", ""])
    lines.extend(["## Exact evidence citations", ""])
    for item in assessment["evidence"]:
        lines.extend([f"- `{item['assertion_id']}` — `{item['source_id']}@{item['version']}` / span `{item['assertion_id']}`: {json.dumps(item['quote'])}"])
    return "\n".join(lines) + "\n"


async def run(args, socket, backend):
    # Explicit allowlist: no API keys, groups, or inherited DB credentials enter the server.
    env = {key: os.environ[key] for key in ("PATH", "HOME", "TMPDIR", "LANG") if key in os.environ}
    env.update(COMPANY_BRAIN_GRAPH=args.graph, COMPANY_BRAIN_KNOWN_AT=AT,
               FALKORDB_SOCKET=socket, PYTHONPATH=str(REPO / "src"))
    params = StdioServerParameters(command=str(REPO / ".venv/bin/python"),
                                   args=["-m", "company_brain.server"], cwd=str(REPO), env=env)
    transcript = {"client": "official MCP Python SDK protocol client; no model", "transport": "stdio subprocess",
                  "recording": "decoded SDK protocol messages; not a raw JSON-RPC packet capture",
                  "captured_at": datetime.now(timezone.utc).isoformat(), "backend": backend,
                  "sdk_version": importlib.metadata.version("mcp"), "graph": args.graph,
                  "trusted_groups": ["public"], "known_at": AT,
                  "implementation_sha256": {str(p.relative_to(REPO)): digest(p) for p in sorted((REPO / "src/company_brain").glob("*.py"))},
                  "fixture_sha256": {name: digest(REPO / f"data/synthetic/{name}.json") for name in ("initial", "completion")},
                  "events": []}
    def event(method, request, response):
        transcript["events"].append({"method": method, "request": request, "response": response})
    with tempfile.TemporaryFile(mode="w+") as errlog:
        async with stdio_client(params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as client:
                initialized = await client.initialize()
                event("initialize", {"client": "SDK ClientSession"}, initialized.model_dump(mode="json"))
                listed = await client.list_tools()
                assert {tool.name for tool in listed.tools} == TOOLS
                assert all(tool.annotations and tool.annotations.readOnlyHint is True and tool.annotations.destructiveHint is False for tool in listed.tools)
                event("tools/list", {}, listed.model_dump(mode="json"))
                async def call(name, arguments, error=False):
                    result = await client.call_tool(name, arguments)
                    event("tools/call", {"name": name, "arguments": arguments}, result.model_dump(mode="json"))
                    assert bool(result.isError) == error, f"unexpected MCP error status for {name}"
                    if not error:
                        return result.structuredContent or json.loads(result.content[0].text)
                found = await call("find_entities", {"query": "legacy-runner", "kind": "Service"})
                assert any(row["id"] == "legacy-runner" for row in found["candidates"])
                assessment = await call("assess_retirement", {"service_id": "legacy-runner", "scope": SCOPE, "planned_at": AT})
                assert assessment["disposition"] == "blocked"
                assert assessment["coverage"]["gaps"] and assessment["conflicts"]
                assert any(b.get("permissions") for b in assessment["blockers"]), "exception must be retained"
                verified = []
                for citation in assessment["evidence"]:
                    evidence = await call("get_evidence", {"source_id": citation["source_id"], "version": citation["version"], "span_id": citation["assertion_id"]})
                    assert evidence["span"]["quote"] == citation["quote"]
                    source = evidence["source"]["text"]
                    span = evidence["span"]
                    assert source[span["start"]:span["end"]] == span["quote"]
                    verified.append(citation["assertion_id"])
                history = await call("get_history", {"entity_id": "invoice-export", "scope": SCOPE})
                assert history["assertions"]
                await call("assess_retirement", {"service_id": "legacy-runner", "scope": SCOPE, "planned_at": "2026-10-17T12:00:00"}, error=True)
                revisions = set()
                for entry in transcript["events"]:
                    response = entry["response"]
                    if entry["method"] != "tools/call" or response.get("isError"):
                        continue
                    payload = response.get("structuredContent") or json.loads(response["content"][0]["text"])
                    revisions.add(payload["graph_revision"])
                assert revisions == {assessment["graph_revision"]}, "graph changed mid-demo"
    transcript["verification"] = {"status": "passed", "all_four_tools_called": True,
        "exact_evidence_spans_verified": verified, "timezone_missing_rejected": True,
        "disposition_preserved": True, "conflicts_gaps_permissions_retained": True,
        "paid_calls": 0, "desktop_agent_session": False}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "protocol-transcript.json").write_text(json.dumps(transcript, indent=2) + "\n")
    (args.output / "scripted-result.md").write_text(report(assessment))
    print(json.dumps(transcript["verification"], indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE)
    parser.add_argument("--graph", default="company_brain_demo_mcp_client")
    args = parser.parse_args()
    if args.graph != "company_brain_demo_mcp_client":
        parser.error("this isolated demo uses only company_brain_demo_mcp_client")
    # Own new ephemeral real FalkorDB; never reopen/reset the evaluation store.
    from redislite.falkordb_client import FalkorDB
    from company_brain.models import Bundle
    from company_brain.store import FalkorStore
    with tempfile.TemporaryDirectory(prefix="company-brain-mcp-") as temp:
        db = FalkorDB(str(Path(temp) / "demo.rdb"))
        try:
            store = FalkorStore(db, args.graph, writable=True)
            for name in ("initial", "completion"):
                store.ingest(Bundle.model_validate_json((REPO / f"data/synthetic/{name}.json").read_text()))
            module = db.client.execute_command("MODULE", "LIST")
            backend = {"type": "real FalkorDBLite / Redis Unix socket", "ephemeral": True,
                       "synthetic_states": ["initial", "completion"], "modules": module}
            # Redis returns byte strings; decode only non-secret module metadata.
            backend["modules"] = json.loads(json.dumps(module, default=lambda b: b.decode() if isinstance(b, bytes) else str(b)))
            socket = db.client.connection_pool.connection_kwargs["path"]
            asyncio.run(run(args, socket, backend))
        finally:
            db.client.shutdown()


if __name__ == "__main__":
    main()
