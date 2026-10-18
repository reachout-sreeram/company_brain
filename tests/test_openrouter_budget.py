"""Mocked HTTP and durable accounting tests; no provider requests or user keys."""
from decimal import Decimal
import json

import httpx
import pytest

from company_brain.openrouter import (BudgetError,LUNA_MODEL,OpenRouterConfig,OpenRouterError,
    OpenRouterEvaluationClient,OpenRouterSession,SpendLedger)

MESSAGES=[{'role':'user','content':'Return a JSON object.'}]


def response(content=None,*,cost='0.00001',completion=10,model=LUNA_MODEL,status=200):
    return httpx.Response(status,json={'model':model,'usage':{'cost':cost,'prompt_tokens':10,'completion_tokens':completion},
        'choices':[{'finish_reason':'stop','message':{'content':json.dumps(content if content is not None else {'ok':True})}}]})


def session(handler,*,ledger=None,**config):
    return OpenRouterSession(OpenRouterConfig(model=LUNA_MODEL,api_key='DUMMY_NOT_A_KEY',allow_live=True,**config),
                             transport=httpx.MockTransport(handler),ledger=ledger)


def test_luna_omits_temperature_and_fences_model_provider_and_prices():
    def check(request):
        data=json.loads(request.content)
        assert data['model']==LUNA_MODEL and 'temperature' not in data
        assert data['reasoning']=={'effort':'none'}
        assert data['max_tokens']==128
        assert data['provider']['only']==['openai'] and not data['provider']['allow_fallbacks']
        assert data['provider']['require_parameters']
        assert data['provider']['max_price']=={'prompt':0.1,'completion':0.5,'request':0}
        assert request.headers['authorization']=='Bearer DUMMY_NOT_A_KEY'
        return response()
    client=session(check,max_output_tokens=128)
    client.complete(MESSAGES)
    assert client.ledger.snapshot()['actual_usd']=='0.00001'


def test_missing_credential_makes_no_request_or_reservation(tmp_path):
    ledger=SpendLedger(tmp_path/'ledger.json')
    config=OpenRouterConfig(model=LUNA_MODEL,allow_live=True)
    client=OpenRouterSession(config,transport=httpx.MockTransport(lambda _:pytest.fail('unexpected request')),ledger=ledger)
    with pytest.raises(OpenRouterError,match='configured'): client.complete(MESSAGES)
    assert not (tmp_path/'ledger.json').exists()


@pytest.mark.parametrize('value',[None,'NaN','-1','Infinity',True])
def test_missing_invalid_cost_halts_and_accounts_conservatively(value):
    client=session(lambda _:response(cost=value))
    with pytest.raises(OpenRouterError,match='cost metadata'): client.complete(MESSAGES)
    state=client.ledger.snapshot()
    assert state['halted'] and state['actual_usd']=='0'
    assert Decimal(state['conservative_usd'])>0 and state['reserved_usd']=='0'
    with pytest.raises(BudgetError,match='halted'): client.complete(MESSAGES)


def test_retry_allowance_reserved_before_first_request_and_counts_every_attempt():
    calls=[]
    ledger=SpendLedger()
    def handler(request):
        calls.append(request)
        state=ledger.snapshot(); entry=next(iter(state['reservations'].values()))
        assert entry['remaining_attempts']==3-len(calls)
        return response(cost='0.00001',status=503 if len(calls)==1 else 200)
    client=session(handler,ledger=ledger,max_attempts=2)
    client.complete(MESSAGES)
    state=ledger.snapshot()
    assert len(calls)==2 and Decimal(state['actual_usd'])==Decimal('0.00002')
    assert state['reserved_usd']=='0'
    assert len(next(iter(state['reservations'].values()))['attempts'])==2


def test_retry_bundle_cannot_fit_cap_so_no_first_request():
    ledger=SpendLedger(limit='0.0025')
    client=session(lambda _:pytest.fail('request before retry budget reserved'),ledger=ledger,max_attempts=2)
    with pytest.raises(BudgetError,match='cap'): client.complete(MESSAGES)
    assert ledger.snapshot()['reservations']=={}


