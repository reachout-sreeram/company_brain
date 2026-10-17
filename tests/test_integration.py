"""Opt-in real FalkorDB integration. Never silently substitutes a database."""
import json
import os
from datetime import datetime
from pathlib import Path
from time import perf_counter

import pytest
from company_brain.assessment import Brain
from company_brain.ingestion import extract_bundle
from company_brain.models import Bundle, Scope
from company_brain.store import FalkorStore, StoreUnavailable

pytestmark = [pytest.mark.integration, pytest.mark.skipif(os.getenv("COMPANY_BRAIN_INTEGRATION")!="1",reason="set COMPANY_BRAIN_INTEGRATION=1 to start real isolated FalkorDB")]
ROOT=Path(__file__).parents[1]
SCOPE=Scope(environment="production",region="eu")
AT=datetime.fromisoformat("2026-10-17T12:00:00+00:00")


def fixture(name): return Bundle.model_validate_json((ROOT/f"data/synthetic/{name}.json").read_text())


@pytest.fixture
def store(tmp_path):
    from redislite.falkordb_client import FalkorDB
    db=FalkorDB(str(tmp_path/"integration.rdb"))
    store=FalkorStore(db,"company_brain_test_integration",writable=True)
    yield store
    store.reset(store.graph_name)
    db.client.shutdown()


def test_real_graph_loop_and_failed_publication(store):
    brain=Brain(store)
    times=[]
    expected=["blocked","blocked","needs_verification","no_known_blockers"]
    for name,disposition in zip(["initial","completion","migration","clear"],expected):
        revision=store.ingest(fixture(name))
        t=perf_counter(); result=brain.assess_retirement("legacy-runner",SCOPE,AT,known_at=AT); times.append((perf_counter()-t)*1000)
        assert result["disposition"]==disposition
        assert result["graph_revision"]==revision
        assert store.ingest(fixture(name))==revision
        if name=="initial":
            assert "monthly-billing" in result["affected_workflows"]
            assert any(e["assertion_id"]=="requires-billing-invoice" for e in result["evidence"])
        if name=="completion": assert any(c["kind"]=="completion_vs_usage" for c in result["conflicts"])
    history=brain.get_history("invoice-export",SCOPE)
    ids={a["id"] for a in history["assertions"]}
    assert {"run-invoice-legacy","run-invoice-v2"}<=ids
    # GRAPH.RO_QUERY must reject graph mutations even with operator credentials.
    with pytest.raises(StoreUnavailable): store.query("CREATE (:Forbidden {id:'mutation'})")
    assert not store.query("MATCH (n:Forbidden) RETURN n")
    # Simulate write failure after staging has begun; old head remains readable.
    before=store.snapshot()[0]
    original=store.query
    def fail_publication(statement,params=None,**kwargs):
        if "MERGE (m:Meta" in statement: raise StoreUnavailable("injected publish failure")
        return original(statement,params,**kwargs)
    store.query=fail_publication
    # Use an actually revoked source in current snapshot.
    current=store.snapshot()[1]
    changed=Bundle(sources=[current.sources[0].model_copy(update={"revoked":True})])
    with pytest.raises(StoreUnavailable): store.ingest(changed)
    store.query=original
    assert store.snapshot()[0]==before
    print("real FalkorDB assessment milliseconds:", times)


def test_persistence_reconnect(store):
    store.ingest(fixture("initial")); before=store.snapshot()[0]
    client=store.db.client
    filename=client.db
    client.save(); client.shutdown()
    from redislite.falkordb_client import FalkorDB
    reopened=FalkorDB(filename)
    store.db=reopened; store.graph=reopened.select_graph(store.graph_name)
    assert store.snapshot()[0]==before
    assert Brain(store).assess_retirement("legacy-runner",SCOPE,AT,known_at=AT)["disposition"]=="blocked"


