# Company Brain research workspace

Research started: 15 October 2026, IST. Direction updated: 17 October 2026, IST.

Current direction: [Stage 3 service retirement readiness](docs/planning/16-stage-3-solution-direction.md), selected by the user on 17 October 2026. Help a platform engineer answer: “Can we retire this service? What still depends on it, what blocks migration, and who owns each blocker?”

The product is an MCP context layer over FalkorDB, with Claude Desktop as the first client. It joins dependency paths to migration work, ownership, decisions, and source evidence. The server resolves facts deterministically; the client LLM explains the assessment and suggests next steps. The demonstration follows three states of one retirement investigation: initial assessment, conflicting completion, and verified migration.

Follow the [engineering framework and decision log](docs/planning/10-engineering-framework.md). Stage 1 is concluded. Stage 2 established the MCP delivery and evidence requirements; its separate support scenarios are superseded by Stage 3. Next is a first working increment with feasibility checks. No application, database integration, evaluation, or deployment has been implemented.

PromiseGraph remains an earlier candidate. No product name has been selected. Future application code and project assets should stay in this directory.

## Document organization

- `docs/research/`: research findings, technology comparisons, and sources.
- `docs/hackathon/`: event rules, sponsor context, and submission strategy.
- `docs/planning/`: user needs, problem selection, and the engineering process.
- `docs/design/`: proposed architecture, data, and evaluation.

## Read in this order

| Document | Purpose |
| --- | --- |
| [Stage 3 service retirement readiness](docs/planning/16-stage-3-solution-direction.md) | Current use case, alternatives, graph model, MCP tools, build sequence, and evaluation |
| [Engineering framework](docs/planning/10-engineering-framework.md) | Stage status, approval gates, and decision log |
| [Stage 1 problem understanding](docs/planning/11-stage-1-problem-understanding.md) | Problem definition, evidence, and limits |
| [Stage 2 success definition](docs/planning/15-stage-2-success-definition.md) | Earlier MCP contract and superseded scenarios; shared principles retained in Stage 3 |
| [Research brief](docs/research/00-research-brief.md) | Historical candidate analysis and evidence boundaries |
| [Company Brain user needs](docs/planning/12-company-brain-user-needs.md) | Broader problem map before choosing a direction |
| [Neo4j and GraphRAG implementations](docs/research/13-neo4j-and-graphrag-implementation-research.md) | Source inspection, retrieval patterns, and reported results |
| [FalkorDB pattern transfer](docs/research/14-falkordb-pattern-transfer-and-experiments.md) | Accuracy and efficiency options with comparison experiments |
| [Rules and expectations](docs/hackathon/01-hackathon-rules.md) | Official requirements and submission checklist |
| [FalkorDB research](docs/research/02-falkordb-research.md) | Database capabilities, limits, and stack choices |
| [Sponsor incentives](docs/hackathon/03-sponsor-incentives.md) | What the event can prove for FalkorDB |
| [Company Brain landscape](docs/research/04-company-brain-landscape.md) | Products, frameworks, close projects, and limitations |
| [Project selection](docs/planning/05-project-selection.md) | Historical candidate alternatives and scores |
| [Architecture](docs/design/06-proposed-architecture.md) | Historical commitment-impact architecture; current plan is in Stage 3 |
| [Evaluation and data](docs/design/07-data-and-evaluation.md) | Historical evaluation plan; current checks are in Stage 3 |
| [Winning strategy](docs/hackathon/08-winning-strategy.md) | Historical submission strategy; current demo is in Stage 3 |
| [Source register](docs/research/09-source-register.md) | Primary references and research limits |

## Key decision

Build one strong Company Brain project. Add another track only when the working implementation supports its claims. Do not divide the event into three unrelated builds.

Use graph traversal to identify affected workflows and connect them to blockers, owners, and decision evidence. Optimize relevant, sufficient context for the client LLM before optimizing tokens or ingestion cost. No mandatory USD 0.10 ingestion cap applies. A missing dependency is not proof of safety. SQL remains a valid alternative; graph benefits, performance, and user savings must be measured.
