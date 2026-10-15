# Company Brain research workspace

Research date: 15 October 2026, IST.

Current process: follow the [ten-stage engineering framework](docs/planning/10-engineering-framework.md). Stage 1 is exploring [Company Brain user needs](docs/planning/12-company-brain-user-needs.md) before selecting a problem. The earlier [problem brief](docs/planning/11-stage-1-problem-understanding.md), recommendations, and technical plans are provisional candidate material, not approved build decisions.

Recommendation: build a customer-commitment impact agent. Its working name is **PromiseGraph**. When a release plan changes, it finds which customer promises need review, traces the dependencies, identifies current owners, and prepares an evidence-backed response plan.

This is a research and design package. No application, database integration, evaluation, or deployment has been implemented. The name and scope are proposals for discussion. Future application code and project assets should stay in this directory.

## Document organization

- `docs/research/`: research findings, technology comparisons, and sources.
- `docs/hackathon/`: event rules, sponsor context, and submission strategy.
- `docs/planning/`: user needs, problem selection, and the engineering process.
- `docs/design/`: proposed architecture, data, and evaluation.

## Read in this order

| Document | Purpose |
| --- | --- |
| [Research brief](docs/research/00-research-brief.md) | Conclusions, evidence boundaries, and recommendation |
| [Engineering framework](docs/planning/10-engineering-framework.md) | Stage status, approval gates, and decision log |
| [Stage 1 problem understanding](docs/planning/11-stage-1-problem-understanding.md) | Concrete problem hypothesis for human review |
| [Company Brain user needs](docs/planning/12-company-brain-user-needs.md) | Broader problem map before choosing a direction |
| [Neo4j and GraphRAG implementations](docs/research/13-neo4j-and-graphrag-implementation-research.md) | Source inspection, retrieval patterns, and reported results |
| [FalkorDB pattern transfer](docs/research/14-falkordb-pattern-transfer-and-experiments.md) | Accuracy and efficiency options with comparison experiments |
| [Rules and expectations](docs/hackathon/01-hackathon-rules.md) | Official requirements and submission checklist |
| [FalkorDB research](docs/research/02-falkordb-research.md) | Database capabilities, limits, and stack choices |
| [Sponsor incentives](docs/hackathon/03-sponsor-incentives.md) | What the event can prove for FalkorDB |
| [Company Brain landscape](docs/research/04-company-brain-landscape.md) | Products, frameworks, close projects, and limitations |
| [Project selection](docs/planning/05-project-selection.md) | Alternatives, scores, and proposed product |
| [Architecture](docs/design/06-proposed-architecture.md) | Agent loop, graph model, temporal rules, and actions |
| [Evaluation and data](docs/design/07-data-and-evaluation.md) | Synthetic corpus, fair baselines, and release gates |
| [Winning strategy](docs/hackathon/08-winning-strategy.md) | Build sequence, demo, submission, and risks |
| [Source register](docs/research/09-source-register.md) | Primary references and research limits |

## Key decision

Build one strong Company Brain project. Add another track only when the working implementation supports its claims. Do not divide the event into three unrelated builds.

The proposed distinction is a measurable workflow: changed capability date → affected commitment → current accountable owner → reviewed action → recorded outcome. Graph storage, citations, memory, and agents already exist in competing systems. They are necessary components, not sufficient differentiation.
