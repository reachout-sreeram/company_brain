# Stage 2: Success definition

Prepared: 16 October 2026, IST. Status: proposed for human review. The user authorized defining criteria for the support-engineer scenario. Thresholds below are engineering targets for approval, not measured results, customer requirements, or organizer judging rules.

## Scenario and desired outcome

A support engineer receives a question about product behavior. The answer depends on current information distributed across tickets, documents, and conversations. The engineer needs the applicable answer, its documented rationale, and the current responsible owner before replying or escalating.

Success means the engineer can reach a correct, reviewable answer or a justified escalation with less manual investigation. The system must distinguish supported facts from missing or conflicting evidence.

The [Stage 1 problem definition](11-stage-1-problem-understanding.md) governs the scope. This specification narrows the first workflow without choosing the SDK, retrieval method, architecture, or product name.

## Task boundary

Input: a product-behavior question, relevant product/version/customer scope where provided, authenticated user context, and a declared source-data revision.

Output: an internal answer brief that the support engineer can inspect and use. The task ends when the engineer has sufficient supported context to answer or knows what must be clarified and where to escalate if ownership is established.

The first version does not send customer messages, change product settings, approve exceptions, or implement a fix. Generated customer wording, if later added, must not imply delivery or approval of an action.

Use a fictional software company and three source forms: documents, structured tickets, and chat-style messages. Live connectors, all-company search, broad executive summaries, and multi-agent coordination are not success requirements for this scenario.

## Answer contract

| Required element | Acceptance condition |
| --- | --- |
| Disposition | Clearly identifies answered, partially answered, clarification needed, conflicting evidence, or insufficient evidence |
| Current behavior | States what applies to the requested scope; does not turn a proposal into shipped behavior |
| Rationale | Explains the documented reason, or explicitly states that no supported reason was found |
| Responsibility | Names the current accountable person/team when supported; separates owner, expert, and approver |
| Evidence | Links each material factual claim to an accessible source version and supporting passage or structured record |
| Currency and scope | Identifies relevant version/date constraints and data revision; does not imply live access to unsynced systems |
| Next step | Gives the supported next step, required clarification, or escalation destination when known |

Use concise prose with expandable evidence or an equivalent inspectable presentation. This is a content requirement, not a selected UI design. A graph visualization is optional.

An illustrative synthetic case: “Can tenant-level audit export be enabled for Product v2, and who owns it?” An old document says no. A later approved decision permits it only after an isolation review. A newer chat proposes removing that review but has not been approved. Ownership has also changed. A successful answer preserves the approved condition and identifies the current owner with evidence. It does not recommend enabling the feature unconditionally.

## Unknown, ambiguous, and conflicting information

A complete answer is required when accessible evidence supports it. Blanket refusal is not acceptable on answerable tasks.

When only part of the answer is known, return that part and identify the gap. Missing rationale does not require hiding a supported behavior or owner. When product scope is ambiguous and changes the answer, request the specific missing detail instead of guessing.

Conflicting authoritative records must remain visible as a conflict. Do not choose a source solely because it has the latest timestamp. Approval, applicability, validity, and explicit supersession determine which statements can establish current behavior.

Evidence that a source mentions an entity is not evidence of ownership or causation. An absent relation is not proof that a restriction or dependency does not exist.

## Evaluation corpus and independent answer key

Prepare 40 authored task cases: 20 development cases and 20 held-out cases. The held-out set contains 15 answerable cases, two missing-evidence cases, two unresolved-conflict cases, and one scope-ambiguity case. Development cases should cover the same categories without duplicating the exact questions or relation patterns.

Among the 15 answerable holdouts, include at least eight requiring evidence from multiple source records, four requiring stale or superseded information to be rejected, and ten with a gold-standard current owner. These groups may overlap. Include ordinary lookup cases to detect regressions from unnecessary graph expansion.

Each answer key specifies required facts, acceptable partial answers, source spans, applicable version, current owner where known, forbidden conclusions, and expected disposition. Review the source corpus and answer key manually before tuning prompts. Keep the key out of the agent's retrieval scope.

Change names, wording, source layout, and some relationship shapes in the holdout. If a held-out case is used to tune the system, report it as development evidence and create a replacement holdout. Do not silently reuse an exposed test set as unseen evaluation.

## Proposed product acceptance thresholds

| Measure | Proposed threshold | Scoring rule |
| --- | --- | --- |
| Complete supported answers | At least 14/15 answerable held-out cases | Every required element must be correct and supported; valid explicit gaps follow the gold contract |
| Handling uncertainty | All 5 non-answerable held-out cases | Correct missing-evidence, conflict, or clarification disposition, with any supported partial answer retained |
| Current owner | At least 90% of applicable held-out cases; at least 10 cases | Wrong, former, or invented owners fail; omission fails when the owner is accessible |
| Citation coverage | 100% of material factual claims cited | Each claim must have a resolvable evidence reference |
| Citation support | At least 95% of material factual claims supported | A human checks whether the cited content actually supports the claim and scope |
| Materially harmful factual errors | Zero in the acceptance suite | No unsupported enablement instruction, proposal described as approved/shipped, or invented owner/approver |
| Response latency | p95 at or below 20 seconds | Full request to usable brief, including model calls; controlled run protocol below |
| Model-call cost | Mean at or below USD 0.05 per task | All retrieval-planning, generation, and retry calls included; actual usage and pricing recorded at evaluation time |

