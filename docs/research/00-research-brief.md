# Research brief

Research checked on 15 October 2026. The event is already in its build window.

## Recommendation

Build PromiseGraph, a Company Brain agent for customer-commitment impact analysis. Start with one question: “The export capability moved to 23 October. Which promises are now at risk, who owns the response, and why?”

Use a fictional B2B software company. Join release tickets, approved decisions, customer promises, people, teams, and source records in FalkorDB. Demonstrate an actual graph update and its effect on the agent's output. Draft follow-up tasks in a local action inbox, then persist their state in the graph.

This is a narrow, testable product hypothesis. No customer interviews, live competitor trials, or production measurements have validated it.

## What the research changed

A generic company assistant is a weak entry. [Glean](https://www.glean.com/blog/introducing-independent-agents), [Rovo](https://learning.atlassian.com/learning/lesson/what-is-rovo), and [Onyx](https://docs.onyx.app/welcome) already position themselves around organizational context and agents. A graph viewer does not establish an advantage.

Connecting multiple sources is also established. Cognee has an explicit [Company Brain Q&A cookbook](https://docs.cognee.ai/cookbooks/company-qa). Temporal fact handling is part of [Graphiti](https://github.com/getzep/graphiti). We must compare against these, not only a basic chatbot.

More seriously, [Drift](https://github.com/sharique2004/mmm-demo) already connects changed meeting decisions to GitHub issue updates using FalkorDB. [Hopper](https://github.com/vraj00222/hopper) traverses technical dependencies into customer obligations. The recommended project sits near both. Its defensible demo focus is release feasibility across commitments, explicit uncertainty, and correct action state after subsequent changes. Do not call that a new category.

## Facts, inferences, and open questions

| Statement | Status |
| --- | --- |
| FalkorDB must support central product behavior | Official requirement; see rules document |
| Company Brain includes ownership, decisions, freshness, and sources | Official theme |
| Sponsor wants developers to choose its context infrastructure | Inference from positioning, resources, and event recaps |
| Customer commitments offer a clearer demo than broad search | Our judgment |
| Teams will pay for this workflow | Unvalidated hypothesis |
| This implementation will beat good RAG | Unmeasured; evaluation is proposed |
| The proposed queries work on a pinned FalkorDB release | Unverified until implementation |

## What would make this useful

The user should receive a small set of affected promises, not a large graph. Each result must explain the date conflict, show the dependency path, expose the supporting source, and identify a person accountable now. It should distinguish “at risk” from “missing evidence.”

A source citation alone is insufficient. The cited text must support the relation used in the conclusion. A correct graph traversal over an invented dependency still produces a wrong answer.

## What would make us reject the idea

Reject or reduce scope if reliable extraction takes most of the event, if the graph does not improve the defined task against a fair retrieval baseline, or if the demo becomes a renamed version of Drift. In that case, ship an honest, smaller commitment checker with visible graph queries rather than a broad “company operating system.”

## Research scope

The landscape covers representative enterprise products, developer frameworks, and unusually close hackathon projects. It is not an exhaustive inventory of all companies. Product strengths come from primary documentation. Vendor outcomes remain vendor-reported. Limitations are labeled as documented constraints, integration tradeoffs, or unverified feature gaps. Missing public documentation does not prove a missing product feature.
