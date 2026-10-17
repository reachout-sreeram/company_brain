"""Harness contract tests, not real-client or model-quality evidence."""
from datetime import datetime
import json
from pathlib import Path

import pytest

from company_brain.assessment import Brain
from company_brain.evaluation import Experiment, RecordSearch, Toolbox, run_arm, run_pair, score_answer, score_narrative
from test_assessment import InMemoryAssessmentTestDouble, NOW, SCOPE, scenario
from test_regressions import restricted_usage_bundle

ROOT=Path(__file__).parents[1]


def toolbox(bundle=None):
    return Toolbox(Brain(InMemoryAssessmentTestDouble(bundle or scenario())),SCOPE,NOW)


def test_search_pages_and_full_record_reads_follow_explicit_references():
    search=toolbox().search
    matches=search.search_records('invoice-export',limit=1)
    assert len(matches['matches'])==1 and matches['next_offset']==1
    record=search.read_record('source-blocked-network@1')['record']
    assert record['assertions'][0]['object_id']=='network-approval'
    owners=search.search_records('network-approval security')
    assert any(r['source_key']=='source-owns-network@1' for r in owners['matches'])


def test_search_never_returns_restricted_records_or_assertions():
    search=toolbox(restricted_usage_bundle()).search
    assert search.hidden
    assert 'restricted-usage@1' not in search.records
    with pytest.raises(ValueError,match='unavailable'): search.read_record('restricted-usage@1')


class ScriptedClient:
    execution_label='scripted test double; no model inference'
    def __init__(self): self.models=[]
    def step(self,**kwargs):
        self.models.append((kwargs['model'],kwargs['temperature'],kwargs['max_output_tokens']))
        if len(kwargs['messages'])==2:
            if kwargs['tools'][0]['name']=='find_entities':
                return {'tool':'assess_retirement','arguments':{'service_id':'legacy-runner','scope':SCOPE.model_dump(),'planned_at':NOW.isoformat()}}
            return {'tool':'search_records','arguments':{'query':'legacy-runner'}}
        return {'final':{'disposition':'blocked','evidence_ids':[]}}


def test_pair_uses_identical_model_settings_and_same_records_digest():
    client=ScriptedClient()
    result=run_pair(client,Experiment(model='scripted/offline'),toolbox(),'Can we retire legacy-runner?',NOW)
    assert len(set(client.models))==1
    assert result['graph']['records_digest']==result['search']['records_digest']
    assert result['graph']['revision']==result['search']['revision']
    assert all(r['execution']==client.execution_label for r in result.values())
    assert all(r['tool_calls']==1 for r in result.values())
    assert result['graph']['supported_evidence_ids']
    assert result['search']['supported_evidence_ids']==[]  # snippets alone do not substantiate assertion IDs


def test_context_and_tool_exhaustion_are_not_completed_results():
    client=ScriptedClient()
    assert run_arm(client,Experiment('scripted/offline',max_context_bytes=1),toolbox(),'graph','q',NOW)['status']=='context_budget_exhausted'
    assert run_arm(client,Experiment('scripted/offline',max_tool_calls=0),toolbox(),'graph','q',NOW)['status']=='tool_budget_exhausted'


def test_cross_arm_tools_and_scope_are_rejected():
    tools=toolbox()
    with pytest.raises(ValueError,match='unavailable'): tools.call('search','assess_retirement',{})
    with pytest.raises(ValueError,match='scope'): tools.call('graph','get_history',{'entity_id':'invoice-export','scope':{'environment':'staging','region':'eu'}})


def test_scoring_rejects_unsupported_citations_and_tracks_raw_counts():
    expected=json.loads((ROOT/'evals/gold/questions.json').read_text())['cases'][0]
    score=score_answer({'disposition':'no_known_blockers','evidence_ids':['invented'],'affected_workflows':['invented'],'gaps':[]},expected,[])
    assert score['unsupported_evidence']==1 and score['extra_workflows']==1
    assert not score['disposition_correct'] and not score['gap_reported']
    assert score['correct_owners']==0 and score['correct_blockers']==0


def test_narrative_scoring_detects_wrong_subject_and_duplicates():
    expected=json.loads((ROOT/'evals/gold/narrative.json').read_text())['cases'][0]['expected']
    correct=expected[0]
    wrong={**correct,'subject_id':'report-job'}
    assert score_narrative([wrong],expected)=={'expected':1,'proposed':1,'true_positive':0,'false_positive':1,'false_negative':1}
    result=score_narrative([correct,correct],expected)
    assert result['true_positive']==1 and result['false_positive']==1


def verify_questions(brain):
    gold=json.loads((ROOT/'evals/gold/questions.json').read_text())
    counts=[]
    for case in gold['cases']:
        result=brain.assess_retirement(gold['service_id'],SCOPE,datetime.fromisoformat(case['planned_at']),known_at=NOW)
        ids={e['assertion_id'] for e in result['evidence']}
        assert set(case['required_assertions'])<=ids
        assert result['disposition']==case['disposition']
        assert set(case['affected_workflows'])<=set(result['affected_workflows'])
        assert set(map(tuple,case['owner_pairs']))<={(o['entity_id'],o['owner_id']) for o in result['owners']}
        assert set(case['blocker_entities'])<={b['entity_id'] for b in result['blockers']}
        assert set(case['required_decisions'])<={d['decision_id'] for d in result['decisions']}
        assert result['coverage']['gaps']
        counts.append({'case':case['id'],'required_assertions':len(case['required_assertions']),'supported_required_assertions':len(set(case['required_assertions'])&ids),'disposition':result['disposition']})
    return counts


def test_additional_questions_use_same_initial_graph_and_known_time():
    counts=verify_questions(toolbox().brain)
    assert len(counts)==2
    assert sum(c['required_assertions'] for c in counts)==15