async def test_real_mcp_tools_and_raw_mock_pipeline(store,monkeypatch):
    monkeypatch.setenv("COMPANY_BRAIN_KNOWN_AT",AT.isoformat())
    from company_brain.extraction import MockExtractor
    from company_brain.server import create_server
    raw=json.loads((ROOT/"data/raw_demo/mock_candidates.json").read_text())
    adapter=MockExtractor({tuple(k.rsplit("@",1)):v for k,v in raw.items()})
    manifest=Bundle.model_validate_json((ROOT/"data/raw_demo/manifest.json").read_text())
    bundle=extract_bundle(manifest,adapter)
    assert all(a.method=="mock" for a in bundle.assertions)
    store.ingest(bundle)
    server=create_server(Brain(store))
    tools=await server.list_tools()
    assert {t.name for t in tools}=={"find_entities","assess_retirement","get_evidence","get_history"}
    assert all(t.annotations.readOnlyHint for t in tools)
    from mcp.shared.memory import create_connected_server_and_client_session
    async with create_connected_server_and_client_session(server) as session:
        listed=await session.list_tools()
        assert len(listed.tools)==4
        assert 'Never override its disposition' in server.instructions
        invalid=await session.call_tool("assess_retirement",{"service_id":"legacy-runner","scope":SCOPE.model_dump(),"planned_at":"2026-10-17T12:00:00"})
        assert invalid.isError
        async def call(name,args):
            response=await session.call_tool(name,args)
            assert not response.isError
            return json.loads(response.content[0].text)
        discovery=await call("find_entities",{"query":"legacy-runner"})
        assert discovery["candidates"][0]["id"]=="legacy-runner"
        assessment=await call("assess_retirement",{"service_id":"legacy-runner","scope":SCOPE.model_dump(),"planned_at":AT.isoformat()})
        assert assessment["disposition"]=="blocked"
        evidence=assessment["evidence"][0]
        passage=await call("get_evidence",{"source_id":evidence["source_id"],"version":evidence["version"],"span_id":evidence["assertion_id"]})
        assert passage["span"]["quote"]==evidence["quote"]
        history=await call("get_history",{"entity_id":"invoice-export","scope":SCOPE.model_dump()})
        assert history["assertions"]


def test_database_reader_acl(store):
    import secrets
    from falkordb import FalkorDB
    store.ingest(fixture("initial"))
    password=secrets.token_hex(24)
    client=store.db.client
    client.acl_setuser("brain_test_reader",enabled=True,passwords=["+"+password],commands=["+graph.ro_query","+info"],keys=[store.graph_name])
    try:
        reader_db=FalkorDB(unix_socket_path=client.connection_pool.connection_kwargs["path"],username="brain_test_reader",password=password,socket_timeout=3)
        reader=FalkorStore(reader_db,store.graph_name)
        assert reader.snapshot()[0]==store.snapshot()[0]
        with pytest.raises(Exception): reader_db.select_graph(store.graph_name).query("CREATE (:Forbidden)")
        with pytest.raises(PermissionError): reader.ingest(fixture("initial"))
        with pytest.raises(PermissionError): reader.reset(store.graph_name)
    finally:
        client.acl_deluser("brain_test_reader")


def test_review_regressions_on_actual_graph(store):
    from test_regressions import restricted_usage_bundle, assert_restricted_coverage, budget_bundle, assert_budget
    store.ingest(restricted_usage_bundle())
    assert_restricted_coverage(store)
    store.reset(store.graph_name)
    store.ingest(budget_bundle())
    assert_budget(store)


def test_graph_native_paths_without_revision_payload_reads(store):
    store.ingest(fixture('initial'))
    original=store.query
    statements=[]
    def checked(statement,params=None,**kwargs):
        assert 'r.payload' not in statement
        assert '$allowed' not in statement
        statements.append(statement)
        return original(statement,params,**kwargs)
    store.query=checked
    result=Brain(store).assess_retirement('legacy-runner',SCOPE,AT,known_at=AT)
    assert any(p['assertion_ids']==['requires-billing-invoice','run-invoice-legacy'] for p in result['dependency_paths'])
    path_queries=[q for q in statements if 'MATCH p=' in q]
    assert len(path_queries)==1
    assert 'SUPERSEDES' in path_queries[0] and 'RETURN p,' in path_queries[0]
    assert any(b['entity_id']=='network-approval' for b in result['blockers'])
    limited=Brain(store,max_results=8).assess_retirement('legacy-runner',SCOPE,AT,known_at=AT)
    evidence={e['assertion_id'] for e in limited['evidence']}
    assert limited['coverage']['truncated']
    for blocker in limited['blockers']:
        assert all(p['assertion_id'] in evidence for p in blocker.get('permissions',[]))
    assert set(limited['affected_workflows'])<={p['consumer_id'] for p in limited['dependency_paths']}


def test_demo_replay_at_future_wallclock_and_historical_projection(store,monkeypatch):
    import company_brain.assessment as module
    from datetime import timedelta
    class Later(datetime):
        @classmethod
        def now(cls,tz=None): return AT+timedelta(days=30)
    monkeypatch.setattr(module,'datetime',Later)
    monkeypatch.setenv('COMPANY_BRAIN_KNOWN_AT',AT.isoformat())
    gold=json.loads((ROOT/'evals/gold/retirement.json').read_text())
    for state in gold['states']:
        store.ingest(fixture(state['fixture']))
        result=Brain(store).assess_retirement('legacy-runner',SCOPE,AT)
        explicit=Brain(store).assess_retirement('legacy-runner',SCOPE,AT,known_at=AT)
        assert result==explicit
        assert result['disposition']==state['disposition']
        legacy=store.query("MATCH (:CurrentEntity {id:'invoice-export'})-[r:RUNS_ON]->(:CurrentEntity {id:'legacy-runner'}) RETURN r.assertion_id")
        if state['fixture'] in {'initial','completion'}: assert legacy==[['run-invoice-legacy']]
        else: assert legacy==[]
        if state['fixture']=='initial':
            assert store.query("MATCH p=(:CurrentEntity {id:'invoice-export'})-[:MIGRATION_TRACKED_BY]->(:CurrentEntity)-[:BLOCKED_BY]->(:CurrentEntity)-[:OWNED_BY]->(:CurrentEntity {id:'security'}) RETURN p")
        assert set(state['required_workflows'])<=set(result['affected_workflows'])
        assert bool(result['coverage']['gaps'])==state['requires_gaps']
    rev=store.snapshot()[0]
    assert store.query('MATCH (e:CurrentEntity) RETURN DISTINCT e.rev')==[[rev]]
    assert store.query('MATCH (e:HistoricalEntity) RETURN count(e)')[0][0]>0
    monkeypatch.delenv('COMPANY_BRAIN_KNOWN_AT')
    assert Brain(store).assess_retirement('legacy-runner',SCOPE,AT)['disposition']=='needs_verification'


