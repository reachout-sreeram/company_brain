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


def empty_answer(disposition='needs_verification'):
    return {'disposition':disposition,'affected_workflows':[],'blocker_entities':[],
            'owner_pairs':[],'evidence_ids':[],'source_references':[],'decisions':[],
            'gaps':['Evidence is incomplete.'],'conflicts':[],'explanation':'Scripted contract probe only.'}


class ScriptedClient:
    execution_label='scripted test double; no model inference'
    def __init__(self): self.models=[]
    def step(self,**kwargs):
        self.models.append((kwargs['model'],kwargs['temperature'],kwargs['max_output_tokens']))
        if len(kwargs['messages'])==2:
            if kwargs['tools'][0]['name']=='find_entities':
                return {'tool':'assess_retirement','arguments':{'service_id':'legacy-runner','scope':SCOPE.model_dump(),'planned_at':NOW.isoformat()}}
            return {'tool':'search_records','arguments':{'query':'legacy-runner'}}
        return {'final':empty_answer('blocked' if kwargs['tools'][0]['name']=='find_entities' else 'needs_verification')}


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


class DecomposingClient:
    execution_label='scripted decomposition; no model inference'
    def step(self,**kwargs):
        messages=kwargs['messages']
        if len(messages)==2:
            return {'tool':'find_entities','arguments':{'query':'billing network approval'}}
        if messages[-1]['role']=='system':
            return {'final':empty_answer()}  # Reproduce premature finalization once.
        response=json.loads(messages[-1]['content'])
        if response.get('accepted') is False:
            query=response['validation_errors'][-1]['suggested_queries'][0]
            return {'tool':'find_entities','arguments':{'query':query}}
        if 'candidates' in response:
            return {'tool':'get_history','arguments':{'entity_id':response['candidates'][0]['id'],'scope':SCOPE.model_dump()}}
        if 'assertions' in response:
            rows=response['assertions']
            runtime=next((a for a in rows if a['predicate']=='RUNS_ON'),None)
            if runtime:
                return {'tool':'assess_retirement','arguments':{'service_id':runtime['object_id'],'scope':SCOPE.model_dump(),'planned_at':NOW.isoformat()}}
            requirement=next(a for a in rows if a['predicate']=='REQUIRES')
            return {'tool':'get_history','arguments':{'entity_id':requirement['object_id'],'scope':SCOPE.model_dump()}}
        answer=empty_answer(response['disposition'])
        answer['affected_workflows']=response['affected_workflows']
        answer['evidence_ids']=[e['assertion_id'] for e in response['evidence']]
        answer['source_references']=[{'assertion_id':e['assertion_id'],'source_key':e['source_id']+'@'+e['version']} for e in response['evidence']]
        answer['decisions']=[d['decision_id'] for d in response['decisions']]
        return {'final':answer}


def test_empty_multi_entity_lookup_cannot_end_in_premature_final():
    result=run_arm(DecomposingClient(),Experiment('scripted/offline'),toolbox(),'graph',
                   'What happens if an approval delays a workflow?',NOW)
    assert result['status']=='completed'
    assert result['events'][0]['response']['candidates']==[]
    assert result['events'][1]['request']['arguments']['query']=='billing'
    assert result['events'][1]['response']['candidates'][0]['id']=='monthly-billing'
    assert result['events'][-1]['request']['tool']=='assess_retirement'
    assert result['answer']['disposition']=='blocked'
    assert result['final_attempts'][0]['errors'][0]['code']=='empty_lookup_retry_required'
    assert result['tool_calls']==5


@pytest.mark.parametrize('arm,tool',[('graph','find_entities'),('search','search_records')])
def test_empty_retry_guidance_is_bounded_and_shared(arm,tool):
    class Client:
        execution_label='scripted empty lookups'
        def step(self,**kwargs):
            queries=[e['content'] for e in kwargs['messages'] if e['role']=='assistant' and json.loads(e['content']).get('tool')==tool]
            if len(queries)<3:
                return {'tool':tool,'arguments':{'query':['unknown foobar','unknown','foobar'][len(queries)]}}
            return {'final':empty_answer()}
    result=run_arm(Client(),Experiment('scripted/offline'),toolbox(),arm,'unknown thing',NOW)
    assert result['status']=='completed' and result['tool_calls']==3
    assert len([e for e in result['events'] if 'host_guidance' in e])==2


def reference_registry():
    from company_brain.evaluation import RetrievedReferences
    tools=toolbox()
    registry=RetrievedReferences(tools.search.entities)
    result=tools.call('graph','assess_retirement',{'service_id':'legacy-runner','scope':SCOPE.model_dump(),'planned_at':NOW.isoformat()})
    registry.collect(result)
    answer=empty_answer(result['disposition'])
    answer.update(evidence_ids=['permits-invoice'],source_references=[{'assertion_id':'permits-invoice','source_key':'source-permits-invoice@1'}],
                  decisions=['temporary-exception'],affected_workflows=['monthly-billing'])
    return registry,answer


