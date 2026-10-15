# Source register and research limits

Additional sources from the subsequent implementation-research pass are linked directly in [Neo4j and GraphRAG implementation research](13-neo4j-and-graphrag-implementation-research.md) and [FalkorDB pattern transfer](14-falkordb-pattern-transfer-and-experiments.md). The counts below describe the initial market-landscape review.

Access date: 15 October 2026. Links below are primary sources. Product documentation and repository READMEs establish published capabilities. They do not establish independent correctness or adoption. Customer stories and sponsor recaps are attributed accounts.

## Event

| ID | Source | Used for |
| --- | --- | --- |
| H1 | [Event overview](https://www.wemakedevs.org/hackathons/falkordb) | Track scope and event positioning |
| H2 | [Official rules](https://www.wemakedevs.org/hackathons/falkordb/rules) | Entry and submission requirements |
| H3 | [Schedule](https://www.wemakedevs.org/hackathons/falkordb/schedule) | Start and closing time |
| H4 | [Resources](https://www.wemakedevs.org/hackathons/falkordb/resources) | Official implementation references |

The overview's static extraction initially showed a loading registration panel. The browser-rendered page exposed the actual Rules, Schedule, and Resources routes, which were then read separately. No signed-in submission form was inspected.

## Database and implementation

| ID | Source | Used for |
| --- | --- | --- |
| F1 | [FalkorDB documentation](https://docs.falkordb.com/) | Engine model, indexes, clients, and license label |
| F2 | [FalkorDB repository](https://github.com/FalkorDB/FalkorDB) | Engine architecture and project scope |
| F3 | [Documentation index](https://docs.falkordb.com/llms.txt) | Compatibility cautions and product boundaries |
| F4 | [Known Cypher limitations](https://docs.falkordb.com/cypher/known-limitations) | Multiplicity, mutation limits, and query portability |
| F5 | [Persistence guide](https://docs.falkordb.com/operations/durability/persistence) | Volumes, durability, and ACL persistence distinction |
| F6 | [GraphRAG SDK repository](https://github.com/FalkorDB/GraphRAG-SDK) | Framework features, provenance, updates, and integration costs |
| F7 | [Community projects](https://www.falkordb.com/community-projects/) | Ecosystem discovery |
| F8 | [Memory Meets Motion recap](https://www.falkordb.com/blog/memory-meets-motion-the-falkordb-standouts/) | Prior-project discovery and sponsor emphasis |
| F9 | [Hack for Humanity recap](https://www.falkordb.com/blog/how-builders-at-hack-for-humanity-used-falkordb-to-solve-real-community-problems/) | Prior examples of query-centered demonstrations |

The docs homepage and index differ on Bolt wording. The recommendation deliberately uses the official RESP client until a pinned build is verified. A guessed authentication documentation route was inaccessible; no security claim relies on that page.

## Enterprise products

| ID | Source | Used for |
| --- | --- | --- |
| P1 | [Glean independent agents](https://www.glean.com/blog/introducing-independent-agents) | Current scope beyond search |
| P2 | [Glean access to information](https://docs.glean.com/user-guide/assistant/how-glean-accesses-info) | User-scoped answer context |
| P3 | [Glean at Zillow](https://www.glean.com/resources/customer-stories/zillow) | Attributed adoption and search-time outcomes |
| P4 | [What is Rovo?](https://learning.atlassian.com/learning/lesson/what-is-rovo) | Teamwork Graph and work context |
| P5 | [Rovo connector administration](https://support.atlassian.com/organization-administration/docs/manage-your-teamwork-graph-connectors/) | Setup and connection boundaries |
| P6 | [Teamwork Graph in Rovo MCP](https://community.atlassian.com/forums/discussion/3227595/use-teamwork-graph-in-rovo-mcp-server-open-beta) | Graph context available to external agents; announcement, not tested integration |
| P7 | [Guru Knowledge Agents](https://help.getguru.com/docs/intro-to-knowledge-agents) | Cited answers, quality controls, and actions |
| P8 | [Guru verification](https://help.getguru.com/docs/verifying-and-unverifying-cards) | Review cadence and eligibility |
| P9 | [Notion Enterprise Search](https://www.notion.com/help/enterprise-search) | Scope, citations, model-dependent context |
| P10 | [Microsoft Copilot connectors](https://learn.microsoft.com/en-us/microsoft-365/copilot/connectors/overview) | Synced versus federated data access |
| P11 | [Slack enterprise search help](https://slack.com/help/articles/38693462131219-Search-across-your-applications-with-enterprise-search) | Connected-source search |
| P12 | [Slack search security design](https://slack.engineering/how-we-built-enterprise-search-to-be-secure-and-private/) | Access filtering before model context |
| P13 | [Dust product](https://dust.tt/) | Shared agents, tools, and governance |
| P14 | [Dust customer stories](https://dust.tt/customers?refer=similarlabs_ai-agents_dust) | Breadth of reported customer applications |
| P15 | [Unblocked product](https://getunblocked.com/) | Cross-source graph context and conflict handling claims |
| P16 | [Unblocked at Rally](https://getunblocked.com/customers/rally/) | Attributed workflow and founder-time outcomes |
| P17 | [Onyx documentation](https://docs.onyx.app/welcome) | Search, agents, actions, and graph claims |
| P18 | [Gemini Enterprise connectors](https://cloud.google.com/gemini-enterprise/connectors) | Suite alternative and edition-specific source coverage |
| P19 | [Moveworks permissions](https://docs.moveworks.com/ai-assistant/enterprise-search/permissions) | Source permission and identity setup |
| P20 | [Moveworks search overview](https://help.moveworks.com/ai-assistant/enterprise-search/overview) | Goal-oriented retrieval |
| P21 | [Sana enterprise search](https://sanalabs.com/products/sana/enterprise-search) | Product scope |
| P22 | [Sana agents](https://sanalabs.com/products/sana/) | Work-agent scope |

A Dust documentation URL initially failed; a second redirected to a different topic. Neither is used as evidence for a specific competitive-intelligence feature. The product page is the basis for Dust's profile. Microsoft Learn returned an authorization notice alongside readable article text; only that visible article content was used.

## Frameworks and close projects

| ID | Source | Used for |
| --- | --- | --- |
| O1 | [Graphiti](https://github.com/getzep/graphiti) | Temporal graph framework, provenance, and FalkorDB support |
| O2 | [Cognee documentation](https://docs.cognee.ai/) | Memory platform scope |
| O3 | [Cognee Company Brain cookbook](https://docs.cognee.ai/cookbooks/company-qa) | Direct overlap and example-specific update semantics |
| O4 | [Microsoft GraphRAG](https://microsoft.github.io/graphrag/) | Community-based and entity-based retrieval |
| O5 | [LightRAG](https://github.com/HKUDS/LightRAG) | Graph retrieval and maintained update features |
| O6 | [Mem0](https://github.com/mem0ai/mem0) | Persistent memory and managed-versus-open benchmark distinction |
| O7 | [Drift](https://github.com/sharique2004/mmm-demo) | Close prior changed-decision workflow |
| O8 | [Continuum](https://github.com/vnmoorthy/continuum-memory-meets-motion) | Close operational-memory workflow and documented storage design |
| O9 | [Hopper](https://github.com/vraj00222/hopper) | Close dependency-to-customer-obligation workflow |

## Evidence limits

The review covers 12 commercial products, six frameworks or SDKs, and three close project examples. The categories overlap: a framework can be both an implementation option and a competitor to the proposed developer experience. GraphRAG SDK appears under database sources rather than being counted twice in the registry.

No competitor has been benchmarked here. No reported customer statistic has been independently reproduced. No exhaustive pricing comparison, procurement analysis, security certification audit, or license legal analysis was performed. Prices and plan details should be checked when choosing services. No hidden judging criteria were inferred as fact.

The prototype recommendation, candidate scores, architecture, cost envelope, evaluation gates, and demo schedule are original analysis based on this research. They are proposals. The repository currently contains documentation only.

For follow-up research, prioritize direct trials of the exact workflow in Glean or Rovo and one configurable agent platform. Then interview likely users. More generic product browsing is less valuable than testing whether the proposed gap actually exists.
