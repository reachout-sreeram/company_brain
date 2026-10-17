"""Reproducible synthetic replay on an explicitly named isolated FalkorDB graph."""
import argparse
from datetime import datetime
import json
from pathlib import Path
from time import perf_counter

from .assessment import Brain
from .models import Bundle, Scope
from .store import connect


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-graph",required=True)
    parser.add_argument("--replays",type=int,default=3,choices=range(1,11))
    parser.add_argument("--project-root",type=Path,default=Path.cwd())
    parser.add_argument("--output",type=Path,default=Path("evals/results/replay.json"))
    args=parser.parse_args()
    store=connect(writable=True)
    if args.confirm_graph!=store.graph_name:
        parser.error("confirmation must exactly match COMPANY_BRAIN_GRAPH")
    root=args.project_root
    expected=json.loads((root/"evals/gold/retirement.json").read_text())
    at=datetime.fromisoformat(expected["assessment_time"])
    scope=Scope.model_validate(expected["scope"])
    canonical=None
    runs=[]
    for run in range(args.replays):
        start=perf_counter();store.reset(args.confirm_graph);reset_ms=(perf_counter()-start)*1000
        states=[]
        for state in expected["states"]:
            bundle=Bundle.model_validate_json((root/f'data/synthetic/{state["fixture"]}.json').read_text())
            store.ingest(bundle)
            start=perf_counter()
            result=Brain(store).assess_retirement(expected["service_id"],scope,at,known_at=at)
            ms=(perf_counter()-start)*1000
            assert result["disposition"]==state["disposition"], state["fixture"]
            assert set(state["required_workflows"])<=set(result["affected_workflows"])
            assert set(state["required_conflicts"])<={c["kind"] for c in result["conflicts"]}
            assert bool(result["coverage"]["gaps"])==state["requires_gaps"]
            if state["fixture"]=="migration":
                assert "monthly-billing" not in result["affected_workflows"]
            states.append({"fixture":state["fixture"],"assessment_ms":ms,"result":result})
        normalized=[s["result"] for s in states]
        if canonical is None:canonical=normalized
        else:assert normalized==canonical,"replay changed canonical result"
        runs.append({"run":run+1,"reset_ms":reset_ms,"states":states})
    report={"backend":"FalkorDB","extraction":"seeded/parsed synthetic fixtures; no LLM calls","reproducible":True,"runs":runs,"limits":"Synthetic functional replay; not production reliability, database comparison, or client LLM latency."}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2))
    print(json.dumps({"passed_replays":len(runs),"output":str(args.output),"dispositions":[s["disposition"] for s in expected["states"]]}))


if __name__=="__main__":main()
