# Company Brain landscape

Research date: 15 October 2026. This is a representative comparison, not a complete market census. We read public documentation and repositories. We did not buy subscriptions, run private evaluations, audit implementations, or interview customers.

“Strength” below means documented capability or an evidence-backed product advantage. “Tradeoff” is our assessment. “Unverified” means a specific feature was not established by the reviewed material. It does not mean the vendor cannot do it.

## The category has several layers

Enterprise search finds information across systems. Knowledge management adds trusted content and accountable owners. Work agents use that context to perform tasks. Memory infrastructure supplies retrieval and retained facts to those agents. Specialized context products focus on a particular team or workflow.

Our entry competes with the final user outcome across all of these layers. Calling it a “brain” does not create a separate market.

## Enterprise products

| Product | What it is good at | Documented constraint or assessed tradeoff | Implication for us |
| --- | --- | --- | --- |
| Glean | Broad organizational context and work agents | Enterprise integration and governance are substantial systems to replicate | Do not compete on connector count or generic agent actions |
| Atlassian Rovo | Context close to Jira, Confluence, and teamwork workflows | Connector setup requires organization administration; some connection limits apply | “Understand projects and owners” is already established |
| Guru | Verification, source trust, and knowledge accountability | Automated review has documented eligibility and cadence rules | Freshness badges alone are weak differentiation |
| Notion AI | Search and cited answers inside a familiar workspace | Search capability varies with selected model; plan eligibility applies | A better-looking document chat is insufficient |
| Microsoft 365 Copilot | Existing work surface with synced and live external context | Synced and federated connectors have different access and extension models | Do not claim all enterprise context must be batch indexed |
| Slack enterprise search | Search in the place teams already discuss work | Results depend on connected user accounts and supported sources | Conversation access and permission filtering are baseline needs |
| Dust | Shared agents, tool use, model choice, and human collaboration | A specific domain workflow still needs configuration and reliable inputs | “Answers plus actions” is not a unique product claim |
| Unblocked | Engineering context across code, issues, docs, and conversations | Our commitment workflow is outside its main engineering emphasis; absence is unverified | It is a close competitor on graph context and institutional knowledge |
| Onyx | Customizable, self-hostable work search and agents | Self-hosting brings operational responsibility | Open source, graphs, and custom tools are not sufficient distinction |
| Gemini Enterprise | Enterprise data connectors and Google's work/AI ecosystem | Connector behavior differs by edition and source | Suite distribution is a serious alternative to a new standalone tool |
| Moveworks | Employee search and permissions across business systems | Connector-specific identity and permission setup remains important | Reasoning over enterprise search is already agentic |
| Sana | Company search and expert agents in a shared work surface | Exact commitment-state workflow was not verified | A clean interface plus company knowledge is already crowded |

### Glean

