# Neo4j and GraphRAG implementation research

Research date: 15 October 2026. This is implementation research during problem discovery. It does not approve a product or architecture.

We inspected official technical documentation, selected public source files, research papers, and attributed customer accounts. We did not execute these systems or reproduce their measurements. Source links to `main` are mutable; pin a commit before adopting implementation details.

## Main finding

GraphRAG is a family of retrieval designs, not a single algorithm and not a guarantee supplied by a database. Separate three questions: what facts and evidence the graph stores, how a question selects relevant context, and whether the answer or action is correct.

Neo4j is useful to study because its public tooling exposes these choices. We can transfer the design patterns to FalkorDB where supported. We cannot assume its drivers, query extensions, procedures, or database-specific SDKs are portable.

## 1. Neo4j: build a source graph and an entity graph

The [knowledge-graph construction guide](https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_kg_builder.html) separates loading, chunking, embedding, schema definition, lexical graph construction, entity/relation extraction, pruning, writing, and resolution. The lexical graph preserves documents and chunks; extracted entities describe their domain. The guide labels the construction feature experimental.

Its default resolution merges nodes with the same label and name. This is a documented default, not proof of accurate identity resolution. Two employees can share a name. For our application, use authoritative source IDs and reviewed aliases, and leave ambiguity unresolved when needed. Typed model output improves structural consistency but does not prove the extracted assertion is true.

Illustrative schema, not copied source code:

```text
SourceVersion → contains → Chunk → supports → Assertion
Assertion → subject → Entity
Assertion → object → Entity
```

An entity mention establishes that a source discusses a person or system. It does not by itself establish ownership, approval, or a dependency. Store those as separately supported assertions.

## 2. Neo4j: hybrid search followed by graph traversal

The [retrieval guide](https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_rag.html) distinguishes vector retrieval, hybrid retrieval, graph expansion, text-to-Cypher, and tool selection. `HybridCypherRetriever` finds candidates with vector and full-text indexes, then uses a supplied traversal to retrieve related context. `Text2CypherRetriever` generates a query; the guide warns that generated syntax can fail.

