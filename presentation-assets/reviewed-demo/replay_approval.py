"""Replay an explicitly selected synthetic reviewer action through the actual CLI.

No inference, credentials, automatic proposal selection, or MCP writes.
"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import argparse,json,os,subprocess,sys
from redislite.falkordb_client import FalkorDB
from company_brain.models import Bundle
from company_brain.ingestion import validate_bundle

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'pyproject.toml').is_file() and (p/'src/company_brain').is_dir())
SELECTED=[
 'extract-e1439acc053738b33e07aeb4',
 'extract-ed1de0ddfaf3e889e164c98b',
 'extract-82af5c14e512875540990c30',
 'extract-1f030345bfd89a795d1be50c',
]
NOTE=('Synthetic demonstration, not a real human approval: manually checked these four exact candidates against full '
      'source/version, quote/span, subject/object and production/eu scope. Runtime observation is explicitly 17 October '
      '09:00 UTC; the version-2 billing prerequisite uses declared validity, not an invented observation. Roster assigns '
      'invoice-export to data-platform. Decision permits use from 1 October until 1 November exclusively. Remaining '
      'proposals are deliberately unapproved; missing extraction facts are not invented.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    pending=HERE/'pending.json';bundle=Bundle.model_validate_json(pending.read_text());validate_bundle(bundle)
    selected=[a for a in bundle.assertions if a.id in SELECTED]
    if len(selected)!=4 or any(a.status!='proposal' for a in selected):raise ValueError('fixed reviewed candidate identities changed')
    now=datetime.now(timezone.utc);at=now.isoformat();before_time=(now-timedelta(microseconds=1)).isoformat()
    db=FalkorDB(str(output/'demo.rdb'))
    env={'PATH':os.defpath,'LANG':'C.UTF-8','FALKORDB_SOCKET':db.client.connection_pool.connection_kwargs['path'],
         'COMPANY_BRAIN_GRAPH':'company_brain_demo_reviewed_narrative'}
    env.pop('COMPANY_BRAIN_LITE_PATH',None)
    commands=[]
    def cli(name,*arguments):
        command=[sys.executable,'-m','company_brain.cli',*arguments]
        done=subprocess.run(command,cwd=ROOT,env=env,text=True,capture_output=True,check=True)
        result=json.loads(done.stdout);(output/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
        commands.append({'step':name,'argv':command[1:],'result':name+'.json'})
        print(json.dumps({'step':name,'disposition':result.get('disposition'),'graph_revision':result.get('graph_revision'),'review_id':result.get('review',{}).get('id')}),flush=True)
        return result
    def assess(name,known):
        return cli(name,'assess','legacy-runner','--environment','production','--region','eu',
                   '--planned-at',at,'--known-at',known)
    try:
        cli('candidates','proposals',str(pending))
        old=cli('ingest-pending','ingest',str(pending));before=assess('before',at)
        flags=[item for ident in SELECTED for item in ('--proposal',ident)]
        approval=cli('approval','approve-proposals',str(pending),*flags,'--actor','demo:synthetic-source-validation',
            '--demonstration','--reviewed-at',at,'--note',NOTE,'--output',str(output/'reviewed.json'))
        cli('review-history','review-history',str(output/'reviewed.json'))
        new=cli('ingest-reviewed','ingest',str(output/'reviewed.json'));after=assess('after',at)
        historic=assess('before-review-knowledge',before_time)
        assert before['disposition']=='needs_verification' and after['disposition']=='blocked'
        assert historic['disposition']=='needs_verification'
        assert 'monthly-billing' in after['affected_workflows']
        assert all(e['approval_kind']=='demonstration' for e in after['evidence'])
        assert len(approval['review']['selections'])==4
        proof={'status':'passed','paid_calls':0,'review_kind':'demonstration; not human acceptance',
            'selected_proposals':SELECTED,'review_id':approval['review']['id'],'reviewed_at':at,
            'before_revision':old['graph_revision'],'after_revision':new['graph_revision'],
            'before_disposition':before['disposition'],'after_disposition':after['disposition'],
            'earlier_knowledge_disposition':historic['disposition'],
            'unapproved_proposals_retained':len(bundle.assertions)-4,'commands':commands}
        (output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');db.client.save()
        print(json.dumps({k:v for k,v in proof.items() if k!='commands'},indent=2))
    finally:db.client.shutdown()


if __name__=='__main__':main()
