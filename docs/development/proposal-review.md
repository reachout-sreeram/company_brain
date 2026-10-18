# Explicit proposal review

Extraction never grants authority. Live extraction produces proposals even when source metadata contains an older reviewed fingerprint. Only the local operator CLI can create selected approval records; no MCP write tool exists.

```sh
.venv/bin/company-brain proposals .local/pending.json
.venv/bin/company-brain approve-proposals .local/pending.json --proposal EXACT_ID --proposal ANOTHER_EXACT_ID --actor demo:synthetic-source-validation --demonstration --reviewed-at TIME_WITH_TIMEZONE --note 'Synthetic demonstration: exact selected claims checked against scoped source text; not human acceptance.' --output .local/reviewed.json
.venv/bin/company-brain review-history .local/reviewed.json
.venv/bin/company-brain ingest .local/reviewed.json
```

Select IDs after reading their source/version, scope, exact quote and digest. No approve-all option exists. Output creation refuses overwriting an existing file. `--demonstration` requires a `demo:` actor, and every demonstration remains labeled in its audit record. Ordinary operator identity is a trusted local input, not authenticated identity or proof of human acceptance; production identity and signing remain outside this demo.

Approval retains the immutable proposal and source, adds a new approved assertion and a review event containing actor/kind, timezone-aware review time, input revision, selected proposal IDs, approved IDs, source/version, full-claim digests and review note. It cannot modify claim subject, scope or content during approval, approve a previously selected proposal again, or backdate review before source recording. Existing operator-authored seeded facts and explicitly pre-reviewed deterministic mocks retain their prior behavior.

Ingestion validates approved extracted facts against their retained proposals and review selections as well as source predicate authority. Actual FalkorDB stores immutable review nodes and APPROVES/REVIEWED_FROM edges per revision. Approval time is a knowledge cutoff in the native active-fact/supersession Cypher: a later review cannot retroactively clear an earlier knowledge view. Evidence includes opaque approval_id, explicit approval_kind (operator/demonstration) and approved_at; actor audit is inspected through operator history, not a new public MCP capability.

Verification for the increment: 207 offline tests passed, 14 real-DB tests skipped in the offline command; targeted review suite 11 passed including actual FalkorDB. The review test demonstrates needs_verification before selection and blocked after two scoped synthetic facts are selected; this is a clearly labeled demonstration action, not a real person's approval or framework acceptance.

## Prerequisite time semantics

`RUNS_ON` and `DEPENDS_ON`, and observed `REQUIRES`, retain explicit observed_at and runtime freshness checks. `REQUIRES` alone may instead declare `time_basis: validity`, an observed_at-free business prerequisite whose effective interval is explicit in source text or trusted `requires_valid_from`/`requires_valid_until` metadata. It does not assert runtime usage or runtime clearance, and its validity does not age as a seven-day runtime observation. It must still be known, approved, scoped, nonrevoked and effective at planned_at. A future declared interval may apply to a future planned date only if the source and approval are already known. Missing observation plus missing declared validity is rejected; recorded_at or wallclock now is never silently converted into an observation.

Changing a supersession chain between observed and validity modes is rejected. Validity replacements need a strictly newer explicit validity start; observed replacements still need a newer observation. Pure contractual changes cannot count as runtime migration verification. The two existing raw prerequisite records now have source version 2 and explicitly declared synthetic validity metadata, with unchanged narrative text. Their metadata is an operator declaration, not an extracted runtime observation. Structured four-state fixture facts remain unchanged.