We also read the [hybrid retriever implementation](https://raw.githubusercontent.com/neo4j/neo4j-graphrag-python/main/src/neo4j_graphrag/retrievers/hybrid.py). It validates search arguments, embeds a question when needed, builds a database-version-dependent search query, combines it with the configured retrieval query, and executes with read routing. Read routing is not a substitute for restricting database privileges.

The [query-construction source](https://raw.githubusercontent.com/neo4j/neo4j-graphrag-python/main/src/neo4j_graphrag/neo4j_queries.py) shows implementations that normalize vector and full-text scores, merge candidates, rank them, and apply a result limit. One route uses maximum score per node; a linear route weights the two components. This is implemented score fusion, not a universal ranking rule.

The transferable pattern is candidate discovery → typed expansion → evidence selection. Hybrid search handles phrasing and exact identifiers; graph traversal retrieves relationships that a similar passage alone may omit. For exact ownership or date questions, structured retrieval can avoid similarity search entirely.

## 3. Neo4j LLM Graph Builder: inspect the actual answer path

The [public application repository](https://github.com/neo4j-labs/llm-graph-builder) supports several retrieval modes and custom schemas. Its documented dependency on APOC and specific Neo4j syntax means it is not a drop-in FalkorDB application.

In [QA_integration.py](https://raw.githubusercontent.com/neo4j-labs/llm-graph-builder/main/backend/src/QA_integration.py), the inspected path selects retrieval configuration, compresses retrieved documents, reformulates follow-up questions, formats context, calls the answer model, and returns source/chunk/entity metadata. It also tracks tokens and timings. The formatting path limits context based on model configuration.

This exposes an important engineering boundary: preserving provenance in the graph is insufficient if answer-time compression discards the supporting passage. Carry evidence IDs through retrieval, reranking, compression, and rendering. A list of retrieved source links does not prove that every generated claim is supported. These are our implications from source inspection, not measured defects in the application.

## 4. Microsoft GraphRAG: community summaries for broad questions

The [research paper](https://arxiv.org/html/2404.16130v2) extracts entities and relationships, groups graph communities, summarizes them, and combines community-level answers. This targets broad sensemaking, such as identifying themes across a corpus. Its evaluation reports gains in comprehensiveness and diversity over a naive retrieval baseline on two corpora. Those metrics are not factual-accuracy scores. The paper acknowledges limited domain coverage and the need for stronger fabrication analysis.

The relevant design lesson is to use summary retrieval for broad thematic questions, not as the authoritative source for a precise current owner or deadline. Summaries can omit exceptions or become stale. The paper is author-run research, not an independent reproduction by us, and it does not establish a Neo4j-versus-FalkorDB performance result.

## 5. HippoRAG 2: associative retrieval with graph ranking

[HippoRAG 2](https://arxiv.org/abs/2502.14802) builds on Personalized PageRank with deeper passage integration and online LLM use. The authors report improved associative-memory performance and address factual-retrieval weaknesses in earlier structured approaches. The [repository](https://github.com/OSU-NLP-Group/HippoRAG) supplies an implementation and evaluation entry points.

The lesson is that connections can improve discovery beyond direct semantic similarity. However, relevance propagated through a graph is not evidence of business authority. Do not select an approver because a node ranks highly. Its research results are not a benchmark of a Company Brain deployment or a particular graph database engine.

## 6. Graphiti: temporal context as a separate implementation pattern

The previously reviewed [Graphiti repository](https://github.com/getzep/graphiti) documents episodic provenance, evolving facts, and FalkorDB support. That makes it a relevant candidate when changing organizational facts are central. Its presence does not remove the need to validate domain-specific authority, source deletion, and permission behavior.

We have not yet traced its complete extraction and invalidation implementation. Treat this as a documented capability and integration candidate, not a source-audited solution to our business rules.

## Where graphs have produced reported value

| Example | Graph's role | Reported outcome and evidence limit |
| --- | --- | --- |
| NASA lessons learned | Connect historical engineering knowledge across programs | Attributed account of useful cross-program reuse; historical, pre-LLM example |
| Anonymous technology/media company | Model business concepts and source metadata to support natural-language analytics | Vendor reports faster insights and less routine analyst work; no public reproducible deployment benchmark reviewed |
| Microsoft GraphRAG | Organize corpus-level context through communities | Author-run evaluation on defined sensemaking tasks |
| Neo4j public tooling | Implement graph construction and multiple retrieval paths | Inspectable implementation, not proof of customer success |
| HippoRAG 2 | Rank related knowledge for retrieval | Research benchmarks; not production impact evidence |

In the [2016 NASA interview](https://neo4j.com/blog/graph-visualization/david-meza-chief-knowledge-architect-nasa/), David Meza describes connecting lessons across Apollo, shuttle, and Orion work. He attributes an avoided problem to historical knowledge reuse. This demonstrates the potential value of a knowledge graph without an LLM. It is not a current deployment audit or a modern GraphRAG benchmark.

The [technology/media customer story](https://neo4j.com/customer-stories/technology-media-company/) describes a graph of business concepts and source metadata used with agents and Amazon Bedrock to support analytics. It reports 10× faster time-to-insight, 92% less analyst time on routine requests, and 150+ daily users. These are Neo4j-published customer claims. They do not isolate the effect of the database from modeling, integrations, or workflow changes. Metadata graphs can guide queries over source systems; they need not contain every underlying business record.

## What succeeded across these examples

Our synthesis: a useful graph makes a previously difficult relationship explicit, and the retrieval method matches the question. Sources remain inspectable. The graph is a maintained representation of a domain rather than a decorative visualization.

Do not conclude that graphs beat vector retrieval on every question. Ordinary document lookup can be simpler with search. A strong retrieval agent can cross several sources without a graph. Benchmark the relevant alternatives.

## Application patterns for our open problem space

| User need | Candidate graph use | Important boundary |
| --- | --- | --- |
| Find an owner | Person → approved responsibility → project/system | Expertise is not approval authority |
| Explain a decision | Decision → alternatives → constraints → source evidence | Mentioning an alternative does not mean it was rejected |
| Catch up | Project → changed assertions → current work → people | Define time window and approval state |
| Reuse lessons | Current issue → related constraint/failure → previous outcome | Similarity does not prove applicability |
| Understand impact | Changed entity → dependency paths → affected work | Missing paths may mean missing data |
| Reduce expert interruption | Product question → capability → implementation/decision → evidence | Incorrect confident answers can cost more than escalation |

These are exploration options. None is a selected product direction.

## Source and research limits

The links above identify the implementation files and references actually inspected. No third-party code was copied into this project. No package was installed and no database was started.

A Neo4j NICD-report landing page was found, but its full report methodology was not reviewed. Its advertised truthfulness improvement is therefore excluded from our conclusions. Broad vendor claims of eliminating hallucinations, SQL being unable to model relationships, or universal speed superiority are also excluded.