def test_timeout_is_not_retried_or_assumed_free():
    calls=[]
    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout('DUMMY_NOT_A_KEY must not appear',request=request)
    client=session(handler,max_attempts=3)
    with pytest.raises(OpenRouterError,match='timed out') as error: client.complete(MESSAGES)
    assert len(calls)==1 and 'DUMMY_NOT_A_KEY' not in str(error.value)
    assert client.ledger.snapshot()['halted']


def test_durable_ledger_reused_across_clients_and_restart(tmp_path):
    path=tmp_path/'budget.json'
    first=session(lambda _:response(cost='0.001'),ledger=SpendLedger(path,limit='0.003'),max_output_tokens=3000)
    first.complete(MESSAGES)
    second=session(lambda _:pytest.fail('cap would be exceeded'),ledger=SpendLedger(path,limit='0.003'))
    with pytest.raises(BudgetError,match='cap'): second.complete(MESSAGES)
    state=SpendLedger(path,limit='0.003').snapshot()
    assert Decimal(state['actual_usd'])==Decimal('0.001')
    assert 'DUMMY_NOT_A_KEY' not in path.read_text() and 'Return a JSON' not in path.read_text()


def test_crashed_open_reservation_blocks_restart(tmp_path):
    path=tmp_path/'budget.json'
    SpendLedger(path).reserve(LUNA_MODEL,100,100,1)
    with pytest.raises(BudgetError,match='unreconciled'):
        SpendLedger(path).reserve(LUNA_MODEL,100,100,1)


def test_limit_above_approved_cap_and_changed_persistent_limit_are_rejected(tmp_path):
    with pytest.raises(BudgetError,match='USD 3'): SpendLedger(limit='3.01')
    path=tmp_path/'ledger.json'
    ledger=SpendLedger(path,limit='1'); key=ledger.reserve(LUNA_MODEL,10,10,1); ledger.finish(key)
    with pytest.raises(BudgetError,match='mismatch'): SpendLedger(path,limit='3').snapshot()


@pytest.mark.parametrize('maximum',[0,True,3001,16001])
def test_output_limits_rejected_before_transport(maximum):
    client=session(lambda _:pytest.fail('request with invalid limit'))
    with pytest.raises(OpenRouterError,match='output limit'): client.complete(MESSAGES,max_output_tokens=maximum)
    assert client.ledger.snapshot()['reservations']=={}


def test_output_overrun_or_model_substitution_halts_after_accounting_known_cost():
    for kwargs in ({'completion':3001},{'model':'another-provider/not-approved'}):
        client=session(lambda _:response(**kwargs))
        with pytest.raises(OpenRouterError,match='reserved bounds'): client.complete(MESSAGES)
        state=client.ledger.snapshot()
        assert state['halted'] and Decimal(state['actual_usd'])==Decimal('0.00001')


def test_actual_cost_above_quote_is_recorded_and_halts():
    client=session(lambda _:response(cost='0.01'))
    with pytest.raises(OpenRouterError,match='reserved bounds'): client.complete(MESSAGES)
    assert client.ledger.snapshot()['halted']
    assert Decimal(client.ledger.snapshot()['actual_usd'])==Decimal('0.01')


def test_evaluation_client_keeps_same_model_settings_and_json_action_protocol():
    wire=[]
    def handler(request):
        wire.append(json.loads(request.content))
        result=response()
        body=result.json()
        body['choices']=[{'finish_reason':'tool_calls','message':{'role':'assistant','content':None,'tool_calls':[
            {'id':'call_final','type':'function','function':{'name':'finish_answer','arguments':json.dumps({'disposition':'blocked'})}}]}}]
        return httpx.Response(200,json=body)
    client=OpenRouterEvaluationClient(session(handler))
    for name in ('assess_retirement','search_records'):
        assert client.step(model=LUNA_MODEL,temperature=None,max_output_tokens=100,
            messages=MESSAGES,tools=[{'name':name,'arguments':'read only'}])['final']['disposition']=='blocked'
    assert {w['model'] for w in wire}=={LUNA_MODEL}
    assert all('temperature' not in w for w in wire)
    assert all(w['tool_choice']=='required' and w['parallel_tool_calls'] is False for w in wire)
    assert all('response_format' not in w for w in wire)
    assert 'mocked' in client.execution_label
    assert len(next(iter(client.session.ledger.snapshot()['reservations'].values()))['attempts'])==1
    with pytest.raises(OpenRouterError,match='temperature'):
        client.step(model=LUNA_MODEL,temperature=0,max_output_tokens=100,messages=MESSAGES,tools=[])


