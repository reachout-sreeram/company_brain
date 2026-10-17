# Project selection

Status: earlier candidate analysis. The [concluded Stage 1 brief](11-stage-1-problem-understanding.md) governs current problem framing. PromiseGraph and its scores are historical, not selected. The selected use case is [Stage 3 service retirement readiness](16-stage-3-solution-direction.md).

Recommendation: one focused Company Brain submission, provisionally named PromiseGraph. This name has not been checked for trademark or domain availability.

## Candidate comparison

Scores are our judgment, not measured demand or organizer scores. Each dimension is 1–5, with 5 best. “Feasibility” means feasible within the remaining event window. Weighted total = graph fit × 0.30 + distinction × 0.25 + demo clarity × 0.25 + feasibility × 0.20.

| Candidate | Graph fit | Distinction | Demo clarity | Feasibility | Weighted total |
| --- | ---: | ---: | ---: | ---: | ---: |
| General company Q&A | 3 | 1 | 3 | 5 | 2.90 |
| Onboarding and expert finder | 4 | 2 | 4 | 4 | 3.50 |
| Decision change to issue updater | 4 | 1 | 5 | 4 | 3.50 |
| Customer-commitment impact agent | 5 | 3 | 5 | 4 | 4.30 |
| Employee exit knowledge handover | 5 | 3 | 4 | 3 | 3.85 |
| Whole-company autonomous operations | 5 | 2 | 2 | 1 | 2.65 |

The distinction score is deliberately moderate. [Drift](https://github.com/sharique2004/mmm-demo) and [Hopper](https://github.com/vraj00222/hopper) are close. The recommendation rests on a stronger demonstration opportunity, not a claim that nobody has built anything similar.

## The proposed user and job

Initial user: a delivery lead at a small B2B software company. Product, engineering, and customer teams maintain different parts of the plan. The lead must reconcile them after a capability's delivery date changes.

Trigger: an approved release decision moves a capability past a date promised to a customer.

Output: affected commitments, supporting paths, current accountable owners, missing information, and proposed follow-up tasks. Success means the lead can review a complete response plan faster and with fewer missed commitments than manual cross-checking. Time saved remains unmeasured.

Do not start with HR, legal determinations, all company departments, or arbitrary autonomous actions. They add data and governance requirements without improving the first demonstration.

## The demonstration scenario

All entities below are fictional.

| Record | Initial state | Change or implication |
| --- | --- | --- |
| Release R-17 | Export capability due 19 October | Approved change moves it to 23 October |
| Promise C-01 | Cedar Retail needs export on 20 October | Flag for review |
| Promise C-02 | Harbor Labs needs export on 27 October | No date conflict found in this check |
| Promise C-03 | Juniper Ops needs audit bundle on 21 October | Flag through audit bundle → export dependency |
| Promise C-04 | Kestrel uses an existing export version | Explicit exception prevents an incorrect flag |
| Promise C-05 | Lumen needs “migration readiness” on 21 October | Dependency mapping absent; mark unknown |
| Ownership | Previous owner appears in an old planning note | Use the newer approved assignment |

Start with old information, ingest the changed decision, run the impact check, and display the result delta. Then add a verified exception for C-01. Only its result should change. A replay must not duplicate actions.

The key moment is precision under change. Three superficially similar customers should receive different results because their dependencies, dates, and exceptions differ.

## Why a graph is appropriate

The indirect path for C-03 spans a commitment, a derived capability, a prerequisite capability, a release, and its supporting decision. Ownership is another dated relation. Enumerating these paths is a better fit for explicit relationships than hoping all required passages appear in a similarity search.

This is a fit argument, not proof that a graph is always superior. A SQL implementation or an agent with strong structured tools can also solve it. Evaluate the retrieval design honestly.

## MVP contract

The MVP accepts one synthetic source bundle containing docs, ticket records, and chat-style messages. It extracts proposed facts from at least one new text record with an actual model call. It validates and commits those facts, runs bounded FalkorDB queries, and returns evidence-backed findings. It stores reviewed local follow-up actions and their outcomes.

An honest minimal agent chooses among resolve-entity, get-current-plan, trace-commitments, inspect-evidence, and prepare-action tools. Business date rules stay deterministic. Do not call a fixed hardcoded answer an agent.

Required screens are an impact list, an evidence path/source panel, and a reviewable action inbox. A small graph centered on one finding is useful. A whole-company force graph is secondary.

## Optional extensions

After the core passes, add “as known at time T,” an owner handover case, and a new-session follow-up that reads earlier decisions from FalkorDB. Only then consider a second entered track. Multiple agents are optional and add no value unless they have distinct responsibilities that can be tested.

For separate future projects, Track 01 could support dependency-impact investigation, while Track 02 could support incident handoff memory. These are concept options only. Building both now would reduce the quality of the selected entry.

## After the hackathon

Interview five delivery or customer-success leads using a recent real workflow, without collecting private records for the hackathon. Ask how they track promises, how often changes cause reconciliation work, what they missed, and whether existing suite agents already solve it. Test the same task in at least two competing products. A business decision should follow that evidence, not hackathon applause.
