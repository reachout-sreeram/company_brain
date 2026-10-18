"""Selected operator review, immutable proposals, knowledge time and real graph audit."""
from datetime import timedelta
import json,sys
from pathlib import Path
import pytest
from company_brain.models import Bundle
from company_brain.ingestion import extract_bundle,validate_bundle,merge_bundle
from company_brain.extraction import MockExtractor
from company_brain.review import approve_proposals,list_proposals
from company_brain.assessment import Brain
from test_assessment import NOW,SCOPE,InMemoryAssessmentTestDouble

ROOT=Path(__file__).parents[1]


def pending_bundle():
    manifest=Bundle.model_validate_json((ROOT/'data/raw_demo/manifest.json').read_text())
    manifest=manifest.model_copy(update={'sources':[s.model_copy(update={'reviewed_claims':[]}) for s in manifest.sources]})
    raw=json.loads((ROOT/'data/raw_demo/mock_candidates.json').read_text())
    return extract_bundle(manifest,MockExtractor({tuple(k.rsplit('@',1)):v for k,v in raw.items()}))


def reviewed(bundle=None):
    bundle=bundle or pending_bundle()
    selected=[a.id for a in bundle.assertions if a.subject_id=='invoice-export' and a.predicate in {'RUNS_ON','OWNED_BY'}]
    return approve_proposals(bundle,selected,actor='demo:source-validation',reviewed_at=NOW+timedelta(hours=1),
                             demonstration=True,note='Synthetic demonstration: selected exact scoped runtime and roster quotes checked against source. Not human acceptance.')


def test_selected_review_preserves_proposals_and_source_versions_with_audit():
    before=pending_bundle();after,event=reviewed(before)
    assert len(event.selections)==2 and event.actor_kind=='demonstration'
    assert event.input_revision==before.revision and event.actor.startswith('demo:')
    assert after.sources==before.sources and all(a in after.assertions for a in before.assertions)
    assert len(after.assertions)==len(before.assertions)+2
    assert len([r for r in list_proposals(after) if r['already_approved']])==2
    for selected in event.selections:
        approved=next(a for a in after.assertions if a.id==selected.approved_id)
        assert approved.approval_id==event.id and approved.source_key==selected.source_key
    validate_bundle(after)


def test_reviewed_fact_changes_answer_only_after_explicit_review_knowledge_time():
    before=pending_bundle();after,event=reviewed(before)
    def assess(bundle,known):return Brain(InMemoryAssessmentTestDouble(bundle)).assess_retirement('legacy-runner',SCOPE,known,known_at=known)
    assert assess(before,event.reviewed_at)['disposition']=='needs_verification'
    assert assess(after,NOW)['disposition']=='needs_verification'
    assert assess(after,event.reviewed_at)['disposition']=='blocked'


@pytest.mark.parametrize('mutation',['missing_audit','wrong_source','changed_claim','backdate','repeat','fake_human'])
def test_review_cannot_silently_promote_tamper_backdate_or_reapprove(mutation):
    before=pending_bundle();after,event=reviewed(before)
    if mutation=='repeat':
        with pytest.raises(ValueError,match='previously approved'):reviewed(after)
        return
    if mutation=='fake_human':
        with pytest.raises(ValueError,match='demo:'):
            approve_proposals(before,[before.assertions[0].id],actor='Saketh',reviewed_at=NOW,demonstration=True,note='bad attribution')
        return
    if mutation=='missing_audit': changed=after.model_copy(update={'reviews':[]})
    elif mutation=='wrong_source':
        sel=event.selections[0].model_copy(update={'source_key':'wrong@1'})
        changed=after.model_copy(update={'reviews':[event.model_copy(update={'selections':[sel,*event.selections[1:]]})]})
    elif mutation=='changed_claim':
        changed=after.model_copy(update={'assertions':[a.model_copy(update={'subject_id':'report-job'}) if a.id==event.selections[0].approved_id else a for a in after.assertions]})
    else:
        with pytest.raises(ValueError,match='predates source'):
            approve_proposals(before,[before.assertions[0].id],actor='demo:test',reviewed_at=NOW-timedelta(days=100),demonstration=True,note='invalid historic review')
        return
    with pytest.raises(ValueError): validate_bundle(changed)


def test_review_audit_identity_is_immutable_on_merge():
    after,event=reviewed()
    with pytest.raises(ValueError,match='immutable identity'):
        merge_bundle(after,Bundle(reviews=[event.model_copy(update={'note':'rewritten'})]))


def test_cli_selected_approval_is_explicit_and_cannot_overwrite(tmp_path,monkeypatch,capsys):
    from company_brain.cli import main
    before=pending_bundle();source=tmp_path/'pending.json';output=tmp_path/'approved.json'
    source.write_text(before.model_dump_json())
    selected=next(a.id for a in before.assertions if a.predicate=='RUNS_ON')
    argv=['brain','approve-proposals',str(source),'--proposal',selected,'--actor','demo:cli',
          '--reviewed-at',(NOW+timedelta(hours=1)).isoformat(),'--note','Synthetic source validation demonstration',
          '--demonstration','--output',str(output)]
    monkeypatch.setattr(sys,'argv',argv);assert main()==0
    original=output.read_bytes();assert b'demonstration' in original
    assert main()==1 and output.read_bytes()==original
    assert source.read_text()==before.model_dump_json()


@pytest.mark.integration
@pytest.mark.skipif(__import__('os').getenv('COMPANY_BRAIN_INTEGRATION')!='1',reason='actual FalkorDB opt-in')
def test_actual_graph_keeps_review_edges_and_historical_cutoff(tmp_path):
    from redislite.falkordb_client import FalkorDB
    from company_brain.store import FalkorStore
    db=FalkorDB(str(tmp_path/'review.rdb'));store=FalkorStore(db,'company_brain_test_review',writable=True)
    try:
        before=pending_bundle();after,event=reviewed(before)
        rev_before=store.ingest(before)
        assert Brain(store).assess_retirement('legacy-runner',SCOPE,event.reviewed_at,known_at=event.reviewed_at)['disposition']=='needs_verification'
        rev_after=store.ingest(after)
        assert rev_before!=rev_after
        assert Brain(store).assess_retirement('legacy-runner',SCOPE,NOW,known_at=NOW)['disposition']=='needs_verification'
        result=Brain(store).assess_retirement('legacy-runner',SCOPE,event.reviewed_at,known_at=event.reviewed_at)
        assert result['disposition']=='blocked'
        assert {e['approval_id'] for e in result['evidence']}=={event.id}
        assert store.query('MATCH (:ProposalReview {rev:$rev})-[:APPROVES]->(a)-[:REVIEWED_FROM]->(p) RETURN count(a)',{'rev':rev_after})==[[2]]
        assert store.snapshot()[1].reviews==after.reviews
    finally:db.client.shutdown()
