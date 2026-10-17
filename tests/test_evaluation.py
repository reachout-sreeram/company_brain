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
    omitted_default={k:v for k,v in correct.items() if k!='supersedes'}
    assert score_narrative([omitted_default],expected)['true_positive']==1
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


def hidden_inventory_bundle(*, hide_service=False):
    """Public source text is unchanged; only structured private identities differ."""
    from company_brain.ingestion import validate_bundle
    old='legacy-runner' if hide_service else 'report-job'
    secret='secret-legacy-service' if hide_service else 'secret-payroll-consumer'
    b=scenario('completion','migration','clear')
    b=b.model_copy(update={
        'entities':[e.model_copy(update={'id':secret,'visibility':'restricted','name':'Hidden payroll entity'}) if e.id==old else e for e in b.entities],
        'assertions':[a.model_copy(update={
            'subject_id':secret if a.subject_id==old else a.subject_id,
            'object_id':secret if a.object_id==old else a.object_id,
            'target_service_id':secret if a.target_service_id==old else a.target_service_id}) for a in b.assertions],
        'inventories':[i.model_copy(update={'service_id':secret if i.service_id==old else i.service_id,
            'consumer_ids':[secret if c==old else c for c in i.consumer_ids]}) for i in b.inventories]})
    validate_bundle(b)
    return b,secret


def check_inventory_privacy(store, secret):
    from company_brain.models import Caller
    public=RecordSearch(Brain(store),SCOPE,NOW)
    result=public.read_record('inventory-clear@1')
    assert result['coverage_incomplete']
    assert result['record']['inventories']==[]
    exposed=json.dumps(public.records)
    assert secret not in exposed and 'Hidden payroll entity' not in exposed
    assert secret not in json.dumps(public.search_records('legacy-runner'))
    authorized=RecordSearch(Brain(store,Caller(groups=frozenset({'public','restricted'}))),SCOPE,NOW)
    assert authorized.read_record('inventory-clear@1')['record']['inventories']
    assert secret in json.dumps(authorized.records)


@pytest.mark.parametrize('hide_service',[False,True])
def test_inventory_metadata_has_same_entity_authorization_as_graph(hide_service):
    bundle,secret=hidden_inventory_bundle(hide_service=hide_service)
    check_inventory_privacy(InMemoryAssessmentTestDouble(bundle),secret)


def test_search_redacts_inaccessible_supersession_ids_like_history():
    from company_brain.models import Bundle,Caller
    from company_brain.ingestion import validate_bundle
    b=scenario('completion','migration','clear')
    old=next(a for a in b.assertions if a.id=='clear-report')
    old=old.model_copy(update={'id':'secret-prior-assertion'})
    old_source=next(s for s in b.sources if s.key==old.source_key)
    source=old_source.model_copy(update={'id':'public-renewal','recorded_at':NOW})
    new=old.model_copy(update={'id':'public-renewal','source_id':source.id,'supersedes':[old.id],
                              'observed_at':NOW,'effective_from':NOW})
    b=b.model_copy(update={'sources':[*[s.model_copy(update={'visibility':'restricted'}) if s.key==old_source.key else s for s in b.sources],source],
        'assertions':[old if a.id=='clear-report' else a for a in b.assertions]+[new]})
    validate_bundle(b)
    store=InMemoryAssessmentTestDouble(b)
    public=RecordSearch(Brain(store),SCOPE,NOW)
    assert old.id not in json.dumps(public.records)
    assert public.read_record(source.key)['record']['assertions'][0]['supersedes']==[]
    authorized=RecordSearch(Brain(store,Caller(groups=frozenset({'public','restricted'}))),SCOPE,NOW)
    assert authorized.read_record(source.key)['record']['assertions'][0]['supersedes']==[old.id]
