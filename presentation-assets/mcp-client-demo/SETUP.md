# Non-Claude MCP protocol demo

This demo uses the installed official MCP Python SDK **1.30.0** as an actual
stdio protocol client. It launches the existing Company Brain MCP server as a
separate process, initializes the session, lists tools, and calls all four tools
against real local FalkorDB. It is a **scripted protocol client**, not a Codex
desktop session, natural-language agent run, or LLM-generated answer.

## Reproduce

From `company-brain/`, using the existing `.venv`:

```sh
COMPANY_BRAIN_KNOWN_AT=2026-10-17T12:00:00Z .venv/bin/python presentation-assets/mcp-client-demo/protocol_client.py
```

The script owns a new temporary FalkorDBLite database and a private Unix socket,
seeds `initial.json` then `completion.json` into the isolated
`company_brain_demo_mcp_client` graph, and shuts down/deletes its temporary database
afterward. No existing graph is reset or modified. The seed is deterministic typed
synthetic data; there is no model extraction in this demo. Only this bootstrap is
an operator write. The MCP subprocess connects to that socket through
`FALKORDB_SOCKET` and uses the application's read-only store. It gets public
access only. No persistent credentials, global client configuration, or paid API
calls are needed. The two output files are replaced on each successful run;
choose `--output /absolute/path` to retain a separate run.

The current machine already has Python 3.13, `mcp`, `falkordb`, and FalkorDBLite.
Other machines need the project's documented dependencies first; this demo does
not install anything. A sandbox must allow the temporary local Redis process and
Unix socket. The verified run required the tool's local execution escalation.
If the socket cannot start, no fallback database or simulated transcript is used.

## What the transcript proves

`protocol-transcript.json` stores decoded responses from `ClientSession.initialize`,
`list_tools`, and `call_tool`; it is not a raw packet capture. It records protocol
negotiation, server instructions, all tool schemas/read-only annotations, calls,
responses, pinned code and fixture SHA-256 hashes, backend module metadata, and
verification checks. The recording contains synthetic source text and no secrets.
The temporary database socket and inherited environment are omitted.

The run finds `legacy-runner`, assesses production/eu at the explicit historical
time, retrieves **every** assessment citation with `get_evidence`, verifies its
quote equals the exact source substring, and gets `invoice-export` history. It
also verifies a timezone-naive retirement time is an MCP tool error. All successful
calls must share one graph revision. `scripted-result.md` faithfully renders the
assessment, including blockers, conflicts, owner and decision records, permission
expiry, coverage gaps and truncation, and exact assertion/source/version/span
citations. A permission exception never rewrites the `blocked` disposition.

Read-only annotations are advisory MCP metadata. Actual store enforcement is the
application's `GRAPH.RO_QUERY` path; this demo does not provision a database ACL
reader or attempt infrastructure mutation. Separate existing integration tests
cover database reader ACL behavior. No production authorization claim is made.

## Existing client inspection and remaining work

No `codex` executable was found on PATH, and no configured Company Brain desktop
session was demonstrated. Cursor, VS Code, and Antigravity are installed, but their
presence does not establish MCP setup or model authorization. Claude was not used.
The fallback selected here is the already installed official SDK.

The evaluation database settings referenced a socket that no longer existed.
Rather than reopen a shared evaluation database during parallel implementation,
this demo uses its own temporary backend.

A subsequent parent message explicitly allocated USD 0.10 for a separate live
Luna/OpenRouter MCP demonstration. That run is now recorded in `LUNA-DEMO.md`.
It chose all four tools through the actual SDK transport and produced a final
answer. The earlier permission-field mismatch is retained unchanged. A subsequent
parent-authorized exact-contract rerun **passed** with a strict final function
schema and no repair. Original failures are all retained. Total actual worker
cost: USD 0.004000040; latest increment USD 0.001729835. The initial scripted protocol
run above still made no paid calls or credential reads; the separate Luna runner
used the existing ignored credential only in process memory. No shared ledger was
modified. Do not reset the task ledger or silently rerun the paid runner.

Code may change while implementation proceeds. Re-run this client after the
implementation is stable and compare recorded hashes before incorporating the
recording into a final presentation. This verifies one seeded blocked/conflict
state, not the entire four-state story, semantic agent quality, speed superiority,
production identity, or stage acceptance.
