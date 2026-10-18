"""Explicit USD-3-approved synthetic OpenRouter run; never runs on import.

Only the named project .env.local may provide a process-memory credential.
Raw model answers are evidence of this harness, not an external MCP client UI.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shlex
import subprocess
from time import perf_counter

from .assessment import Brain
from .evaluation import Experiment,Toolbox,run_arm,score_answer,score_narrative
from .extraction import RawSource,OpenRouterExtractor,ExtractionError,raw_source
from .ingestion import extract_bundle
from .models import Bundle,Scope
from .openrouter import (LUNA_MODEL,OpenRouterConfig,OpenRouterError,OpenRouterSession,
                         OpenRouterEvaluationClient,SpendLedger)
from .store import FalkorStore,StoreUnavailable

GRAPH='company_brain_demo_live_evaluation'
PROTOCOL_REVISION='native-function-calls-v4-exact-references'
CASES=('initial','completion','migration','clear','invoice-owner-rationale','network-slip-billing')


def load_named_credential(root):
    path=root/'.env.local'
    if not path.is_file() or path.is_symlink(): raise OpenRouterError('named project .env.local is unavailable')
    ignored=subprocess.run(['git','check-ignore','--quiet','--','.env.local'],cwd=root,
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
    tracked=subprocess.run(['git','ls-files','--error-unmatch','--','.env.local'],cwd=root,
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
    if not ignored or tracked: raise OpenRouterError('named credential file must be ignored and untracked')
    try:
        matches=[]
        for line in path.read_text().splitlines():
            line=line.strip()
            if line.startswith('export '): line=line[7:].lstrip()
            name,separator,value=line.partition('=')
            if separator and name.strip() in {'OPENROUTER_API_KEY','OPEN_ROUTER'}:
                tokens=shlex.split(value,comments=True,posix=True)
                if len(tokens)!=1 or not tokens[0]: raise ValueError('invalid named credential')
                matches.append(tokens[0])
        if len(matches)!=1: raise ValueError('expected one named credential')
        return matches[0]
    except (OSError,ValueError):
        raise OpenRouterError('named credential is missing or malformed; value withheld') from None


def redact(value,key):
    if isinstance(value,str): return value.replace(key,'[REDACTED]')
    if isinstance(value,list): return [redact(x,key) for x in value]
    if isinstance(value,dict): return {redact(k,key):redact(v,key) for k,v in value.items()}
    return value


def checked_final(body):
    try:
        choice=body['choices'][0]
        if choice['finish_reason']!='stop': raise ValueError('incomplete')
        return json.loads(choice['message']['content'])
    except (KeyError,IndexError,TypeError,ValueError):
        raise OpenRouterError('smoke output malformed or incomplete') from None


def archive_report(output):
    """Keep prior evidence byte-for-byte before another authorized run."""
    if not output.exists(): return None
    for number in range(1,10000):
        archive=output.with_name(f'{output.stem}-archive-{number}{output.suffix}')
        try:
            with archive.open('x') as target: target.write(output.read_text())
            return archive.name
        except FileExistsError: continue
    raise OpenRouterError('report archive slots exhausted')


def resume_comparison(previous,archive):
    if previous.get('model')!=LUNA_MODEL or not previous.get('smoke',{}).get('passed'):
        raise OpenRouterError('comparison resume requires a successful same-model smoke report')
    report=dict(previous)
    report.pop('error',None)
    report.update(status='not_started',evaluations=[],protocol_revision=PROTOCOL_REVISION,
                  previous_protocol_attempt=archive)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-approved-usd3',action='store_true',required=True)
    parser.add_argument('--confirm-graph',required=True)
    parser.add_argument('--comparison-only',action='store_true')
    parser.add_argument('--cases',nargs='+',choices=CASES,help='Explicit paired subset; only with --comparison-only')
    args=parser.parse_args()
    if args.cases and not args.comparison_only: parser.error('--cases requires --comparison-only')
    if args.confirm_graph!=GRAPH: parser.error('confirm the exact isolated live-evaluation demo graph')
    root=Path(__file__).resolve().parents[2]
    output=root/'evals/results/live-openrouter.json'
    key=None
    report={'model':LUNA_MODEL,'cap_usd':'3','status':'not_started','smoke':None,
            'extraction':[],'narrative':[],'evaluations':[],
            'protocol_revision':PROTOCOL_REVISION,
            'limits':'Small synthetic run; no customer or production validation; native OpenRouter function-call harness over read-only tools, not an external MCP client UI.'}
    if args.comparison_only:
        previous=json.loads(output.read_text())
        report=resume_comparison(previous,archive_report(output))
    else:
        archive_report(output)
    report['selected_cases']=list(dict.fromkeys(args.cases or CASES))
    report['implementation_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    report['comparison_controls']={'output_tokens':1500,'turns':20,'tool_calls':12,'context_bytes':65536,
        'max_empty_retries':2,'max_final_repairs':2,'temperature':None,'reasoning_effort':'none'}
    database=None
    session=None
    ledger=SpendLedger(root/'.local/openrouter-budget.json')
    def save():
        report['ledger']=ledger.snapshot()
        if session is not None: report['provider_responses']=session.responses
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(redact(report,key) if key else report,indent=2))
    try:
        key=load_named_credential(root)
        config=OpenRouterConfig(model=LUNA_MODEL,api_key=key,allow_live=True,max_output_tokens=1500,max_attempts=1,timeout_seconds=120)
        session=OpenRouterSession(config,ledger=ledger)
        if not args.comparison_only:
            start=perf_counter()
            body=session.complete([{'role':'system','content':'Return only a JSON object with ok set to true.'},
                                   {'role':'user','content':'OpenRouter connectivity test for synthetic evaluation.'}],max_output_tokens=128)
            if checked_final(body)!={'ok':True}: raise OpenRouterError('smoke response did not match expected JSON')
            report['smoke']={'passed':True,'latency_ms':(perf_counter()-start)*1000,'generation_id':body.get('id'),
                             'model':body.get('model'),'usage':body['usage']}
            report['status']='smoke_passed'; save()
            print(json.dumps({'milestone':'smoke','passed':True,'actual_usd':ledger.snapshot()['actual_usd']}),flush=True)
        # Actual FalkorDB only, on newly named isolated demo graphs.
        from redislite.falkordb_client import FalkorDB
        database=FalkorDB(str(root/'.local/openrouter-evaluation.rdb'))
        store=FalkorStore(database,GRAPH,writable=True)
        raw_store=FalkorStore(database,GRAPH+'_raw',writable=True)
        store.reset(GRAPH)
        if not args.comparison_only: raw_store.reset(GRAPH+'_raw')
        at=datetime.fromisoformat('2026-10-17T12:00:00+00:00')
        scope=Scope(environment='production',region='eu')
        if not args.comparison_only:
            extractor=OpenRouterExtractor(config,session=session)
            manifest=Bundle.model_validate_json((root/'data/raw_demo/manifest.json').read_text())
            extracted=[]; by_source={}
            for source in manifest.sources:
                start=perf_counter()
                try:
                    part=manifest.model_copy(update={'sources':[source],'inventories':[]})
                    result=extract_bundle(part,extractor)
                    extracted.extend(result.assertions)
                    by_source[source.key]=result.assertions
                    report['extraction'].append({'source_key':source.key,'status':'validated',
                        'assertions':[a.model_dump(mode='json') for a in result.assertions],
                        'latency_ms':(perf_counter()-start)*1000})
                except (ExtractionError,ValueError) as error:
                    report['extraction'].append({'source_key':source.key,'status':'failed','error':str(error),
                        'latency_ms':(perf_counter()-start)*1000})
                save()
                if ledger.snapshot()['halted']: raise OpenRouterError('cost ledger halted during extraction')
            raw_revision=raw_store.ingest(manifest.model_copy(update={'assertions':extracted}))
            at=datetime.fromisoformat('2026-10-17T12:00:00+00:00')
            scope=Scope(environment='production',region='eu')
            report['raw_pipeline']={'revision':raw_revision,'approved':sum(a.status=='approved' for a in extracted),
                'proposals':sum(a.status=='proposal' for a in extracted),
                'assessment':Brain(raw_store).assess_retirement('legacy-runner',scope,at,known_at=at)}
            # Score manual narrative expectations without giving goldens to the model.
            combined=Bundle()
            from .ingestion import merge_bundle
            for stage in ('initial','completion','migration','clear'):
                combined=merge_bundle(combined,Bundle.model_validate_json((root/f'data/synthetic/{stage}.json').read_text()))
            sources={s.key:s for s in combined.sources}
            narrative=json.loads((root/'evals/gold/narrative.json').read_text())
            for case in narrative['cases']:
                source_key=case['source_key']; start=perf_counter()
                try:
                    if source_key in by_source: candidates=by_source[source_key]
                    else:
                        source=sources[source_key]
                        candidates=extractor.extract(raw_source(source,combined.entities))
                    report['narrative'].append({'source_key':source_key,'status':'scored',
                        'counts':score_narrative(candidates,case['expected']),
                        'candidates':[c.model_dump(mode='json') for c in candidates],
                        'latency_ms':(perf_counter()-start)*1000})
                except (ExtractionError,ValueError) as error:
                    report['narrative'].append({'source_key':source_key,'status':'failed','error':str(error),
                        'latency_ms':(perf_counter()-start)*1000})
                save()
                if ledger.snapshot()['halted']: raise OpenRouterError('cost ledger halted during narrative evaluation')
        client=OpenRouterEvaluationClient(session)
        experiment=Experiment(model=LUNA_MODEL,temperature=None,max_output_tokens=1500)
        gold=json.loads((root/'evals/gold/retirement.json').read_text())
        extra=json.loads((root/'evals/gold/questions.json').read_text())
        tasks=[]
        for state in gold['states']:
            tasks.append({'id':state['fixture'],'fixture':state['fixture'],
                'question':'Can we retire legacy-runner in production/eu? Explain business dependencies, blockers, owners, conflicts, permission expiry and coverage gaps with evidence IDs.',
                'planned_at':at.isoformat(),'expected':state})
        tasks.extend({**c,'fixture':'initial','expected':c} for c in extra['cases'])
        tasks=[task for task in tasks if task['id'] in report['selected_cases']]
        for index,task in enumerate(tasks):
            store.reset(GRAPH)
            for stage in ('initial','completion','migration','clear'):
                store.ingest(Bundle.model_validate_json((root/f'data/synthetic/{stage}.json').read_text()))
                if stage==task['fixture']: break
            toolbox=Toolbox(Brain(store),scope,at)
            pair={'case':task['id'],'fixture':task['fixture'],'model':LUNA_MODEL,
                  'record_digest':toolbox.search.digest,'arms':{}}
            report['evaluations'].append(pair)
            for arm in (('graph','search') if index%2==0 else ('search','graph')):
                start=perf_counter()
                try:
                    run=run_arm(client,experiment,toolbox,arm,task['question'],datetime.fromisoformat(task['planned_at']))
                    run['latency_ms']=(perf_counter()-start)*1000
                    if run['status']=='completed':
                        expected=task['expected']
                        if 'required_assertions' in expected:
                            run['counts']=score_answer(run['answer'],expected,run['supported_evidence_ids'])
                        else:
                            answer=run['answer']
                            run['counts']={'disposition_correct':answer.get('disposition')==expected['disposition'],
                                'required_workflows':len(expected['required_workflows']),
                                'correct_workflows':len(set(expected['required_workflows'])&set(answer.get('affected_workflows',[]))),
                                'unsupported_evidence':len(set(answer.get('evidence_ids',[]))-set(run['supported_evidence_ids'])),
                                'gap_handling_correct':bool(answer.get('gaps'))==expected['requires_gaps']}
                    pair['arms'][arm]=run
                except (OpenRouterError,ValueError,KeyError,TypeError) as error:
                    pair['arms'][arm]={'status':'failed','error':str(error),'latency_ms':(perf_counter()-start)*1000}
                save()
                print(json.dumps({'milestone':'arm','case':task['id'],'arm':arm,'status':pair['arms'][arm]['status'],'actual_usd':ledger.snapshot()['actual_usd']}),flush=True)
                if ledger.snapshot()['halted']: raise OpenRouterError('cost ledger halted during comparison')
        failures=any(x['status']=='failed' for x in report['extraction']) or any(a['status']!='completed' for c in report['evaluations'] for a in c['arms'].values())
        report['status']='completed_with_failures' if failures else 'completed'; save()
    except (OpenRouterError,StoreUnavailable,ValueError,OSError) as error:
        report['status']='stopped'; report['error']=str(error)
        # Authentication errors occur before any inference; do not reveal file contents.
        try: save()
        except (OpenRouterError,OSError): pass
    finally:
        if database is not None:
            try: database.client.save(); database.client.shutdown()
            except Exception: pass
    safe=redact(report,key) if key else report
    ledger_state=safe.get('ledger',{})
    print(json.dumps({'status':safe['status'],'smoke_passed':bool(safe['smoke'] and safe['smoke']['passed']),
        'actual_usd':ledger_state.get('actual_usd'),'conservative_usd':ledger_state.get('conservative_usd'),
        'halted':ledger_state.get('halted'),'report':str(output),'error':safe.get('error')}))
    return 0 if report['status'] in {'completed','completed_with_failures'} else 1


if __name__=='__main__': raise SystemExit(main())