def test_contract_accepts_exact_separate_assertion_source_workflow_decision_ids():
    registry,answer=reference_registry()
    assert registry.validate(answer)==[]


@pytest.mark.parametrize('field,value,code',[
    ('evidence_ids',['source-permits-invoice@1#permits-invoice'],'citation_format'),
    ('evidence_ids',['invented-assertion'],'unsupported_assertion'),
    ('evidence_ids',['inventory-initial'],'unsupported_assertion'),
    ('source_references',[{'assertion_id':'permits-invoice','source_key':'source-owns-invoice@1'}],'unsupported_source_pair'),
    ('source_references',[],'citation_pairing'),
    ('affected_workflows',['monthly-billing (production/eu)'],'unretrieved_entity'),
    ('affected_workflows',['invoice-export'],'entity_kind'),
    ('decisions',['temporary-exception permits use until November'],'unretrieved_entity'),
    ('decisions',['invoice-export'],'entity_kind'),
    ('owner_pairs',[['invoice-export','security']],'unsupported_owner_pair'),
    ('disposition','no_known_blockers','disposition_override'),
    ('gaps',[],'missing_coverage_gaps')])
def test_final_contract_rejects_observed_live_failures_and_unsupported_claims(field,value,code):
    registry,answer=reference_registry()
    errors=registry.validate({**answer,field:value})
    assert code in {e['code'] for e in errors}


@pytest.mark.parametrize('arm',['graph','search'])
def test_invalid_final_is_preserved_and_repair_is_bounded_for_both_arms(arm):
    class BadClient:
        execution_label='scripted invalid final'
        def step(self,**kwargs):
            return {'final':{**empty_answer(),'evidence_ids':['invented']}}
    result=run_arm(BadClient(),Experiment('scripted/offline'),toolbox(),arm,'q',NOW)
    assert result['status']=='invalid_final' and result['tool_calls']==0
    assert len(result['final_attempts'])==3
    assert all(a['answer']['evidence_ids']==['invented'] for a in result['final_attempts'])
    assert 'answer' not in result


def test_local_validation_repair_cannot_rewrite_original_strict_score():
    registry,answer=reference_registry()
    invalid={**answer,'evidence_ids':['source-permits-invoice@1#permits-invoice']}
    class RepairClient:
        execution_label='scripted final repair'
        def step(self,**kwargs):
            if len(kwargs['messages'])==2:
                return {'tool':'assess_retirement','arguments':{'service_id':'legacy-runner','scope':SCOPE.model_dump(),'planned_at':NOW.isoformat()}}
            if kwargs['messages'][-1]['role']=='tool' and json.loads(kwargs['messages'][-1]['content']).get('accepted') is False:
                return {'final':answer}
            return {'final':invalid}
    result=run_arm(RepairClient(),Experiment('scripted/offline'),toolbox(),'graph','q',NOW)
    assert result['status']=='completed' and len(result['final_attempts'])==1
    assert result['final_attempts'][0]['answer']==invalid
    assert result['answer']==answer
    expected=json.loads((ROOT/'evals/gold/questions.json').read_text())['cases'][0]
    assert score_answer(invalid,expected,registry.assertions)['unsupported_evidence']==1
    assert score_answer(answer,expected,registry.assertions)['unsupported_evidence']==0


@pytest.mark.parametrize('arm,tool',[('graph','find_entities'),('search','search_records')])
def test_repeated_identical_empty_query_still_consumes_retry_allowance(arm,tool):
    class Client:
        execution_label='scripted repeated miss'
        def step(self,**kwargs):
            queries=[m for m in kwargs['messages'] if m['role']=='assistant']
            if len(queries)<3:
                return {'tool':tool,'arguments':{'query':'nevermatches query'}}
            return {'final':empty_answer()}
    result=run_arm(Client(),Experiment('scripted/offline'),toolbox(),arm,'q',NOW)
    assert result['status']=='completed' and result['tool_calls']==3
    assert len([e for e in result['events'] if 'host_guidance' in e])==2


@pytest.mark.parametrize('arm',['graph','search'])
def test_both_arms_receive_actual_remaining_budget_and_finish_at_zero(arm):
    class Client:
        execution_label='scripted budget-aware finish'
        def step(self,**kwargs):
            if len(kwargs['messages'])==2:
                controls=json.loads(kwargs['messages'][1]['content'])['budgets']
                assert controls['data_tool_calls']==1
                return {'tool':'find_entities' if arm=='graph' else 'search_records','arguments':{'query':'legacy-runner'}}
            budget=json.loads(kwargs['messages'][-1]['content'])['host_budget']
            assert budget['remaining_data_tool_calls']==0
            return {'final':empty_answer()}
    result=run_arm(Client(),Experiment('scripted/offline',max_tool_calls=1),toolbox(),arm,'q',NOW)
    assert result['status']=='completed' and result['tool_calls']==1