def test_additional_question_goldens_and_provider_neutral_harness(store):
    from test_evaluation import verify_questions, ScriptedClient
    from company_brain.evaluation import Experiment, Toolbox, run_pair
    store.ingest(fixture('initial'))
    assert len(verify_questions(Brain(store)))==2
    result=run_pair(ScriptedClient(),Experiment('scripted/offline'),Toolbox(Brain(store),SCOPE,AT),
                    'Who owns invoice export, and why is it still on the old runner?',AT)
    assert result['graph']['revision']==result['search']['revision']
    assert result['graph']['records_digest']==result['search']['records_digest']
    assert all(arm['status']=='completed' for arm in result.values())


def test_search_inventory_privacy_on_actual_graph(store):
    from test_evaluation import hidden_inventory_bundle,check_inventory_privacy
    for hide_service in (False,True):
        store.reset(store.graph_name)
        bundle,secret=hidden_inventory_bundle(hide_service=hide_service)
        store.ingest(bundle)
        check_inventory_privacy(store,secret)


def test_transitive_renewal_lineage_on_actual_graph(store,monkeypatch):
    from test_supersession import renewal_bundle,assert_renewal_chain,assert_history
    monkeypatch.setenv('COMPANY_BRAIN_KNOWN_AT',AT.isoformat())
    for length in (2,3,16):
        store.reset(store.graph_name)
        store.ingest(renewal_bundle(length))
        assert_renewal_chain(store,length)
        assert store.query("MATCH (:CurrentEntity {id:'report-job'})-[r:RUNS_ON]->(:CurrentEntity {id:'legacy-runner'}) RETURN r.assertion_id")==[]
        if length==2: assert_history(store)


def test_transitive_lineage_access_and_revocation_barriers_on_actual_graph(store):
    from test_supersession import barrier_bundle,check_barrier
    for barrier in ('revoked_leaf','revoked_middle','restricted_leaf','restricted_middle','future_recorded','future_recorded_middle','future_effective'):
        store.reset(store.graph_name)
        store.ingest(barrier_bundle(barrier))
        check_barrier(store,barrier)
    # A source revocation affects the new revision, never the immutable old one.
    from test_supersession import renewal_bundle,assessment
    store.reset(store.graph_name)
    before=store.ingest(renewal_bundle())
    source=next(s for s in renewal_bundle().sources if s.id=='renewal-source-1')
    after=store.ingest(Bundle(sources=[source.model_copy(update={'revoked':True})]))
    assert after!=before
    assert assessment(store)['disposition']=='needs_verification'
    historical=store.resolved(before,SCOPE,AT,AT,frozenset({'public'}))
    assert 'renewal-1' in historical and 'run-report-legacy' not in historical
    assert store.dependency_paths(before,'legacy-runner',SCOPE,AT,AT,frozenset({'public'}),8,129)==[]


def test_invalid_renewal_scope_and_depth_preserve_published_graph(store):
    from test_supersession import renewal_bundle
    oversized=renewal_bundle(17)
    baseline=oversized.model_copy(update={
        'sources':[s for s in oversized.sources if not s.id.startswith('renewal-source-')],
        'assertions':[a for a in oversized.assertions if not a.id.startswith('renewal-')]})
    store.ingest(baseline)
    before=store.snapshot()[0]
    renewal=next(a for a in oversized.assertions if a.id=='renewal-1')
    source=next(s for s in oversized.sources if s.key==renewal.source_key)
    invalid=renewal.model_copy(update={'id':'bad-scope-renewal','scope':Scope(environment='staging',region='eu')})
    with pytest.raises(ValueError,match='scope'):
        store.ingest(Bundle(sources=[source],assertions=[invalid]))
    assert store.snapshot()[0]==before
    with pytest.raises(ValueError,match='supersession depth'):
        store.ingest(oversized)
    assert store.snapshot()[0]==before