Glean describes independent agents grounded in shared company context and permissions. Its [product announcement](https://www.glean.com/blog/introducing-independent-agents) directly contradicts the assumption that it is only a search bar. Its [access documentation](https://docs.glean.com/user-guide/assistant/how-glean-accesses-info) also makes user access part of answer context.

The [Zillow case study](https://www.glean.com/resources/customer-stories/zillow) reports 80% adoption across 7,000 employees and over 1.5 hours of weekly search time saved per employee. These are vendor-published customer outcomes, not independently reproduced results. They suggest that distribution, onboarding, and fitting existing workflows matter as much as retrieval architecture.

Our assessment: broad integrations and governance are an incumbent advantage. A small team should prove one result with a transparent test set. We have not established that Glean lacks commitment impact analysis.

### Atlassian Rovo

[Atlassian's introduction](https://learning.atlassian.com/learning/lesson/what-is-rovo) presents search, context, and work supported by the Teamwork Graph. Its [MCP announcement](https://community.atlassian.com/forums/discussion/3227595/use-teamwork-graph-in-rovo-mcp-server-open-beta) describes graph-context tools for other agents. A graph-backed assistant integrated into existing engineering tools is already a serious competitive pattern.

The [connector administration guide](https://support.atlassian.com/organization-administration/docs/manage-your-teamwork-graph-connectors/) requires administrative setup and documents connection restrictions. This is deployment friction, not proof of poor retrieval. Our response should be a small, reproducible workflow rather than a miniature Jira replacement.

### Guru

[Knowledge Agents](https://help.getguru.com/docs/intro-to-knowledge-agents) combine connected knowledge, cited answers, configurable behavior, and actions. The important lesson is stewardship: content needs an accountable owner and a defined trust state.

Guru's [verification guide](https://help.getguru.com/docs/verifying-and-unverifying-cards) documents daily quality runs, a seven-day review cooldown, and review eligibility for external content used in an answer. This is a specific scope and cadence boundary. It does not mean Guru cannot detect stale knowledge. Our proposed event-triggered impact check addresses a different question: which open commitments change after a new decision?

### Notion AI

[Enterprise Search](https://www.notion.com/help/enterprise-search) supports workspace and connected-app questions with citations. Its distribution advantage is the existing document workspace. The guide explicitly notes model-dependent access to workspace and connector context. This is a verified constraint; stale-data or multi-hop failure rates were not measured.

Do not claim Notion cannot work with relations. Its help page explicitly mentions database views, relations, and properties. Our differentiation must concern a specific decision and its testable correctness.

### Microsoft 365 Copilot

The [connector overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/connectors/overview) distinguishes indexed synced connectors from live federated connectors. It documents source-permission respect and differences in supported customization. This means a live, tool-based architecture is not by itself new.

Our assessment: an organization already invested in Microsoft may value deployment fit more than a new interface. A future product would need a clear reason to exist alongside its current suite. We have not tested an equivalent Copilot workflow.

### Slack

[Enterprise search](https://slack.com/help/articles/38693462131219-Search-across-your-applications-with-enterprise-search) adds connected application content to search and AI answers. Slack's [engineering account](https://slack.engineering/how-we-built-enterprise-search-to-be-secure-and-private/) describes using requester access controls before data reaches the model.

The product lesson is direct: enforce access before generation. Do not retrieve everything and hide forbidden citations afterward. Our synthetic permission tests must cover derived facts and caches too.

### Dust

[Dust](https://dust.tt/) combines company knowledge, shared agents, connected tools, model choice, and governance. Our assessment is that reusable task-specific agents and adoption inside teams are stronger patterns than one omniscient assistant.

Dust publishes [customer stories](https://dust.tt/customers?refer=similarlabs_ai-agents_dust). Those establish reported customer use, not a controlled comparison with our idea. We did not verify a particular release-to-promise reconciliation implementation. A custom Dust agent could plausibly address this problem, so avoid categorical feature-gap claims.

### Unblocked

[Unblocked](https://getunblocked.com/) explicitly claims cross-source graph reasoning, conflict resolution, freshness, permission-aware delivery, and organizational memory. This is the closest product counterexample to “existing tools cannot connect why a decision was made.”

Its [Rally story](https://getunblocked.com/customers/rally/) reports fewer founder interruptions and an estimated five to ten hours saved weekly. Treat those as reported outcomes. Our assessment: explaining engineering history alone will overlap strongly. The proposed focus is an explicit, dated obligation workflow spanning product and customer teams. We have not demonstrated that Unblocked cannot support it.

### Onyx

[Onyx documentation](https://docs.onyx.app/welcome) includes organizational search, custom agents, actions, hybrid retrieval, and AI-generated knowledge graphs. It is not a fair “vector-only” strawman. Self-hostability and configurability are useful strengths. Operating connectors, permissions, indexing, and updates remains work for a deployment team.

For our entry, starting from a full enterprise platform could consume the event and obscure original work. Borrow design lessons; do not ship a lightly renamed search UI.

### Gemini Enterprise, Moveworks, and Sana

Google's [connector catalog](https://cloud.google.com/gemini-enterprise/connectors) shows enterprise search spanning multiple sources, with edition-specific choices. Assess identity mapping and actual connector behavior before treating it as equivalent to an arbitrary permission model. We did not trial the commitment workflow.

[Moveworks permissions documentation](https://docs.moveworks.com/ai-assistant/enterprise-search/permissions) describes a unified permissions platform and source-specific access setup. Its [overview](https://help.moveworks.com/ai-assistant/enterprise-search/overview) presents planned, goal-oriented search. A multi-step search agent is therefore not a novel distinction.

[Sana](https://sanalabs.com/products/sana/enterprise-search) offers enterprise knowledge retrieval, while its [agent product](https://sanalabs.com/products/sana/) extends into work tasks. These pages establish product scope, not measured accuracy. The workflow gap remains unverified for all three. Their inclusion reinforces a narrow recommendation rather than a claim that we can outbuild a full enterprise suite.

## Developer frameworks and research systems

| System | Documented strength | Boundary for this product |
| --- | --- | --- |
| Graphiti / Zep | Temporal context, provenance, hybrid retrieval | Memory infrastructure still needs business rules and action semantics |
| Cognee | Configurable memory pipeline; explicit Company Brain cookbook | A starter is not a distinct product; update semantics need inspection |
| Microsoft GraphRAG | Entity graphs, community summaries, local/global retrieval | Corpus understanding differs from reliable commitment state transitions |
| LightRAG | Graph-assisted retrieval with maintained ingestion and evaluation features | Need to verify the selected storage backend and authorization design |
| Mem0 | Persistent user, session, and agent memory | Conversation memory does not define operational ownership or obligation status |
| FalkorDB GraphRAG SDK | FalkorDB-native ingestion and retrieval tooling | Framework output needs application-level validation |

### Graphiti and Zep

[Graphiti](https://github.com/getzep/graphiti) preserves fact validity and episode provenance and supports FalkorDB. That directly weakens a novelty claim based only on remembering changing facts. It is a framework; the surrounding application still needs policies and workflows. The repository distinguishes open Graphiti from managed Zep, whose infrastructure should not be assumed to use our chosen backend.

Choose it if its temporal model passes our scenarios with less work than a small custom layer. Do not report its published latency or recall as our measured result.

### Cognee

The [Company Brain cookbook](https://docs.cognee.ai/cookbooks/company-qa) joins a company database, tickets, and documents through a declared graph model. It already answers ownership and decision questions across sources. This is a direct conceptual overlap, not merely a related library.

The cookbook states that edited files remain alongside old versions unless the dataset is cleared. For that example, explicit “current fact” handling needs attention. This is not a blanket claim about every Cognee deployment. Our proposed application must show which version is valid without rebuilding away its history.

### Microsoft GraphRAG

[GraphRAG documentation](https://microsoft.github.io/graphrag/) describes entity extraction, community structure, summaries, and several retrieval modes. It also recommends prompt tuning and documents version migration concerns. It is useful for understanding a corpus. Our assessment: importing its whole pipeline is unnecessary for a small operational graph unless tests show that its retrieval helps.

### LightRAG

The [repository](https://github.com/HKUDS/LightRAG) documents graph retrieval, document deletion and graph regeneration, context-returning APIs, reranking, and evaluation integrations. Do not describe graph retrieval frameworks as universally static. Its exact FalkorDB integration and the chosen release's business-state behavior were not validated in this research.

### Mem0

[Mem0](https://github.com/mem0ai/mem0) focuses on retained memory across users, sessions, and agents. Its README distinguishes managed benchmark results from the open SDK. That distinction is important. We should use memory only where the task needs it and avoid retaining model-generated conclusions as authoritative source facts.

## Close projects that materially affect originality

### Drift

[Drift's README](https://github.com/sharique2004/mmm-demo) describes meeting-transcript extraction, a FalkorDB decision graph, supersession, and reviewed GitHub issue comments after a decision changes. This substantially covers the first idea considered during research.

Reject “meeting decisions changed, update the issue” as our main pitch. A different name and UI would not make it distinct. Its runtime was not tested here. Read its source before claiming any detailed implementation gap.

### Continuum

[Continuum](https://github.com/vnmoorthy/continuum-memory-meets-motion) describes open-work tracking, cited actions, and outcome write-back. Its README architecture places SQLite in the memory plane and FalkorDB as a mirror. That is a documented design choice, not a code audit or a judgment under another event's rules.

For our entry, keep the essential impact queries and action state in FalkorDB. Avoid a second store that can answer the whole product question when the graph is removed.

### Hopper

[Hopper](https://github.com/vraj00222/hopper) connects advisories through dependencies and services to customers and contract clauses. It already overlaps with technical change → customer impact → governed action.

Our proposal focuses on promised delivery feasibility, scoped exceptions, changed owners, and incomplete evidence. This is a narrower workflow distinction, not proof of a moat. Do not adopt its absence-of-path claims without a completeness qualification.

## What success seems to require

The strongest commercial pattern is useful context delivered where work already occurs, with access control and measurable reduction in manual effort. The strongest framework pattern is reusable ingestion and retrieval infrastructure. The strongest hackathon pattern is a small, visible loop in which graph facts cause an agent decision.

These are interpretations of the reviewed evidence. Only Glean and Unblocked outcomes above have specific cited customer claims in this document. Product pages establish positioning and documented capabilities, not independent accuracy, profitability, or market leadership.

## The remaining hypothesis

There may be room for a small, auditable commitment-reconciliation tool that a delivery lead can run without deploying a broad company AI platform. Validate that with users and direct competitor trials after the event. For this hackathon, prove correctness and clarity on a disclosed corpus. Do not claim to have found an uncontested market.
