# Data and evaluation plan

Status: historical candidate plan for the earlier commitment-impact idea. The [Stage 2 support-engineer success definition](../planning/15-stage-2-success-definition.md) is the current proposed evaluation contract. No dataset has been generated or ingested. No scores have been measured.

## Data choice

Use an original synthetic company corpus. It gives us lawful, reproducible records and known answers. It also lets us test changes that public data rarely captures together: a promise, a release dependency, a reassignment, and an approved exception.

Do not use real internal messages, employee data, contracts, or customer records. Do not imply this corpus represents a collected company dataset. The [event rules](https://www.wemakedevs.org/hackathons/falkordb/rules) restrict acceptable information. Synthetic data is the clearest fit for this demo.

Suggested corpus: 12 fictional people, four teams, eight customers, ten capabilities, three releases, 16 commitments, and 40–60 source records. Include Markdown decisions, ticket JSON, and chat-style JSONL. These are planning sizes, not existing files or benchmark scale.

Use no real contract language to infer legal obligations. The product checks fictional operational promises and dates.

## Separate the source corpus from the answer key

Each source needs origin `synthetic`, generation method, authoring date, a stable ID, version, and the scenario it belongs to. Document that the project team created it. Source records must be readable without a special SaaS account.

Create a separate human-reviewed answer key containing expected entities, relations, active facts, evidence spans, and output classifications. The agent must not read the answer key. Do not generate both source truth and evaluation verdicts from one unchecked model output.

Initial structured seed facts can make setup deterministic. Separately evaluate extraction from natural text, including a newly entered source. Show which path produced each fact.

## Required scenario coverage

| Case | Expected behavior |
| --- | --- |
| Direct release dependency | Find the impacted promise |
| Two- or three-hop capability chain | Find the indirect impact and show each edge |
| Similar wording, different capability | Avoid a false match |
| Release arrives before promised date | No date conflict found in this check |
| Scoped approved exception | Exclude only the matching scope |
| Missing dependency record | Return unknown, not safe |
| Old and new owner | Choose the approved current owner |
| Conflicting approved dates | Request review; do not choose silently |
| Casual suggestion after official decision | Preserve approved state |
| Duplicate source replay | No duplicate facts or actions |
| Late-arriving source | Separate effective date from arrival date |
| Removed evidence | Invalidate dependent conclusion or flag evidence loss |
| Dependency cycle | Terminate with an explained limit |
| Hidden supporting source | No restricted detail reaches model or user |
| Malicious source instruction | No tool misuse or unauthorized mutation |
| Plan changes after draft creation | Mark draft obsolete before approval |
| Database outage | Explicit failure with no canned result |

“No date conflict found” is narrower than “customer is safe.” It only concerns the loaded, accessible graph, specified dependency rules, and tested date constraints.

## Baselines

Compare several systems on the same questions and corpus:

1. Keyword retrieval with a fixed chunking method and the same answer model.
2. Vector retrieval plus reranking with the same answer model.
3. A competent hybrid retrieval agent that can search iteratively within a fixed budget.
4. Proposed FalkorDB path retrieval plus the same answer model.

Also run a deterministic oracle over the hand-checked truth table to verify date classification. This tests the graph implementation independently of generated prose.

If time is short, prioritize vector-plus-reranking and the oracle. Clearly label omitted baselines. Do not compare a multi-tool graph agent against a one-shot vector baseline and attribute the whole gain to the database.

Controls: same source versions, access rules, generation model, temperature where supported, answer token cap, question wording, and maximum evidence budget. Record retrieval and planning calls separately. Vector indexing and graph extraction both have costs; include them.

Ablation: keep extraction and generation constant, then remove graph expansion. This isolates traversal's contribution better than a comparison that changes the entire stack. It still does not establish that FalkorDB outperforms another graph engine.

## Question set

Create 36 scored cases before optimizing prompts: 18 development cases and 18 held-out cases. Balance direct, indirect, stale, ambiguous, negative, and action-state scenarios. Review every expected answer manually. Keep at least six permission or injection checks separate as pass/fail adversarial cases.

Example questions:

| Question | Required evidence |
| --- | --- |
| Which promises need review after R-17 moves? | Commitment, valid dependency path, current release date |
| Why is Juniper affected when its ticket does not mention export? | Audit-bundle prerequisite path |
| Who is responsible now? | Current approved ownership assertion |
| Why is Kestrel excluded? | Scoped exception and supporting source |
| Can we conclude Lumen is unaffected? | Coverage check; expected abstention |
| What changed since the last run? | Stored run and material fact revision |
| Is this draft still valid? | Current graph revision and evidence checks |

Held-out cases should change names, topology, dates, and source wording. Renaming the same demonstration is a weak holdout. Include at least one unseen dependency shape.

## Metrics

| Metric | Definition |
| --- | --- |
| Impact precision | Correct flagged commitments / all flagged commitments |
| Impact recall | Correct flagged commitments / all truly affected commitments |
| Owner accuracy | Correct current owner / cases with a known owner |
| Temporal accuracy | Correct active fact selection / temporal cases |
| Path validity | Returned paths whose relations and evidence all pass review / returned paths |
| Citation support | Supported factual claims / checked factual claims |
| Abstention accuracy | Correct unknown/conflict decisions / cases requiring them |
| Action correctness | Valid, nonduplicate, current actions / proposed actions |
| Access leakage | Forbidden details exposed; target zero |
| Runtime and cost | Extraction, retrieval, model, and total cost measured separately |

Report raw counts beside percentages. A small dataset does not justify broad accuracy claims. For example, 17/18 is descriptive evidence, not enterprise reliability.

## Proposed release gates

These are internal targets, not achieved results or official judging criteria. Require all five primary demo cases to behave correctly, zero observed leakage in the defined access tests, zero duplicate actions after replay, no unqualified “safe” result for missing data, and restart persistence.

For the held-out task set, aim for at least 90% precision and recall and 100% valid evidence paths. A missed target should appear in the results. It should trigger a fix or a narrower product claim, not selective removal of difficult cases.

Collect latency p50 and p95 only with enough timed runs to make the numbers meaningful, for example 50 repeated queries after warm-up. Report the data size, hardware, engine version, cache state, and sample count. Do not report DB time as total agent time.

## Artifacts to produce during implementation

Keep `data/synthetic/` for source records, `evals/gold/` for hidden truth, `evals/results/` for generated result files, and `queries/` for actual tested Cypher. Include a command that replays the exact evaluation. These paths are a proposed layout; they have not been created in this research phase.
