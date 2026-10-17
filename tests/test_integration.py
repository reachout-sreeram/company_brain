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


async def test_real_mcp_tools_and_raw_mock_pipeline(store):
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
