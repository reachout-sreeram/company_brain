# Company Brain: user needs and problem discovery

Research date: 15 October 2026. Stage 1 remains open. This document broadens discovery before selecting a problem. PromiseGraph is one candidate, not the default direction.

## What people want

Working hypothesis: people want to get the context needed to complete a task, trust that context, find the responsible person when needed, and continue without unnecessary searching or interruptions. Company Brain is an umbrella for these jobs. It is not a single user need.

The needs differ by role, company size, information practices, and the consequences of a wrong answer. An employee, a delivery manager, an administrator, and an AI agent do not need the same experience.

## Evidence behind the problem map

[GitLab's Glean end-user guide](https://handbook.gitlab.com/handbook/eta/ai/tools/glean/) describes fragmentation across tools, search effort, conflicting information, and onboarding friction. This is a company's published account of its own knowledge-access needs, not an independent product evaluation.

[Atlassian's State of Teams 2025](https://www.atlassian.com/blog/state-of-teams-2025) reports substantial time spent searching for answers in its survey. This supports investigating information friction. A supplier-sponsored survey does not establish frequency or severity for our intended user group.

[Unblocked's Rally case study](https://getunblocked.com/customers/rally/) describes product questions from sales, customer success, and support that required engineering help despite existing documentation. The founder reports a large reduction in interruptions after adoption. This is an attributed customer story published by the vendor, not a controlled experiment.

[GitLab's architecture workflow](https://handbook.gitlab.com/handbook/engineering/architecture/workflow/) explicitly maintains decisions and document status to help later contributors understand architectural choices. This is evidence of an organizational practice for preserving context, not proof that an AI agent should replace that practice.

[Microsoft's discussion of the infinite workday](https://www.microsoft.com/en-us/copilot/blog/2025/06/26/how-microsoft-365-copilot-and-agents-help-tackle-the-infinite-workday/) provides broader context on communication load. It does not establish that another assistant will reduce interruptions.

## Problem map

The following taxonomy is our synthesis. Examples are illustrative, not interview quotations.

| User job | Example question | Cost of failure | Potential existing remedy |
| --- | --- | --- | --- |
| Find the right information | Where is the current integration guide? | Search effort and blocked work | Better navigation or search |
| Determine current approved truth | Which of these conflicting instructions applies? | Rework or wrong customer answers | Source ownership, versioning, explicit approval |
| Find accountability or expertise | Who owns this system, and who knows its history? | Misrouting and repeated interruptions | Maintained service catalog or expert directory |
| Understand a decision | Why did we reject this approach? | Repeated debate and repeated mistakes | Decision records with alternatives and rationale |
| Catch up after absence or handoff | What changed while I was away? | Missed changes and repeated briefings | Contextual summaries and handover records |
| Coordinate across teams | What blocks this project, and who must act? | Delays and incomplete follow-through | Dependency tracking and clear responsibility |
| Assess consequences | What work or customer commitments does this change affect? | Missed downstream effects | Maintained dependency links and review checklists |
| Reuse organizational experience | Have we solved this before, and did it work? | Duplicate work and repeated incidents | Searchable outcomes and linked prior work |

Finding a responsible owner is not the same as finding the most knowledgeable person. A frequent author or highly connected person is not automatically authorized to approve a change.

## Role-specific needs

| Role | Likely high-value job | Validation needed |
| --- | --- | --- |
| New hire or person joining a project | Build enough context to complete a first task | Where they actually get blocked |
| Engineer | Understand constraints, prior incidents, and ownership | Which answers are absent from code and docs |
| Support or customer success | Resolve a product question without engineering escalation | Repeated question types and error consequences |
| Sales | Explain supported behavior and limitations accurately | Which claims require expert confirmation |
| Manager or project lead | Identify blockers, changing decisions, and follow-up responsibility | Whether current issue tracking already suffices |
| Knowledge owner | Find and repair stale or contradictory material | Review burden and acceptable automation |
| IT or security administrator | Preserve access control and know what the system did | Permission and retention requirements |
| AI agent developer | Supply reliable context and permitted tools | Whether infrastructure or a user-facing product is needed |

These are candidate segments. We have not interviewed them or ranked willingness to adopt or pay.

## Root causes to distinguish

Information may exist but be hard to find. It may be findable but outdated. It may never have been written down. A decision may exist without an owner. A team may know the answer but lack authority to act. These require different remedies.

An AI system cannot reliably reconstruct an unrecorded decision. It should identify missing evidence and help route the question. Better documentation, explicit decision status, and clearer accountability can be part of a solution. A graph does not remove those requirements.

Do not describe disagreement, unclear strategy, lack of staff, or missing decision authority as retrieval failures. They may be organizational problems that software can expose but cannot settle.

## Trust and adoption requirements

Users need evidence they can inspect, a clear distinction between approved and proposed information, current ownership, and an honest unknown state. They also need access control and a practical place to review errors. Answers must appear in their workflow with little setup or maintenance burden.

These are proposed design requirements to validate, not proof of an unserved market. Existing products already address many of them.

## Graph fit comes after problem selection

Simple document lookup may need search rather than a graph. Linked decisions, changing ownership, historical outcomes, and transitive dependencies are stronger graph candidates. We must still evaluate them against simpler approaches. The event's database requirement is a constraint on the eventual entry, not evidence of user demand.

## Discovery shortlist

Investigate three problem families next: repeated expert interruptions, conflicting or stale decisions, and missing cross-team impact. They have concrete triggers and observable outcomes. This is a research shortlist, not a product decision.

For each, collect a specific recent task: what triggered it, which tools and people were needed, what delayed the work, what happened when the answer was wrong, and what the current workaround costs. Ask whether an existing tool already solves it. Use the same questions across candidate problems before ranking them.

No participant interviews or private data collection have occurred. No problem direction has been approved.
