"""Explicit operator review; no model chooses selections, identity or review time."""
from hashlib import sha256
import json
from .ingestion import claim_digest,validate_bundle
from .models import ProposalReview,ReviewSelection,aware


def list_proposals(bundle):
    validate_bundle(bundle)
    approved={s.proposal_id for r in bundle.reviews for s in r.selections}
    return [{'proposal_id':a.id,'already_approved':a.id in approved,'source_key':a.source_key,
             'source_hash':next(s.content_hash for s in bundle.sources if s.key==a.source_key),
             'claim_digest':claim_digest(a),'claim':a.model_dump(mode='json')}
            for a in bundle.assertions if a.status=='proposal']


def approve_proposals(bundle,proposal_ids,*,actor,reviewed_at,note,demonstration=False):
    validate_bundle(bundle);reviewed_at=aware(reviewed_at)
    if not proposal_ids or len(proposal_ids)!=len(set(proposal_ids)):
        raise ValueError('select unique proposal IDs explicitly')
    if not actor.strip() or not note.strip(): raise ValueError('actor and source-validation note are required')
    proposals={a.id:a for a in bundle.assertions if a.status=='proposal'}
    already={s.proposal_id for r in bundle.reviews for s in r.selections}
    if any(i not in proposals or i in already for i in proposal_ids): raise ValueError('unknown or previously approved proposal')
    metadata={'input_revision':bundle.revision,'actor':actor,'actor_kind':'demonstration' if demonstration else 'operator',
              'reviewed_at':reviewed_at.isoformat(),'proposal_ids':sorted(proposal_ids),'note':note}
    review_id='review-'+sha256(json.dumps(metadata,sort_keys=True).encode()).hexdigest()[:24]
    selections=[];approved=[]
    for ident in sorted(proposal_ids):
        proposal=proposals[ident]
        approved_id='approved-'+sha256((review_id+ident).encode()).hexdigest()[:24]
        selections.append(ReviewSelection(proposal_id=ident,approved_id=approved_id,
            source_key=proposal.source_key,claim_digest=claim_digest(proposal)))
        approved.append(proposal.model_copy(update={'id':approved_id,'status':'approved','approval_id':review_id,'approval_kind':metadata['actor_kind'],'approved_at':reviewed_at}))
    review=ProposalReview(id=review_id,actor=actor,actor_kind=metadata['actor_kind'],reviewed_at=reviewed_at,
        input_revision=bundle.revision,selections=selections,note=note)
    result=bundle.model_copy(update={'assertions':[*bundle.assertions,*approved],'reviews':[*bundle.reviews,review]})
    validate_bundle(result)
    return result,review
