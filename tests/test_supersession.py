"""Rereview regressions: renewal lineage, temporal history and access barriers."""
from datetime import timedelta
from hashlib import sha256
import json

import pytest

from company_brain.assessment import Brain
from company_brain.ingestion import validate_bundle
from company_brain.models import Caller, Scope
from test_assessment import NOW, SCOPE, InMemoryAssessmentTestDouble, scenario


def renewal_bundle(length=2):
    b=scenario('completion','migration','clear')
    old=next(a for a in b.assertions if a.id=='clear-report')
    template=next(s for s in b.sources if s.key==old.source_key)
    original=old.model_copy(update={'effective_until':NOW})
    sources=list(b.sources)
    assertions=[original if a.id==old.id else a for a in b.assertions]
    prior=original
    for i in range(1,length):
        observed=NOW-timedelta(seconds=(length-i)*30)
        text=template.text.replace('11:30:00Z',observed.strftime('%H:%M:%SZ'))
        source=template.model_copy(update={'id':f'renewal-source-{i}','text':text,
            'content_hash':sha256(text.encode()).hexdigest(),'recorded_at':observed+timedelta(seconds=5)})
        current=old.model_copy(update={'id':f'renewal-{i}','source_id':source.id,
            'effective_from':observed,'observed_at':observed,'supersedes':[prior.id],
            'effective_until':NOW if i<length-1 else None,'quote':text,'span_end':len(text)})
        sources.append(source); assertions.append(current); prior=current
    return b.model_copy(update={'sources':sources,'assertions':assertions})


def barrier_bundle(barrier):
    b=renewal_bundle()
    target=next(a for a in b.assertions if a.id==('clear-report' if barrier.endswith('middle') else 'renewal-1'))
    if barrier.startswith('revoked') or barrier.startswith('restricted'):
        update={'revoked':True} if barrier.startswith('revoked') else {'visibility':'restricted'}
        return b.model_copy(update={'sources':[s.model_copy(update=update) if s.key==target.source_key else s for s in b.sources]})
    if barrier.startswith('future_recorded'):
        return b.model_copy(update={'sources':[s.model_copy(update={'recorded_at':NOW+timedelta(minutes=1)}) if s.key==target.source_key else s for s in b.sources]})
    if barrier=='future_effective':
        return b.model_copy(update={'assertions':[a.model_copy(update={'effective_from':NOW+timedelta(minutes=1)}) if a.id==target.id else a for a in b.assertions]})
    raise AssertionError('unknown test barrier')


def assessment(store,*,planned=NOW,known=NOW,groups=frozenset({'public'})):
    return Brain(store,Caller(groups=groups)).assess_retirement('legacy-runner',SCOPE,planned,known_at=known)


def assert_renewal_chain(store,length):
    result=assessment(store)
    assert result['disposition']=='no_known_blockers',result['coverage']
    assert result['dependency_paths']==[]
    assert result['affected_workflows']==[]
    ids={e['assertion_id'] for e in result['evidence']}
    assert f'renewal-{length-1}' in ids
    assert 'run-report-legacy' not in ids and 'clear-report' not in ids
    history=Brain(store).get_history('report-job',SCOPE)
    assert {'run-report-legacy','clear-report',f'renewal-{length-1}'}<={a['id'] for a in history['assertions']}


@pytest.mark.parametrize('length',[2,3,16])
def test_expired_intermediates_do_not_resurrect_old_usage(length):
    b=renewal_bundle(length); validate_bundle(b)
    assert_renewal_chain(InMemoryAssessmentTestDouble(b),length)


def assert_history(store):
    # The original clearance was valid then; a later renewal cannot rewrite it.
    historical=assessment(store,planned=NOW-timedelta(minutes=20),known=NOW-timedelta(minutes=15))
    assert historical['disposition']=='no_known_blockers'
    assert 'clear-report' in {e['assertion_id'] for e in historical['evidence']}
    assert 'renewal-1' not in json.dumps(historical)
    # At noon the original has expired; an as-yet unrecorded renewal is unavailable.
    earlier_knowledge=assessment(store,known=NOW-timedelta(seconds=26))
    assert earlier_knowledge['disposition']=='needs_verification'
    assert any(p['consumer_id']=='report-job' for p in earlier_knowledge['dependency_paths'])
    assert 'renewal-1' not in json.dumps(earlier_knowledge)
    assert assessment(store)['disposition']=='no_known_blockers'


def test_known_at_and_historical_intervals_preserve_prior_state():
    assert_history(InMemoryAssessmentTestDouble(renewal_bundle()))


@pytest.mark.parametrize('barrier',['revoked_leaf','revoked_middle','restricted_leaf','restricted_middle','future_recorded','future_recorded_middle','future_effective'])
def test_inaccessible_revoked_or_future_chain_members_do_not_erase_usage(barrier):
    b=barrier_bundle(barrier); validate_bundle(b)
    check_barrier(InMemoryAssessmentTestDouble(b),barrier)


def check_barrier(store,barrier):
    planned=NOW+timedelta(minutes=2) if barrier=='future_effective' else NOW
    result=assessment(store,planned=planned)
    assert result['disposition']=='needs_verification',result['coverage']
    assert any(p['consumer_id']=='report-job' for p in result['dependency_paths'])
    if barrier.startswith('restricted'):
        private_id='clear-report' if barrier.endswith('middle') else 'renewal-1'
        private_source='source-clear-report' if barrier.endswith('middle') else 'renewal-source-1'
        assert private_id not in json.dumps(result)
        assert private_source not in json.dumps(result)
        assert 'assessment coverage is incomplete for this caller' in result['coverage']['gaps']
        from company_brain.evaluation import RecordSearch
        assert private_id not in json.dumps(RecordSearch(Brain(store),SCOPE,NOW).records)
        allowed=assessment(store,groups=frozenset({'public','restricted'}))
        assert allowed['disposition']=='no_known_blockers'


def test_expired_clearance_without_current_renewal_does_not_grant_clearance():
    b=renewal_bundle()
    b=b.model_copy(update={'assertions':[a for a in b.assertions if a.id!='renewal-1']})
    result=assessment(InMemoryAssessmentTestDouble(b))
    assert result['disposition']=='needs_verification'
    assert any(p['consumer_id']=='report-job' for p in result['dependency_paths'])


def test_gap_between_clearances_is_not_retroactively_cleared():
    b=renewal_bundle()
    b=b.model_copy(update={'assertions':[a.model_copy(update={'effective_until':NOW-timedelta(minutes=20)}) if a.id=='clear-report' else a for a in b.assertions]})
    validate_bundle(b)
    during_gap=assessment(InMemoryAssessmentTestDouble(b),planned=NOW-timedelta(minutes=10))
    assert during_gap['disposition']=='needs_verification'
    assert assessment(InMemoryAssessmentTestDouble(b))['disposition']=='no_known_blockers'


@pytest.mark.parametrize('field,value',[
    ('scope',Scope(environment='staging',region='eu')),
    ('target_service_id','runner-v2'),
    ('subject_id','invoice-export'),
])
def test_renewal_cannot_cross_scope_target_or_subject(field,value):
    b=renewal_bundle()
    b=b.model_copy(update={'assertions':[a.model_copy(update={field:value}) if a.id=='renewal-1' else a for a in b.assertions]})
    with pytest.raises(ValueError): validate_bundle(b)


def test_supersession_limit_rejects_longer_chain_instead_of_silently_ignoring_it():
    with pytest.raises(ValueError,match='supersession depth'):
        validate_bundle(renewal_bundle(17))
