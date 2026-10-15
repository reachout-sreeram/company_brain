# FalkorDB research

The product name is FalkorDB. This document separates the database engine, retrieval frameworks, and our application responsibilities.

## What the database contributes

FalkorDB stores a property graph: labeled nodes and typed relationships with properties. Its implementation uses sparse adjacency matrices and GraphBLAS. Queries use Cypher with implementation-specific support. Full-text, vector, and range indexes are documented. These are capabilities, not measured performance results for this project. [Official documentation](https://docs.falkordb.com/), [core repository](https://github.com/FalkorDB/FalkorDB).

For our task, the benefit is a directly queryable chain from a release through a capability into customer promises and owners. A semantic search can find a release announcement. A graph query can enumerate promises linked to that capability, including records that use different words.

SQL can express this with joins and recursive queries. Do not claim relational databases cannot represent these relationships. FalkorDB is a suitable mandated engine because the proposed workload centers on typed, repeated traversals and evidence paths. Its speed advantage against SQL, Neo4j, or another engine has not been measured here.

## Proposed use of engine capabilities

| Capability | Use | What we must still implement |
| --- | --- | --- |
| Nodes and relationships | People, capabilities, promises, sources | Stable IDs and extraction validation |
| Cypher pattern matching | Impact and ownership traversal | Correct time and status filters |
| Text or vector indexes | Find candidate entities from a question | Ranking, ambiguity handling, access filtering |
| Multiple graphs | Separate synthetic workspaces if needed | Trusted graph selection and authorization |
| Read-only queries | Agent retrieval tools | Tool allowlist, timeouts, bounded paths |
| Durable storage | Retain facts and action outcomes | Persistence configuration and restart verification |

Separate graph names do not establish source-level authorization. The application must prevent a user from selecting another workspace's graph or reading an unauthorized supporting source.

## Compatibility matters

The documentation is not fully consistent on transport. The main page advertises RESP and Bolt, while the [documentation index](https://docs.falkordb.com/llms.txt) describes Redis-protocol commands and warns against assuming Bolt. Use the official FalkorDB client over RESP for the MVP. Pin the exact engine and client versions after a successful smoke test. Do not choose a Neo4j driver from assumed compatibility.

The [known limitations](https://docs.falkordb.com/cypher/known-limitations) document warns that unreferenced relationships can affect multiplicity, `LIMIT` does not bound preceding eager mutations, and some index and aggregation behavior differs from expected Cypher patterns. For this project: test counts explicitly, avoid using a final `LIMIT` as a write safety control, and verify every query on the pinned engine. Do not paste Neo4j procedures into the app unchecked.

## Framework options

| Option | Useful capability | Decision for this build |
| --- | --- | --- |
| Official FalkorDB client | Direct control over application schema and queries | Recommended default |
| FalkorDB GraphRAG SDK | Extraction, retrieval, typed schema, provenance, updates | Time-boxed integration spike |
| Graphiti with FalkorDB | Temporal facts and hybrid retrieval | Alternative if temporal ingestion dominates |
| Cognee | Broad document-to-memory pipeline and Company Brain starter | Learn from it; do not repackage the cookbook |

The [GraphRAG SDK README](https://github.com/FalkorDB/GraphRAG-SDK) documents source-chunk provenance, grounded-answer controls, and incremental document updates. It also notes that `finalize()` scans the graph for deduplication and that update concurrency has correctness constraints. Treat SDK updates as ingestion mechanics; they do not define whether a business promise has been superseded. Its published benchmark is vendor-reported and is not our evaluation.

[Graphiti](https://github.com/getzep/graphiti) supports FalkorDB and preserves temporal provenance. It can reduce custom memory work, but its graph schema and extraction behavior must fit our deterministic commitment checks. A framework is useful only if we can inspect and explain the resulting facts.

Recommendation: implement a small typed extraction boundary plus explicit Cypher tools. Choose one ingestion framework only after it passes our source-update and deletion cases. Do not install several overlapping memory layers.

## Operational limits and costs

Use a persistent container or managed instance. The [persistence guide](https://docs.falkordb.com/operations/durability/persistence) covers volumes and durability options. ACL users need separate persistence configuration. Confirm the storage path against the pinned image, then test a restart. A volume alone is not proof of crash recovery.

Memory use includes graph data, text, indexes, and embeddings. Estimate it from the actual corpus; do not infer capacity from a tiny seed. Bound traversal depth and returned rows. Detect cycles. Report a depth cap as a coverage limit.

For a hackathon, extraction and generation calls may dominate total cost. Cache unchanged source extraction by content hash. Log token usage, model, request count, and billed cost where available. An illustrative planning envelope is $10–30 for model calls, not a provider quote or a measured requirement. Set a hard spending cap before bulk ingestion.

The core is labeled SSPLv1 in its documentation; the GraphRAG SDK repository lists Apache-2.0. Record component licenses separately. This research does not make a licensing-compliance determination. [Core documentation](https://docs.falkordb.com/), [SDK](https://github.com/FalkorDB/GraphRAG-SDK).

## Technical spike exit criteria

Before product work, prove connection, parameterized writes, read-only traversal, idempotent ingestion, source update, source removal, and restart persistence on pinned versions. Save exact commands and actual output. No such spike has been run in this research phase.
