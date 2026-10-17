# Run the service-retirement slice

This is the Stage 7 implementation of [the selected Stage 3 plan](../planning/16-stage-3-solution-direction.md). FalkorDB is the actual backend. Unit tests use an explicitly named test double; there is no alternative production database. Live company connectors and automatic infrastructure actions are outside this slice.

## Install

From `company-brain/`, with Python 3.13 and `uv`:

```sh
uv venv .venv --python 3.13
uv pip install --python .venv/bin/python -r requirements.lock
uv pip install --python .venv/bin/python --no-build-isolation --no-deps -e .
```

`requirements.lock` pins the exercised macOS development environment, including the official FalkorDB client, official MCP Python SDK 1.x, Pydantic, httpx, pytest and optional FalkorDBLite. FalkorDBLite requires Python >=3.12 and a supported OS/architecture. General TCP deployment can install `.[dev]` without the `lite` extra. Review/update pins deliberately rather than silently switching SDK major versions.

No secrets file is read. A sandbox may require permission to download dependencies and bind the private database socket. Do not treat a skipped integration suite as a passing integration.

## Local persistent FalkorDB

The official FalkorDBLite package embeds a real Redis + FalkorDB module and manages a private Unix socket. On this machine it runs FalkorDB 4.18.3. Use a dedicated path and graph:

```sh
mkdir -p .local
export COMPANY_BRAIN_LITE_PATH="$PWD/.local/retirement.rdb"
export COMPANY_BRAIN_GRAPH=company_brain_demo_retirement
export COMPANY_BRAIN_KNOWN_AT=2026-10-17T12:00:00Z
```

The database persists at that file across CLI invocations; a real shutdown/reopen check is in the integration suite. The private runtime also writes library-managed settings beside it. `.local/` is ignored. Do not remove it when data should persist.

Alternatively, run a compatible FalkorDB server/container with persistent storage, unset `COMPANY_BRAIN_LITE_PATH`, and configure `FALKORDB_HOST` / `FALKORDB_PORT`. TCP connection also supports `FALKORDB_USERNAME`, `FALKORDB_PASSWORD`, and `FALKORDB_SOCKET` for a pre-existing Unix socket. No Docker runtime was available here, so the container route has not been exercised.

The built-in Lite shortcut is local development access, with server reads enforced by `GRAPH.RO_QUERY`. For a separately operated server, provision a distinct MCP reader through your secure database administration process, with only `GRAPH.RO_QUERY`, `INFO` (needed by the official client), and access to this exact graph key. Use separate operator credentials for ingestion. The integration test verifies an ephemeral reader can read but cannot execute graph mutation. No persistent credentials were created during development. Do not expose an unauthenticated local demo server to a network.

## Seed and assess

```sh
.venv/bin/company-brain validate data/synthetic/initial.json
.venv/bin/company-brain ingest data/synthetic/initial.json
.venv/bin/company-brain assess legacy-runner --environment production --region eu --planned-at 2026-10-17T12:00:00Z --known-at 2026-10-17T12:00:00Z
.venv/bin/company-brain ingest data/synthetic/completion.json
.venv/bin/company-brain ingest data/synthetic/migration.json
.venv/bin/company-brain assess legacy-runner --environment production --region eu --planned-at 2026-10-17T12:00:00Z --known-at 2026-10-17T12:00:00Z
.venv/bin/company-brain history invoice-export --environment production --region eu
.venv/bin/company-brain ingest data/synthetic/clear.json
```

Expected progression: initial billing dependency blocks retirement; ticket completion conflicts with newer usage; verified invoice migration removes billing impact but leaves the stale reporting gap; explicit target-scoped reporting verification permits `no_known_blockers` inside the declared inventory only. That status never grants shutdown approval.

Sources, assertions and prior revisions remain in FalkorDB. Source versions and assertion IDs are immutable. Revoking a source deactivates its evidence. Invalid ingestion is rejected before staging; staging/publish failure leaves the published revision readable. Concurrent publication uses a compare-and-set head update. Multiple distributed writers and crash recovery beyond the tested failure injection are not validated.

Ingestion accepts typed JSON exports with explicit facts. Generic catalog/ticket vendor adapters are not implemented. Structured fixtures are labeled `seeded`/`parsed`; they are never presented as LLM extraction. Narrative candidates pass the same validator after extraction. Only exact full-candidate digests in trusted operator `Source.reviewed_claims` metadata can activate extracted/mock claims; changed subject, scope, object, dates or supersession require fresh review. Unreviewed candidates remain proposals; unreviewed supersession is rejected. The raw demo manifest contains explicit reviewed digests for the authored mock candidates. This is an operator trust gate, not automated semantic proof. Exact source spans prove provenance, not semantic entailment; review expected facts independently before trusting new extracted relationships.

## Replay and tests

```sh
.venv/bin/python -m pytest -q
COMPANY_BRAIN_INTEGRATION=1 .venv/bin/python -m pytest tests/test_integration.py -q -s
.venv/bin/python -m company_brain.replay --confirm-graph company_brain_demo_retirement --replays 3
```

