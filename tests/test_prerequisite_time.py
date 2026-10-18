"""Explicit contract validity is distinct from current observed runtime usage."""
from datetime import timedelta
import pytest
from company_brain.assessment import Brain
from company_brain.extraction import raw_source,validate_candidates,ExtractionError
from company_brain.ingestion import validate_bundle
from test_assessment import scenario,NOW,SCOPE,InMemoryAssessmentTestDouble


def validity_bundle(start=None,end=None):
    b=scenario();a=next(a for a in b.assertions if a.predicate=='REQUIRES')
    start=start or NOW-timedelta(days=60)
    source=next(s for s in b.sources if s.key==a.source_key)
    source=source.model_copy(update={'requires_valid_from':start,'requires_valid_until':end})
    changed=a.model_copy(update={'time_basis':'validity','observed_at':None,'effective_from':start,'effective_until':end})
    b=b.model_copy(update={'sources':[source if s.key==source.key else s for s in b.sources],
                          'assertions':[changed if old.id==a.id else old for old in b.assertions]})
    validate_bundle(b)
    return b,changed


def test_validity_prerequisite_does_not_expire_as_runtime_observation():
    b,a=validity_bundle()
    result=Brain(InMemoryAssessmentTestDouble(b)).assess_retirement('legacy-runner',SCOPE,NOW,known_at=NOW)
    assert 'monthly-billing' in result['affected_workflows']
    assert not any('stale dependency evidence: monthly-billing'==g for g in result['coverage']['gaps'])
    assert result['disposition']=='blocked'


def test_explicit_future_contract_can_apply_to_future_planned_time_but_not_before_validity():
    start=NOW+timedelta(days=2);end=NOW+timedelta(days=10);b,a=validity_bundle(start,end)
    brain=Brain(InMemoryAssessmentTestDouble(b))
    before=brain.assess_retirement('legacy-runner',SCOPE,NOW,known_at=NOW)
    later=brain.assess_retirement('legacy-runner',SCOPE,start,known_at=NOW)
    expired=brain.assess_retirement('legacy-runner',SCOPE,end,known_at=NOW)
    assert 'monthly-billing' not in before['affected_workflows']
    assert 'monthly-billing' in later['affected_workflows']
    assert 'monthly-billing' not in expired['affected_workflows']


def test_undated_runtime_and_undeclared_requirement_cannot_become_validity_or_now():
    b=scenario()
    for predicate in ('RUNS_ON','DEPENDS_ON','REQUIRES'):
        original=next((a for a in b.assertions if a.predicate==predicate),None)
        if not original: continue
        bad=original.model_copy(update={'observed_at':None})
        with pytest.raises(ValueError,match='observation time'):
            validate_bundle(b.model_copy(update={'assertions':[bad if a.id==bad.id else a for a in b.assertions]}))
        bad=bad.model_copy(update={'time_basis':'validity'})
        with pytest.raises(ValueError,match='validity'):
            validate_bundle(b.model_copy(update={'assertions':[bad if a.id==bad.id else a for a in b.assertions]}))


def test_extraction_uses_declared_prerequisite_interval_without_inventing_observation():
    b,a=validity_bundle();source=next(s for s in b.sources if s.key==a.source_key)
    payload={'assertions':[{'subject_id':a.subject_id,'predicate':'REQUIRES','object_id':a.object_id,
        'value':None,'target_service_id':None,'quote':a.quote,'effective_from':None,
        'effective_until':None,'observed_at':None,'time_basis':None}]}
    candidate=validate_candidates(raw_source(source,b.entities),payload)[0]
    assert candidate.time_basis=='validity' and candidate.observed_at is None
    assert candidate.effective_from==source.requires_valid_from.isoformat()
    assert candidate.effective_from!=NOW.isoformat()
    payload['assertions'][0]['effective_from']=(NOW+timedelta(days=5)).isoformat()
    with pytest.raises(ExtractionError,match='disagrees'):
        validate_candidates(raw_source(source,b.entities),payload)


def test_missing_validity_metadata_and_dates_is_quarantined_not_filled_from_record_time():
    b=scenario();a=next(a for a in b.assertions if a.predicate=='REQUIRES');source=next(s for s in b.sources if s.key==a.source_key)
    with pytest.raises(ExtractionError,match='explicit source dates'):
        validate_candidates(raw_source(source,b.entities),{'assertions':[{'subject_id':a.subject_id,'predicate':'REQUIRES','object_id':a.object_id,
            'quote':a.quote,'effective_from':None,'observed_at':None,'time_basis':'validity'}]})


@pytest.mark.integration
@pytest.mark.skipif(__import__('os').getenv('COMPANY_BRAIN_INTEGRATION')!='1',reason='actual FalkorDB opt-in')
def test_actual_cypher_validity_interval_and_observation_freshness_remain_distinct(tmp_path):
    from redislite.falkordb_client import FalkorDB
    from company_brain.store import FalkorStore
    db=FalkorDB(str(tmp_path/'validity.rdb'));store=FalkorStore(db,'company_brain_test_validity',writable=True)
    try:
        b,a=validity_bundle(NOW+timedelta(days=2),NOW+timedelta(days=10));store.ingest(b)
        brain=Brain(store)
        result=brain.assess_retirement('legacy-runner',SCOPE,NOW+timedelta(days=2),known_at=NOW)
        assert 'monthly-billing' in result['affected_workflows']
        assert any(e['time_basis']=='validity' and e['observed_at'] is None for e in result['evidence'])
        assert 'monthly-billing' not in brain.assess_retirement('legacy-runner',SCOPE,NOW,known_at=NOW)['affected_workflows']
        late=brain.assess_retirement('legacy-runner',SCOPE,NOW+timedelta(days=30),known_at=NOW+timedelta(days=30))
        # Independent open migration prerequisites still block; stale runtime never becomes clearance.
        assert late['disposition']=='blocked'
        assert not any(path['fresh'] for path in late['dependency_paths'])
        assert any('stale dependency evidence' in g for g in late['coverage']['gaps'])
    finally:db.client.shutdown()


def test_future_recording_cannot_make_a_known_future_contract_available_early():
    b,a=validity_bundle(NOW+timedelta(days=2),NOW+timedelta(days=4))
    b=b.model_copy(update={'sources':[s.model_copy(update={'recorded_at':NOW+timedelta(hours=1)}) if s.key==a.source_key else s for s in b.sources]})
    validate_bundle(b)
    result=Brain(InMemoryAssessmentTestDouble(b)).assess_retirement('legacy-runner',SCOPE,NOW+timedelta(days=2),known_at=NOW)
    assert 'monthly-billing' not in result['affected_workflows']


def test_live_extraction_never_activates_even_a_matching_pre_reviewed_mock_digest():
    import json
    from pathlib import Path
    from company_brain.models import Bundle
    from company_brain.extraction import MockExtractor
    from company_brain.ingestion import extract_bundle
    root=Path(__file__).parents[1]
    b=Bundle.model_validate_json((root/'data/raw_demo/manifest.json').read_text())
    raw=json.loads((root/'data/raw_demo/mock_candidates.json').read_text())
    fixtures=MockExtractor({tuple(k.rsplit('@',1)):v for k,v in raw.items()})
    class LiveContractAdapter:
        method='extracted'
        def extract(self,source):return fixtures.extract(source)
    pending=extract_bundle(b,LiveContractAdapter())
    assert pending.assertions and all(a.status=='proposal' for a in pending.assertions)
    assert not pending.reviews
