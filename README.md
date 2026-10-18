# Company Brain research workspace

Research date: 15 October 2026, IST. Updated 18 October 2026.

Purpose: Claude can read company records but cannot establish which one is approved, current, or owned by whom. This context layer establishes that from FalkorDB and reports missing or conflicting evidence instead of guessing.

There is no custom UI. A CLI ingests records into FalkorDB. A deterministic resolver decides current truth. An MCP server returns verdicts to Claude Desktop, which is the user interface. FalkorDB Browser shows the graph during the demo.

Current process: follow the [ten-stage engineering framework](docs/planning/10-engineering-framework.md). [Stage 1 is concluded](docs/planning/11-stage-1-problem-understanding.md). [Stage 2 is approved](docs/planning/15-stage-2-success-definition.md) and was extended on 18 October 2026 with the architecture and harnesses, enhancements, and build order. Next step is implementation, starting with build tier P0 (Scenario 1 end to end).

Earlier candidate: **PromiseGraph**, a customer-commitment impact agent with a web UI. It was never selected and is superseded by Stage 2. No product name has been selected.

No application, database integration, evaluation, or deployment has been implemented yet. Future application code and project assets should stay in this directory.

## Document organization

- `docs/research/`: research findings, technology comparisons, and sources.
- `docs/hackathon/`: event rules, sponsor context, and submission strategy.
- `docs/planning/`: user needs, problem selection, and the engineering process.
- `docs/design/`: earlier architecture, data, and evaluation proposals.

## Current plan

| Document | Purpose |
| --- | --- |
| [Stage 2 success definition](docs/planning/15-stage-2-success-definition.md) | The plan: scenarios, architecture and harnesses, tool contract, build order, acceptance criteria, demo script |
| [Engineering framework](docs/planning/10-engineering-framework.md) | Stage status, approval gates, and decision log |
| [Stage 1 problem understanding](docs/planning/11-stage-1-problem-understanding.md) | Final problem definition, evidence, limits, and handoff |
| [Rules and expectations](docs/hackathon/01-hackathon-rules.md) | Official requirements and submission checklist |

## Research and reference

| Document | Purpose |
| --- | --- |
| [Company Brain user needs](docs/planning/12-company-brain-user-needs.md) | Broader problem map before choosing a direction |
| [Company Brain landscape](docs/research/04-company-brain-landscape.md) | Products, frameworks, close projects, and limitations |
| [Sponsor incentives](docs/hackathon/03-sponsor-incentives.md) | What the event can prove for FalkorDB |
| [FalkorDB research](docs/research/02-falkordb-research.md) | Database capabilities, limits, and stack choices |
| [Neo4j and GraphRAG implementations](docs/research/13-neo4j-and-graphrag-implementation-research.md) | Source inspection, retrieval patterns, and reported results |
| [FalkorDB pattern transfer](docs/research/14-falkordb-pattern-transfer-and-experiments.md) | Accuracy and efficiency options with comparison experiments |
| [Source register](docs/research/09-source-register.md) | Primary references and research limits |

## Historical: earlier PromiseGraph candidate

Kept for the record. Each document is marked superseded or partly superseded at the top.

| Document | Still useful for |
| --- | --- |
| [Research brief](docs/research/00-research-brief.md) | Market findings on competitors and close projects |
| [Project selection](docs/planning/05-project-selection.md) | Record of the alternatives considered |
| [Architecture](docs/design/06-proposed-architecture.md) | Assertion model, temporal and authority rules, failure behavior |
| [Evaluation and data](docs/design/07-data-and-evaluation.md) | Synthetic-data and fair-baseline principles |
| [Winning strategy](docs/hackathon/08-winning-strategy.md) | Differentiation claims to avoid, submission package, risks |

## Key decision

Build one strong Company Brain project. Add another track only when the working implementation supports its claims. Do not divide the event into three unrelated builds.

Graph storage, citations, memory, and agents already exist in competing systems. Our distinction is source authority: an approved record outranks a newer unapproved one, ownership is kept separate from expertise and approval, and conflicting or missing evidence is reported rather than resolved silently. Success criteria are approved. Customer validation and implementation have not occurred.