The replay explicitly resets only the named demo graph, compares four states to `evals/gold/retirement.json`, checks canonical results across runs, and writes evidence-linked output to `evals/results/replay.json`. Golden files are never loaded into ingestion or exposed by MCP. Assessment time is fixed for reproducibility. Set `COMPANY_BRAIN_KNOWN_AT` as above for stable historical MCP demos; without this explicit setting, MCP calls use current UTC and historical fixtures become stale. Real freshness rules remain unchanged. Reset/reingest old demo graphs after this schema correction.

Reset is available only for the strict `company_brain_demo_*` / `company_brain_test_*` naming convention, operator access and exact confirmation:

```sh
.venv/bin/company-brain reset --confirm-graph company_brain_demo_retirement
```

Never point these commands at user or production graphs. There is no `FLUSHDB` operation.

## MCP client

Run `.venv/bin/company-brain-mcp` as a stdio server. Configure your client with the absolute executable path and the same graph/database environment above. Example provider-neutral MCP stdio server entry (replace `/absolute/path/company-brain`):

```json
{
  "mcpServers": {
    "company-brain": {
      "command": "/absolute/path/company-brain/.venv/bin/company-brain-mcp",
      "env": {
        "COMPANY_BRAIN_LITE_PATH": "/absolute/path/company-brain/.local/retirement.rdb",
        "COMPANY_BRAIN_GRAPH": "company_brain_demo_retirement"
      }
    }
  }
}
```

Tools: `find_entities(query, kind?)`, `assess_retirement(service_id, scope, planned_at)`, `get_evidence(source_id, version, span_id?)`, and `get_history(entity_id, scope)`. `scope` contains `environment` and `region`; `planned_at` needs an explicit timezone. `span_id` is the returned assertion ID.

Ask: “Can we retire legacy-runner in production/eu? Show indirect business dependencies, blockers, owners and evidence.” Clarify ambiguous names. Cite each material finding using its source/version/span; preserve contradictions, stale evidence and coverage gaps. Distinguish suggested next steps from approved decisions. No tool can mutate infrastructure or ingest facts. Access groups are trusted `COMPANY_BRAIN_GROUPS` server configuration, never model arguments.

The official SDK protocol round-trip is tested. No real model/client conversation or intent evaluation has been run. Claude Desktop and Claude models are excluded by the user.

## Separate extraction demo

Use a fresh graph; narrative source versions deliberately differ from seeded fixtures:

```sh
export COMPANY_BRAIN_GRAPH=company_brain_demo_raw
.venv/bin/company-brain extract-ingest data/raw_demo/manifest.json --mock-candidates data/raw_demo/mock_candidates.json
```

This exercises raw source → **explicit deterministic mock extraction** → validation → FalkorDB → the same MCP tools. It makes no API call. Never call its results real model extraction.

The OpenRouter adapter is ready and its HTTP contract/error handling is tested using mocked responses. A future live run requires approval of model, spending limit, and secure process-environment credential setup first. Do not paste a key into chat or commit it. After those decisions, the opt-in command is:

```sh
# OPENROUTER_API_KEY must already be securely available to this process.
.venv/bin/company-brain extract-ingest data/raw_demo/manifest.json --allow-paid-api --model APPROVED_MODEL --max-tokens 2048
```

No default model, retry loop or live call occurs automatically. The token cap bounds output, not total dollar cost; this slice has no enforceable dollar-budget controller. Provider errors are sanitized, redirect following/environment proxies are disabled, and credentials are never logged. Real extraction and its end-to-end fact accuracy remain unverified. Do not upload real company records through this demo.

## Remaining evaluation

Functional replay and adapter tests do not establish customer demand, production reliability, search improvement, or FalkorDB speed superiority. Search-only comparison execution, relationship ablation, independently authored unseen branches, comprehensive authority policy, production identity, and client intent/answer evaluation remain Stage 8 work. The Stage 3 p95 <2 seconds and reset <30 seconds targets require declared hardware/sample/cache settings before acceptance.

Official API references: [FalkorDBLite](https://github.com/FalkorDB/falkordblite), [FalkorDB Python client](https://github.com/FalkorDB/falkordb-py), [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), and [OpenRouter API](https://openrouter.ai/docs/api-reference/chat-completion).

## Supersession renewal semantics

Resolution follows up to 16 explicit `SUPERSEDES` links within one revision, subject and scope. The ancestor and the suppressing successor must be currently eligible for the requested `planned_at` and `known_at`. An intermediate assertion may have expired, because its replacement link remains historical evidence; its approval, source validity, visibility, scope, start date, observation and recording cutoffs must still pass. A revoked or inaccessible chain member cannot be crossed. An expired clearance with no eligible renewal does not grant clearance, and a later renewal cannot retroactively fill a validity gap or become known earlier than its source.

Ingestion rejects chains longer than 16 links before publication rather than accepting facts the bounded query cannot fully resolve. Scope, subject and clearance-target changes remain invalid supersession. Source revocation breaks lineage in the new revision; retained earlier immutable revisions preserve their prior state. Earlier-revision inspection is an operator/store capability, not a new MCP argument or tool. The current projection and assessment use the same Cypher resolver. The complete updated query is in README and `evals/results/rereview-traversal.cypher`.
