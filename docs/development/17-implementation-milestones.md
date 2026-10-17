# Stage 7 implementation milestones

The governing framework is [the ten-stage engineering framework](../planning/10-engineering-framework.md). Stage 1 is concluded, Stage 2 principles remain, and the user selected Stage 3 service retirement readiness. The decision log explicitly allows the hackathon shortcut through formal Stages 4–6 with feasibility checks inside the first increment. The user's subsequent development authorization starts Stage 7; it does not establish Stage 8 acceptance or Stage 9 validation.

## Increment 1: evidence foundation

Implemented strict typed entity, source, assertion and inventory contracts, content hashes and exact source spans, scoped authority, immutable-source merges, explicit supersession, source revocation, deterministic fixtures, and an opt-in OpenRouter extraction adapter. Normal tests use seeded facts or explicitly labeled mock extraction. Trusted operator metadata supplies authority; models cannot grant it.

Verified: 64 evidence/ingestion and mocked-HTTP adapter tests passed. No provider calls were made. A real official FalkorDBLite 0.10.0 / FalkorDB 4.18.3 probe accepted parameterized Cypher and read-only queries. The sandbox blocks socket binding; the isolated runtime probe succeeded with approved execution permissions. Docker is absent.

Scope: foundational validation is executable. Quote equality is not semantic proof of an extracted claim. Operators must review extraction and compare against independent expected facts. Customer validation, broad connector ingestion, database scale and live extraction remain unverified.

## Review and gates

Each increment is committed locally with descriptive stage/test evidence. Existing planning edits are preserved outside these implementation commits. No pushes or history rewrites are authorized. The configured Git author email matches the authenticated `reachout-sreeram` account's public email.

Stage 7 remains in progress until the complete demo and its limits are reviewed. Stage 8 independent evaluation and Stage 9 real-world validation must not be marked complete from synthetic tests. Paid extraction requires a chosen model, spending limit, and secure credential setup before a live run.