def test_input_limit_and_nontext_messages_rejected_before_transport():
    client=session(lambda _:pytest.fail('unbounded request'))
    with pytest.raises(OpenRouterError,match='byte budget'):
        client.complete([{'role':'user','content':'x'*131072}])
    with pytest.raises(OpenRouterError,match='text messages'):
        client.complete([{'role':'user','content':[{'type':'image_url','image_url':'x'}]}])


@pytest.mark.parametrize('field',['OPENROUTER_API_KEY','OPEN_ROUTER'])
def test_named_credential_is_ignored_untracked_and_process_memory_only(tmp_path,monkeypatch,field):
    from company_brain.live_evaluation import load_named_credential,redact
    from types import SimpleNamespace
    path=tmp_path/'.env.local'
    path.write_text('UNRELATED=do_not_export\n'+field+'="DUMMY_VALUE"\n')
    def git(args,**kwargs):
        return SimpleNamespace(returncode=0 if args[1]=='check-ignore' else 1)
    monkeypatch.setattr('company_brain.live_evaluation.subprocess.run',git)
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    assert load_named_credential(tmp_path)=='DUMMY_VALUE'
    import os
    assert 'OPENROUTER_API_KEY' not in os.environ
    assert redact({'answer':'DUMMY_VALUE is withheld'},'DUMMY_VALUE')=={'answer':'[REDACTED] is withheld'}
    assert path.read_text().endswith(field+'="DUMMY_VALUE"\n')


def test_nonignored_or_tracked_credential_file_never_read(tmp_path,monkeypatch):
    from company_brain.live_evaluation import load_named_credential
    from types import SimpleNamespace
    (tmp_path/'.env.local').touch()
    monkeypatch.setattr('company_brain.live_evaluation.subprocess.run',lambda *a,**k:SimpleNamespace(returncode=0))
    with pytest.raises(OpenRouterError,match='ignored and untracked'): load_named_credential(tmp_path)


def test_native_call_results_use_original_call_id_and_real_tool_role():
    requests=[]
    def handler(request):
        data=json.loads(request.content);requests.append(data)
        if len(requests)==1:
            name='search_records';args={'query':'legacy-runner','offset':0,'limit':5};ident='original_call_id'
        else:
            assert data['messages'][-1]=={'role':'tool','tool_call_id':'original_call_id','content':'{"matches": []}'}
            assert data['messages'][-2]['tool_calls'][0]['id']=='original_call_id'
            name='finish_answer';args={'disposition':'needs_verification'};ident='final_id'
        result=response().json()
        result['choices']=[{'finish_reason':'tool_calls','message':{'role':'assistant','content':None,'tool_calls':[
            {'id':ident,'type':'function','function':{'name':name,'arguments':json.dumps(args)}}]}}]
        return httpx.Response(200,json=result)
    client=OpenRouterEvaluationClient(session(handler))
    tools=[{'name':'search_records','arguments':'query, offset, limit'}]
    messages=[{'role':'system','content':'policy'},{'role':'user','content':'question'}]
    action=client.step(model=LUNA_MODEL,temperature=None,max_output_tokens=200,messages=messages,tools=tools)
    messages.extend([{'role':'assistant','content':json.dumps(action)},{'role':'tool','content':'{"matches": []}'}])
    assert client.step(model=LUNA_MODEL,temperature=None,max_output_tokens=200,messages=messages,tools=tools)['final']['disposition']=='needs_verification'


def test_free_text_multiple_actions_are_rejected_not_silently_salvaged():
    client=OpenRouterEvaluationClient(session(lambda _:response({'tool':'search_records','arguments':{}})))
    with pytest.raises(OpenRouterError,match='native function'):
        client.step(model=LUNA_MODEL,temperature=None,max_output_tokens=200,messages=MESSAGES,tools=[])
