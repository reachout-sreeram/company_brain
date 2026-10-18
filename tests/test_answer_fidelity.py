"""Returned-packet fidelity, not golden-answer normalization."""
import pytest
from company_brain.evaluation import RetrievedReferences
from test_evaluation import toolbox,assessment_answer,empty_answer
from test_assessment import NOW,SCOPE


def packet_registry(max_results=128):
    tools=toolbox();tools.brain.max_results=max_results
    packet=tools.call('graph','assess_retirement',{'service_id':'legacy-runner','scope':SCOPE.model_dump(),'planned_at':NOW.isoformat()})
    refs=RetrievedReferences(tools.search.entities);refs.collect(packet)
    return packet,refs


def test_complete_scoped_packet_is_accepted_without_golden_lookup():
    packet,refs=packet_registry()
    assert refs.validate(assessment_answer(packet))==[]


def test_blocker_target_is_not_an_extra_assessment_blocker():
    packet,refs=packet_registry();answer=assessment_answer(packet)
    answer['blocker_entities'].append(packet['service_id'])
    error=next(e for e in refs.validate(answer) if e['code']=='assessment_field_mismatch')
    assert error['field']=='blocker_entities' and error['value']['extra']==[packet['service_id']]


def test_omitted_bridge_evidence_from_returned_packet_is_rejected():
    packet,refs=packet_registry();answer=assessment_answer(packet)
    bridge=next(e['assertion_id'] for e in packet['evidence'] if e['assertion_id'] not in {i for p in packet['dependency_paths'] for i in p['assertion_ids']})
    answer['evidence_ids'].remove(bridge)
    answer['source_references']=[r for r in answer['source_references'] if r['assertion_id']!=bridge]
    assert {'code':'missing_returned_evidence','field':'evidence_ids','value':[bridge]} in refs.validate(answer)


@pytest.mark.parametrize('field',['affected_workflows','blocker_entities','owner_pairs','decisions'])
def test_reported_assessment_fields_cannot_drop_returned_findings(field):
    packet,refs=packet_registry();answer=assessment_answer(packet)
    assert answer[field]
    answer[field]=[]
    assert any(e['code']=='assessment_field_mismatch' and e['field']==field for e in refs.validate(answer))


def test_truncated_packet_never_requires_unreturned_evidence():
    packet,refs=packet_registry(1)
    assert packet['coverage']['truncated']
    assert len(packet['evidence'])<=1
    assert refs.validate(assessment_answer(packet))==[]


def test_record_method_requires_cited_role_support_not_just_mentioned_entity():
    tools=toolbox();record=tools.search.read_record('source-run-invoice-legacy@1')
    row=record['record']['assertions'][0]
    refs=RetrievedReferences(tools.search.entities);refs.collect(record)
    answer=empty_answer('blocked');answer.update(evidence_ids=[row['id']],
        source_references=[{'assertion_id':row['id'],'source_key':row['source_id']+'@'+row['source_version']}],
        blocker_entities=[row['object_id']])
    assert any(e['code']=='unsupported_finding_role' for e in refs.validate(answer))
    answer['blocker_entities']=[row['subject_id']]
    assert refs.validate(answer)==[]
    answer['evidence_ids']=[];answer['source_references']=[]
    assert any(e['code']=='uncited_finding_support' for e in refs.validate(answer))
