# Verified run — 2026-10-18

This page describes the initial scripted protocol run. The later paid natural-
language run, retained failures and separate costs are documented in
`LUNA-DEMO.md`; the latest single authorized exact-contract rerun passed with no
repair, and the earlier failed answer remains unchanged in the archives.

- Client: official MCP Python SDK 1.30.0, separate stdio server process.
- Negotiated protocol: 2025-11-25; server: Company Brain.
- Backend: actual FalkorDB module 4.18.3, temporary local FalkorDBLite database.
- State: existing synthetic `initial` plus `completion`, public caller only.
- Graph: `company_brain_demo_mcp_client`.
- Revision: `17d8e0c78e34cf797b2dc15c161e49f6c4b3da2b771f3982c642eb5dd8f7a0dd`.
- 19 decoded protocol events: initialize, tools/list, 17 tools/call requests.
- All four read-only tools exercised successfully. Every successful response
  returned the same graph revision. A timezone-naive assessment was rejected.
- 13 evidence citations fetched through MCP; every quote matched its exact source
  substring at the returned offsets.
- Disposition: `blocked`; two conflicts; five coverage gaps; truncation false.
- Exception retained: `permits-invoice`, decision `temporary-exception`, expires
  `2026-11-01T00:00:00+00:00`. It does not waive the blocked disposition.
- Paid calls: zero. No credentials read or created. No Claude use.
- Scripted rendering, not a natural-language model answer or desktop session.

Run command, from `company-brain/`:

```sh
COMPANY_BRAIN_KNOWN_AT=2026-10-17T12:00:00Z .venv/bin/python presentation-assets/mcp-client-demo/protocol_client.py
```

The successful run required escalation to permit the local database process and
Unix socket. The original sandbox-only attempt could not start Redis. Two client
transcript-bookkeeping errors were corrected before the successful run; these
attempts made no paid calls and touched only their own temporary databases. The
recorded transcript is the final successful run. A basic credential-marker scan
of the output found no API-key/Bearer marker. The client intentionally passes only
an allowlisted environment and never reads `.env.local`.

Parent budget coordination was unavailable: sending to the supplied source
thread ID returned `thread not found`. The paid Luna agent demo was deferred,
without attempting a request. Implementation task was notified successfully.
An optional notification to the separate judges-drafts task was denied by
automatic approval review because that destination lacked explicit messaging
authorization; no retry or workaround was attempted.

Artifacts are confined to this directory; application, assessment, search,
evaluation, README and shared configuration were not edited by this demo worker.
Parallel implementation edits remain owned by their implementation task. No
branch/stage/push/publication/acceptance action was taken.
