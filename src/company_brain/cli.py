"""Operator CLI; paid extraction requires explicit opt-in and environment credentials."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from .assessment import Brain
from .ingestion import extract_bundle, validate_bundle
from .models import Bundle, Scope
from .store import StoreUnavailable, connect
from .extraction import ExtractionError


def load(path):
    return Bundle.model_validate_json(Path(path).read_text())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest="command",required=True)
    validate=commands.add_parser("validate"); validate.add_argument("path")
    ingest=commands.add_parser("ingest"); ingest.add_argument("path")
    reset=commands.add_parser("reset"); reset.add_argument("--confirm-graph",required=True)
    assess=commands.add_parser("assess"); assess.add_argument("service_id"); assess.add_argument("--environment",required=True); assess.add_argument("--region",required=True); assess.add_argument("--planned-at",required=True); assess.add_argument("--known-at")
    history=commands.add_parser("history"); history.add_argument("entity_id"); history.add_argument("--environment",required=True); history.add_argument("--region",required=True)
    extract=commands.add_parser("extract-ingest"); extract.add_argument("manifest"); extract.add_argument("--mock-candidates"); extract.add_argument("--allow-paid-api",action="store_true"); extract.add_argument("--model"); extract.add_argument("--max-tokens",type=int,default=2048)
    proposals=commands.add_parser('proposals');proposals.add_argument('path')
    approve=commands.add_parser('approve-proposals');approve.add_argument('path')
    approve.add_argument('--proposal',action='append',required=True)
    approve.add_argument('--actor',required=True);approve.add_argument('--reviewed-at',required=True)
    approve.add_argument('--note',required=True);approve.add_argument('--demonstration',action='store_true')
    approve.add_argument('--output',required=True)
    audits=commands.add_parser('review-history');audits.add_argument('path')
    args=parser.parse_args()
    try:
        if args.command=='proposals':
            from .review import list_proposals
            result={'proposals':list_proposals(load(args.path))}
        elif args.command=='review-history':
            bundle=load(args.path);validate_bundle(bundle)
            result={'reviews':[r.model_dump(mode='json') for r in bundle.reviews]}
        elif args.command=='approve-proposals':
            from .review import approve_proposals
            bundle,review=approve_proposals(load(args.path),args.proposal,actor=args.actor,
                reviewed_at=datetime.fromisoformat(args.reviewed_at),note=args.note,demonstration=args.demonstration)
            with Path(args.output).open('x') as output: output.write(bundle.model_dump_json(indent=2))
            result={'output':args.output,'review':review.model_dump(mode='json'),'revision':bundle.revision}
        elif args.command=="validate":
            bundle=load(args.path); validate_bundle(bundle); result={"valid":True,"revision":bundle.revision}
        elif args.command=="ingest":
            result={"graph_revision":connect(writable=True).ingest(load(args.path))}
        elif args.command=="reset":
            store=connect(writable=True); store.reset(args.confirm_graph); result={"reset":store.graph_name}
        elif args.command=="extract-ingest":
            from .extraction import MockExtractor, OpenRouterExtractor, OpenRouterConfig
            import os
            if args.mock_candidates:
                if args.allow_paid_api or args.model:
                    raise ValueError("choose explicit mock or paid extraction")
                raw=json.loads(Path(args.mock_candidates).read_text())
                adapter=MockExtractor({tuple(k.rsplit("@",1)):v for k,v in raw.items()})
            else:
                if not args.allow_paid_api or not args.model:
                    raise ValueError("live extraction needs --allow-paid-api, --model and securely configured OPENROUTER_API_KEY")
                adapter=OpenRouterExtractor(OpenRouterConfig(model=args.model,api_key=os.getenv("OPENROUTER_API_KEY",""),allow_live=True,max_output_tokens=args.max_tokens))
            bundle=extract_bundle(load(args.manifest),adapter)
            result={"graph_revision":connect(writable=True).ingest(bundle),"extraction_method":adapter.method}
        else:
            brain=Brain(connect())
            scope=Scope(environment=args.environment,region=args.region)
            if args.command=="history": result=brain.get_history(args.entity_id,scope)
            else: result=brain.assess_retirement(args.service_id,scope,datetime.fromisoformat(args.planned_at),known_at=datetime.fromisoformat(args.known_at) if args.known_at else None)
        print(json.dumps(result,indent=2))
    except (ValueError,OSError,StoreUnavailable,PermissionError,ExtractionError) as exc:
        # Provider/DB errors are already sanitized; never print config or credentials.
        if isinstance(exc,ExtractionError): message=str(exc)
        elif isinstance(exc,StoreUnavailable): message=str(exc)
        else: message="Input or operation rejected; check source validation, graph name and command options"
        print(message,file=sys.stderr)
        return 1
    return 0


if __name__=="__main__":
    raise SystemExit(main())
