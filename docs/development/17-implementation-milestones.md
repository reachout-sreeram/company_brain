# Stage 7 implementation milestones

The governing framework is [the ten-stage engineering framework](../planning/10-engineering-framework.md). Stage 1 is concluded, Stage 2 principles remain, and the user selected Stage 3 service retirement readiness. The decision log explicitly allows the hackathon shortcut through formal Stages 4–6 with feasibility checks inside the first increment. The user's subsequent development authorization starts Stage 7; it does not establish Stage 8 acceptance or Stage 9 validation.

## Increment 1: evidence foundation

Implemented strict typed entity, source, assertion and inventory contracts, content hashes and exact source spans, scoped authority, immutable-source merges, explicit supersession, source revocation, deterministic fixtures, and an opt-in OpenRouter extraction adapter. Normal tests use seeded facts or explicitly labeled mock extraction. Trusted operator metadata supplies authority; models cannot grant it.

Verified: 64 evidence/ingestion and mocked-HTTP adapter tests passed. No provider calls were made. A real official FalkorDBLite 0.10.0 / FalkorDB 4.18.3 probe accepted parameterized Cypher and read-only queries. The sandbox blocks socket binding; the isolated runtime probe succeeded with approved execution permissions. Docker is absent.

Scope: foundational validation is executable. Quote equality is not semantic proof of an extracted claim. Operators must review extraction and compare against independent expected facts. Customer validation, broad connector ingestion, database scale and live extraction remain unverified.

## Review and gates

Each increment is committed locally with descriptive stage/test evidence. Existing planning edits are preserved outside these implementation commits. No pushes or history rewrites are authorized. The configured Git author email matches the authenticated `reachout-sreeram` account's public email.

Stage 7 remains in progress until the complete demo and its limits are reviewed. Stage 8 independent evaluation and Stage 9 real-world validation must not be marked complete from synthetic tests. Paid extraction requires a chosen model, spending limit, and secure credential setup before a live run.

## Increment 2: first complete retirement loop

Implemented FalkorDB assertion nodes and evidence edges, bounded graph queries, scoped deterministic resolution, conservative coverage, immutable revisions and compare-and-set publication, operator CLI, four read-only MCP tools, restart persistence, repeatable isolated reset/replay, and separate raw-source mock extraction into the actual graph. Added explicit target-service clearance and newer-observation requirements after review exposed unsafe clearance cases.

Verified: the final full suite at this milestone passed 88 tests (84 offline, 4 opt-in real FalkorDB integration), followed by 3 additional CLI guard tests. Three clean four-state replays produced identical canonical results. The raw-source CLI completed with `extraction_method: mock`. Actual MCP protocol round-trips and an ephemeral read-only database role were exercised. No live OpenRouter call or real Claude session occurred. See [local run instructions](18-local-development.md) and [the measured verification report](../../evals/results/verification.md).

Stage 7 now has a runnable first complete slice for human review. Stage 8 benchmark/independent scenario work and Stage 9 user validation remain open. No formal architecture or product validation is inferred from the hackathon shortcut or these tests.