Citation coverage and citation support are different. Attaching a link is not enough. Unsupported critical claims fail the gate even if the overall support percentage passes. Answer completion already includes scope, rationale, owner, and currency where required, so strong prose cannot compensate for a missing essential fact.

For owner accuracy, require at least `ceil(0.90 × applicable_cases)` correct. Report all raw numerators and denominators. If a metric has no applicable cases, mark it unevaluated rather than passing it.

Latency and cost targets are provisional interaction and budget choices. Revisit them during feasibility validation if evidence justifies a different tradeoff. Do not weaken correctness or access controls to reach them. Log ingestion, indexing, and hosting costs separately so a cheap query does not hide expensive preparation.

## Hard failure checks

Create 12 separate adversarial cases: four source-access cases, three source-instruction injection cases, three identity/scope confusion cases, and two dependency failure cases. All must pass. Zero failures in this finite suite is a release condition, not proof of universal security.

Access checks cover answers, evidence paths, intermediate model context, caches, and displayed metadata. Private synthetic details must not cross their defined access boundary. Source instructions must not expand privileges, trigger mutations, or replace task instructions. Similar names must not cause incorrect identity merging. Database unavailability must produce an explicit failure rather than a hidden canned answer. Model unavailability must not produce a fabricated explanation.

## Change and persistence checks

Run six stateful sequences, all of which must pass:

1. An approved behavior update changes the next answer after ingestion completes.
2. Ownership reassignment replaces the current owner while preserving valid history.
3. A newer unapproved suggestion does not override approved behavior.
4. Source deletion or access revocation removes dependent evidence from subsequent answers and invalidates affected caches.
5. Replaying an unchanged source version does not create duplicate facts or inconsistent answers.
6. A restart preserves committed facts and source revision; database-dependent questions still query FalkorDB.

For the initial test, support explicit ingestion followed by query. Do not claim real-time synchronization. An old answer must not be presented as current during an incomplete update; either use a clearly identified consistent revision or report that the update is pending.

## Fair comparison and graph-value criterion

Required automated baseline: a competent hybrid-search agent that can search iteratively and rerank passages. Use the same answer model, source versions, access rules, task wording, generation budget, and retrieval-call cap. Include extraction, indexing, and query costs for both methods. Keyword-only search is an optional diagnostic baseline, not the sole competitor.

The graph candidate must meet the product acceptance thresholds. In addition, demonstrate at least one of the following against the hybrid baseline:

- At least two additional successful cases out of the same 20 held-out tasks, with no new materially harmful error.
- At least 30% lower mean per-task model token use, including planning and retries, with no reduction in total successful cases or multi-source-case successes.

Both routes must preserve the hard checks. Report regressions case by case. These are small-sample engineering comparisons, not statistical proof of market-wide superiority. Latency, ingestion cost, and maintenance effort must accompany any token-saving claim.

An ablation with the same extraction and generation but graph expansion disabled helps identify the value of relationships. Do not attribute the entire system improvement to FalkorDB when the model, source quality, or tool budget also changed. Comparing Neo4j and FalkorDB engine speed is not required for product success.

If the baseline already solves the task adequately and the graph adds no measured benefit, investigate a different relationship-dependent scenario or reject the extra complexity. Do not manufacture graph necessity by deliberately weakening the baseline.

## Usability and real-world validation

Proposed later user-validation target: at least three people familiar with support work, each completing six tasks split across assisted and manual investigation. Counterbalance task allocation with matched difficulty so nobody repeats a task after learning its answer.

Measure time to a correct answer or justified escalation, not time to first generated text. Target at least 30% lower median completion time without lower task correctness. Also observe whether participants can inspect sources, distinguish current decisions from proposals, and recognize when escalation is needed.

This study belongs to later evaluation and real-world validation. If only synthetic task checks or developer walkthroughs occur, label them accordingly. Do not claim validated effort savings or completed Stage 9 without the relevant user evidence.

## Runtime measurement protocol

For the automated holdout, record task-level verdicts from one predeclared primary run and repeat each task three times to expose model variability. Report every repeat and any harmful or access failure; do not select the best output. Hard failure checks apply across all observed runs.

For latency, collect 50 timed requests after a declared warm-up, distributed across task types with result caching disabled. Report p50, p95, failures, corpus size, hardware, model, engine/client versions, and concurrency. Record cold-start latency separately. Report cache-enabled runs separately if added. Timeouts count as failed responses, not excluded samples.

Manual answer review is the authority for acceptance. Automated or model-based grading may assist, but it must not be the only judge of evidence, current ownership, or access behavior.

## What an excellent result looks like

The engineer receives a short correct answer, can inspect why it is current, sees the responsible owner, and knows the next step. A changed approved record changes the answer. A conflicting or absent record produces an honest gap. The same workload is demonstrably better served than a competent baseline on correctness or model-token efficiency.

The demo must show actual ingestion and FalkorDB-backed retrieval on at least one case that crosses source records. A prewritten answer, decorative graph, or hardcoded owner list does not satisfy the runtime requirement.

## Approval and next stage

Review the scenario boundary, answer contract, thresholds, mandatory failure checks, and baseline requirement. Approval establishes what success means; it does not select the implementation.

After approval, Stage 3 compares structured graph tools, hybrid search with graph expansion, and temporal-memory approaches against this specification. The [earlier commitment-focused evaluation notes](../design/07-data-and-evaluation.md) remain historical candidate material and do not override this scenario's criteria.
