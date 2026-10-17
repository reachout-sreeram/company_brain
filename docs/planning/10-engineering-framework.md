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
| 2. Success definition | Outcomes, acceptance criteria, failure conditions | What does success mean? | MCP and evidence principles retained; earlier scenarios superseded by the selected Stage 3 retirement workflow |
| 3. Solution exploration | Multiple solution directions and tradeoffs | Which direction should we pursue? | Service retirement readiness selected by the user on 17 October 2026; build approach documented |
| 4. Solution validation | Feasibility experiments and comparison evidence | Is this worth building? | Not validated; feasibility checks planned inside the first increment under the hackathon shortcut |
| 5. Product design | User journey, scope, interaction states | Is this the product we want? | MCP retirement workflow described in Stage 3; no UI or user validation completed |
| 6. Architecture and planning | Justified components, sequence, evaluation plan | Is the design appropriate? | Proposed graph, tool contracts, and build sequence in Stage 3; runtime untested |
| 7. Incremental development | Small working increments and verification | Review significant milestones and changes | In progress; review corrections and verification in implementation milestones |
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
| Prioritize intent interpretation and the right supporting sources | Clarified 17 October 2026 | Direct user instruction; ingestion below USD 0.10 is not mandatory |
| Explain Stage 3 solution choices | Requested 17 October 2026 | Revisit retrieval design within the approved MCP context-layer direction |
| Select service retirement readiness | Approved 17 October 2026 | Direct user instruction to use service retirement and update Stage 3 |
| Replace the three separate support scenarios | Direction selected 17 October 2026 | One retirement workflow with initial blockers, conflicting completion, and verified migration |

Record subsequent approvals with the user's actual decision and any conditions. Do not infer approval from silence or elapsed time.

Latest direction: the user selected [service retirement readiness](16-stage-3-solution-direction.md). Stage 3 now records alternatives, relationship-driven retrieval, evidence rules, MCP tools, a build sequence, and evaluation. It supersedes the earlier audit-export, SSO, and retention demonstrations. The MCP context-layer direction and cost clarification remain. Next is the first working increment with feasibility checks. No implementation or runtime validation has occurred.

Additional research: [Neo4j and GraphRAG implementation patterns](../research/13-neo4j-and-graphrag-implementation-research.md) and [FalkorDB transfer experiments](../research/14-falkordb-pattern-transfer-and-experiments.md) inform later solution exploration. This research does not advance or approve a stage by itself.

| Stage closure | Date | Scope |
| --- | --- | --- |
| Stage 1 concluded at user instruction | 15 October 2026 | Consolidated problem understanding; no approval inferred for PromiseGraph, architecture, or implementation |
| Stage 2 approved | 17 October 2026 | MCP-first delivery; three scenarios; hackathon shortcut through Stage 6 |
| Stage 3 direction selected | 17 October 2026 | Service retirement readiness; detailed plan documented, implementation and validation pending |

Current restriction update (17 October 2026): provider-neutral MCP only; the earlier Claude Desktop/client decision is withdrawn. Never use Claude models or request Claude access. Paid/live API execution awaits model, total spending cap and approved secure credentials. Local Stage 7 corrections are authorized; later framework acceptance and public submission remain pending human review.
