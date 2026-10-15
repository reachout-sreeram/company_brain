# Stage 1: Problem understanding

Status: concluded on 15 October 2026 at the user's instruction. This concludes desk research and problem framing. It does not establish customer validation or approve a product, architecture, or implementation.

## Final problem definition

Employees cannot always establish the current, approved context for a project or system without searching several tools and interrupting colleagues. The required answer may depend on ownership, decision history, dependencies, and supporting evidence that are recorded separately or disagree.

Our problem focus is helping an employee resolve a work question that depends on these connected facts. The desired result is a supported understanding of what applies now, who is responsible, why the current decision exists, and what remains uncertain.

This is narrower than answering every company question. It does not select a customer-commitment product or a particular retrieval architecture.

## User and job

Initial target segment for subsequent validation: people in a software organization who need context across engineering, product, and support. The exact first role and workflow remain to be narrowed against success criteria. These are candidate users, not interviewed participants.

| Stakeholder | Job | Consequence of missing context |
| --- | --- | --- |
| Employee investigating a project or system | Establish current facts, rationale, and responsibility | Blocked work, rework, or an incorrect answer |
| Subject-matter expert | Resolve questions that need specialist judgment | Repeated interruptions and duplicated explanations |
| Project or system owner | Maintain accurate responsibilities and decisions | Misrouting and work based on obsolete assumptions |
| Knowledge administrator | Preserve access, source quality, and corrections | Untrusted or inappropriate information access |
| Hackathon participant | Demonstrate a useful, explainable agent | A technically functional but unfocused entry |

The task starts with a real work question, not with browsing a graph. It ends with sufficient supported context to continue, or a precise account of missing or conflicting evidence and an appropriate escalation when known.

## User needs considered

The [user-needs research](12-company-brain-user-needs.md) identifies eight related jobs: finding information, determining current truth, finding ownership or expertise, understanding decisions, catching up, coordinating work, assessing consequences, and reusing experience.

The central problem selected for further definition is current context and its justification. Catch-up, impact analysis, onboarding, and repeated-question handling are possible workflows that use this capability. They are not all mandatory features.

Ownership and expertise are distinct. The person with the most knowledge is not automatically the accountable owner or authorized approver.

## Root causes

| Cause | How it creates the problem | Evidence status |
| --- | --- | --- |
| Information is distributed across tools | A person must assemble the answer manually | Supported by published company accounts |
| Different records disagree | Finding a passage does not establish which answer applies | Supported by published company accounts |
| Rationale and approval state are separated from the final instruction | Employees cannot distinguish a proposal, rejected option, and current decision | Organizational practices support its importance; frequency unmeasured |
| Relationships and responsibility change | Old ownership or dependencies can mislead later work | Plausible mechanism; prevalence in our target segment unverified |
| Some knowledge remains undocumented | Search and retrieval cannot establish a supported answer | Design limitation; amount of missing knowledge unmeasured |

These causes can coexist. More search, more documents, or a larger model will not necessarily resolve conflicting authority or absent evidence.

## Evidence and its limits

[GitLab's end-user guide](https://handbook.gitlab.com/handbook/eta/ai/tools/glean/) describes fragmented information, conflicting answers, search effort, and onboarding friction. This is a published account from a company using a knowledge platform, not a benchmark of our proposed solution.

The [Rally customer account](https://getunblocked.com/customers/rally/) describes product questions that required engineering help despite existing documentation. It supports repeated expert interruption as a useful workflow to investigate. Its outcomes are vendor-published and were not independently reproduced.

[GitLab's architecture workflow](https://handbook.gitlab.com/handbook/engineering/architecture/workflow/) preserves decision rationale and document status. This supports the importance of explicit decision state. It does not establish that AI should make those decisions.

No user interviews, live competitor trials, prototype evaluations, or measurements of our target users' effort have occurred. The evidence establishes a credible problem category. It does not establish an unserved market, willingness to pay, or superiority over existing products.

## Existing solutions and remaining question

The [market review](../research/04-company-brain-landscape.md) shows that company search, agents, citations, permissions, organizational graphs, and temporal memory already exist. We cannot claim novelty merely by combining them.

The question carried forward is whether a focused workflow can provide more reliable current context, clearer evidence, or less manual effort than a reasonable existing process. Alternatives include better-maintained documentation, decision records, an owner directory, an existing suite agent, hybrid search, and a dedicated graph-backed application.

We have not established that competitors fail at this task. Their absence of a publicly documented feature is not proof of a product gap.

## Technical findings relevant to the problem

The [Neo4j and GraphRAG research](../research/13-neo4j-and-graphrag-implementation-research.md) distinguishes exact graph queries, hybrid search with relationship expansion, broad community summaries, and associative retrieval. The [FalkorDB transfer plan](../research/14-falkordb-pattern-transfer-and-experiments.md) identifies methods worth testing.

Graphs are plausible when the answer depends on connected facts. Simple document lookup may need only search. Correct identity, supported assertions, current validity, and source access remain application responsibilities. A valid traversal over incorrect facts still gives an incorrect result.

FalkorDB is an event constraint. No performance or accuracy advantage has been measured. Choosing an SDK or writing database code belongs to later stages.

## Constraints and boundaries

Work within the Company Brain theme and the [event requirements](../hackathon/01-hackathon-rules.md). Use permitted, reproducible data, with synthetic records for the initial demonstration. The event window limits implementation scope.

Exclude employee surveillance, unsupported legal judgments, unrestricted autonomous company operations, and claims of replacing human decision authority. Do not fabricate unrecorded decisions or treat an absent dependency as proof of no impact.

PromiseGraph remains one candidate workflow. Its earlier scores, screens, graph model, and build plan are provisional historical proposals. They are not the Stage 1 conclusion.

## Assumptions to validate in subsequent stages

We must establish which role experiences this problem often enough, which questions cause meaningful delays or errors, whether sufficient evidence exists, whether an existing process already works, and how much setup or maintenance users will accept.

Measure success on a concrete task. Separate retrieval failure, incorrect extraction, obsolete facts, missing evidence, and organizational disagreement. These require different remedies.

## Stage 1 conclusion and handoff

Conclude Stage 1 with this problem statement:

> Help employees establish the current, supported context for a project or system across scattered company records, including responsibility and decision rationale, while exposing conflicting or missing evidence.

The user requested that Stage 1 be updated and concluded. Record that instruction as authorization to close this research stage, not as approval of every hypothesis or later technical choice.

Stage 2 must define a first user scenario, measurable outcomes, acceptance criteria, and failure conditions. Stage 3 then compares solution directions. No implementation has started.
