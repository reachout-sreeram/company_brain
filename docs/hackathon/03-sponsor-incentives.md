# What FalkorDB gains

The sponsor can gain adoption, reusable examples, technical feedback, and evidence for its positioning. That is an inference from public material. We do not know its internal campaign targets, conversion goals, or judging discussions.

## What is directly observable

The event makes meaningful database use a condition of entry. The [official resources](https://www.wemakedevs.org/hackathons/falkordb/resources) guide participants toward its clients, graph tooling, and ecosystem. The [database repository](https://github.com/FalkorDB/FalkorDB) positions the engine for knowledge graphs and GraphRAG.

Past sponsor recaps highlight actual queries, graph-specific behavior, citations, and implementation details. The [Hack for Humanity recap](https://www.falkordb.com/blog/how-builders-at-hack-for-humanity-used-falkordb-to-solve-real-community-problems/) praises bounded read queries, typed facts, repeatable ingestion, and explicit database-failure behavior. This is evidence of what the sponsor has chosen to showcase previously, not a rubric for this event.

## Likely business goals and our response

| Likely goal | Why it is plausible | Useful evidence from our entry |
| --- | --- | --- |
| Become an agent infrastructure choice | The event centers on agent context | Agent decisions actually use graph results |
| Reduce adoption friction | Setup guides and client examples are prominent | Reproducible setup and documented integration findings |
| Demonstrate value beyond vector retrieval | Relationship-based questions recur in positioning | Fair comparison on relationship-dependent questions |
| Grow the ecosystem | The event exposes multiple libraries and integrations | A reusable extraction contract and query set |
| Create public reference material | Recaps link projects and explain their queries | Clear repository, demo, and technical write-up |
| Find future Cloud or enterprise users | Local and managed options create an adoption path | Honest operational notes and a plausible pilot |
| Learn product weaknesses | New developers stress documentation and clients | Minimal reproductions for actual failures |

“Buy for” should not be read as the sponsor buying our project or IP. The rules retain participant ownership. Commercial follow-up is possible, but none is promised.

## The technical proposition they likely want demonstrated

An agent often needs context assembled from relationships, not merely similar passages. A graph can become the working record used during retrieval, planning, and updates. A useful demonstration therefore shows a changed fact altering the result of a graph query and the next permitted action.

This does not prove that graphs solve hallucination, that FalkorDB is faster than every alternative, or that all agent memory should be a graph. The meaningful claim is narrower: a defined relationship query supports a useful decision with inspectable evidence.

## Lessons from prior projects

The [Memory Meets Motion recap](https://www.falkordb.com/blog/memory-meets-motion-the-falkordb-standouts/) includes Drift, which maps changed decisions to issues, and Hopper, which maps vulnerabilities to customer obligations. It also highlights retained action outcomes and deterministic controls. These are close precedents, so generic claims about “memory plus action” are weak.

Some recap claims need care. An absent path proves only the absence of a path in the loaded graph under the chosen constraints. It does not prove real-world safety if ingestion is incomplete. Likewise, a traversal that can be written in Cypher can often be implemented with SQL. Do not repeat vendor comparisons as mathematical impossibility claims.

## A credible sponsor-facing pitch

“We used FalkorDB to connect release facts, customer promises, and ownership. The agent retrieves a typed path for each flagged commitment. A new decision changes the current graph, and the next run updates the response plan. Our evaluation compares that workflow with retrieval baselines on the same corpus.”

Only use the past tense after building and measuring it. During planning, say “we propose.”

## What weakens the entry

Adding the database only to draw a network, showing hardcoded impact lists, reporting synthetic revenue as saved revenue, or claiming superiority without a baseline will make the project less credible. A good reference project should be easy for another developer to inspect, reproduce, and adapt.
