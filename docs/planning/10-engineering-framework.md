# Engineering framework and decision log

This project follows the AI-Native Problem Solving & Product Engineering Framework supplied by the user. Research and proposals do not constitute approval.

## Operating rules

Understand the problem before choosing technology or product features. FalkorDB is an event constraint; it does not establish the user problem. Compare alternatives before committing. Separate facts, assumptions, measurements, and judgments.

AI prepares research, artifacts, experiments, implementation, and evaluation. The human validates assumptions and makes the direction decisions specified below. Ask for each approval only after preparing a concrete artifact to review. Approval of one stage does not imply approval of later stages. Reopen an earlier decision when new evidence materially changes its basis.

The supplied message ends at mandatory principle 3, `Human-`. No missing text has been inferred. The ten complete stages and two complete mandatory principles apply.

## Stage status

| Stage | Required artifact | Human gate | Current status |
| --- | --- | --- | --- |
| 1. Problem understanding | Problem, stakeholders, root causes, alternatives, assumptions | Are we solving the right problem? | Concluded on 15 October 2026 at user instruction; see final brief |
| 2. Success definition | Outcomes, acceptance criteria, failure conditions | What does success mean? | Approved on 17 October 2026: MCP-first context layer, three scripted scenarios with golden verdicts |
| 3. Solution exploration | Multiple solution directions and tradeoffs | Which direction should we pursue? | Shortcut for hackathon: direction fixed by Stage 2 approval |
| 4. Solution validation | Feasibility experiments and comparison evidence | Is this worth building? | Not started |
| 5. Product design | User journey, scope, interaction states | Is this the product we want? | Earlier screen suggestions are provisional |
| 6. Architecture and planning | Justified components, sequence, evaluation plan | Is the design appropriate? | Earlier architecture is unapproved and untested |
| 7. Incremental development | Small working increments and verification | Review significant milestones and changes | Not started |
| 8. Independent evaluation | Evidence separate from implementation claims | Accept, improve, redesign, or reject? | Not started |
| 9. Real-world validation | Realistic task and user evidence | Does it solve the problem? | Not started |
| 10. Optimization and delivery | Fixes, reproducible package, final demo | Ready to present, launch, or deploy? | Not started |

Do not mark Stage 9 complete solely because synthetic cases pass. Record whether validation used real users, realistic synthetic scenarios, or actual operational data. These establish different levels of evidence.

## Decision record

| Decision | Status | Basis |
| --- | --- | --- |
| Apply the user's ten-stage framework | Adopted | Direct user instruction |
| Work within the Company Brain theme | User preference | Initial task |
| Use FalkorDB centrally for the entry | Constraint recorded | Prior event research |
| Select release-to-customer-commitment reconciliation as the problem | Candidate only | User requested broader problem exploration first |
| Build PromiseGraph with the earlier architecture | Not approved | Prior recommendation only |
| Define success for the support-engineer product-behavior scenario | Authorized | User requested Stage 2 for this scenario on 16 October 2026 |
| Adopt Stage 2 success definition | Approved 17 October 2026 | Revised to three scripted scenarios, golden verdicts, five hard checks |
| Deliver as MCP context layer, not a web app | Approved 17 October 2026 | User decision: no chat UI, no answer-generation tokens; Claude Desktop is the client |
| Skip formal Stages 3 to 6 for the hackathon | Approved as deliberate shortcut | Direction: deterministic resolver + FalkorDB + MCP server + Claude skill; revisit after the event |

Record subsequent approvals with the user's actual decision and any conditions. Do not infer approval from silence or elapsed time.

Latest direction: Stage 2 approved on 17 October 2026. The product is an MCP context layer over FalkorDB, evaluated on three scripted scenarios (see [success definition](15-stage-2-success-definition.md)). Stages 3 to 6 are shortcut for the hackathon. Next: Stage 7 incremental development.

Additional research: [Neo4j and GraphRAG implementation patterns](../research/13-neo4j-and-graphrag-implementation-research.md) and [FalkorDB transfer experiments](../research/14-falkordb-pattern-transfer-and-experiments.md) inform later solution exploration. This research does not advance or approve a stage by itself.

| Stage closure | Date | Scope |
| --- | --- | --- |
| Stage 1 concluded at user instruction | 15 October 2026 | Consolidated problem understanding; no approval inferred for PromiseGraph, architecture, or implementation |
| Stage 2 approved | 17 October 2026 | MCP-first delivery; three scenarios; hackathon shortcut through Stage 6 |
