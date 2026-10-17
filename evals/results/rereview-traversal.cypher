MATCH (a:Assertion {rev:$rev})
WHERE a.status='approved' AND a.environment=$environment
      AND a.region=$region AND a.effective_from <= $planned
      AND (a.effective_until IS NULL OR $planned < a.effective_until)
      AND a.recorded_at <= $known
      AND (a.observed_at IS NULL OR a.observed_at <= $known)
      AND (NOT a.predicate IN ['RUNS_ON','DEPENDS_ON','REQUIRES','VERIFIED_CLEAR']
           OR a.effective_from <= $known)
      AND a.revoked=false
      AND a.source_visibility IN $groups AND a.subject_visibility IN $groups
      AND a.object_visibility IN $groups AND a.target_visibility IN $groups
OPTIONAL MATCH lineage=(new:Assertion {rev:$rev})-[:SUPERSEDES*1..16]->(a)
WHERE new.status='approved' AND new.environment=$environment
      AND new.region=$region AND new.effective_from <= $planned
      AND (new.effective_until IS NULL OR $planned < new.effective_until)
      AND new.recorded_at <= $known
      AND (new.observed_at IS NULL OR new.observed_at <= $known)
      AND (NOT new.predicate IN ['RUNS_ON','DEPENDS_ON','REQUIRES','VERIFIED_CLEAR']
           OR new.effective_from <= $known)
      AND new.revoked=false
      AND new.source_visibility IN $groups AND new.subject_visibility IN $groups
      AND new.object_visibility IN $groups AND new.target_visibility IN $groups
  AND all(member IN nodes(lineage) WHERE member.rev=$rev AND member.subject_id=a.subject_id
      AND member.status='approved' AND member.environment=$environment
      AND member.region=$region AND member.effective_from <= $planned
      AND member.recorded_at <= $known
      AND (member.observed_at IS NULL OR member.observed_at <= $known)
      AND (NOT member.predicate IN ['RUNS_ON','DEPENDS_ON','REQUIRES','VERIFIED_CLEAR']
           OR member.effective_from <= $known)
      AND member.revoked=false
      AND member.source_visibility IN $groups AND member.subject_visibility IN $groups
      AND member.object_visibility IN $groups AND member.target_visibility IN $groups)
WITH a, count(new) AS replacements WHERE replacements=0
WITH collect(a.id) AS active_ids
MATCH p=(consumer:Entity {rev:$rev})-[:RUNS_ON|DEPENDS_ON|REQUIRES*1..9]->(target:Entity {rev:$rev,id:$target})
WHERE all(edge IN relationships(p) WHERE edge.assertion_id IN active_ids)
WITH active_ids, p, consumer
OPTIONAL MATCH q=(consumer)-[:MIGRATION_TRACKED_BY|BLOCKED_BY*1..9]->(:Entity {rev:$rev})
WHERE all(edge IN relationships(q) WHERE edge.assertion_id IN active_ids)
RETURN p, [node IN nodes(p) | node.id], [edge IN relationships(p) | edge.assertion_id],
       collect([node IN nodes(q) | node.id]), collect([edge IN relationships(q) | edge.assertion_id]), consumer.id AS consumer_id
ORDER BY length(p), consumer_id LIMIT $limit
