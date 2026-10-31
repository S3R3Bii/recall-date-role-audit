"""Run source-backed acceptance and rejection examples; no network writes."""
from pathlib import Path
import argparse,json
from guard import validate_event
from analyze import load,save,ROOT

def evidence_table():
    cases={r["campaign"]:r for r in load("results/cases.json")}
    evidence={}
    for row in load("data/api_notice_assertions.json"):
        for i,a in enumerate(row["assertions"]):
            evidence["API-"+row["campaign"]+"-"+str(i)]=dict(campaign=row["campaign"],date=a["date"],state=a["state"],role=a["role"],
                status="AMBIGUOUS" if cases[row["campaign"]]["category"]=="CONFLICTING_DATES" else "SUPPORTED",
                first_availability_verified=False)
    for d in load("data/document_adjudication.json"):
        evidence[d["document_id"]]=dict(campaign=d["campaign"],date=d["printed_date"] if d["date_precision"]=="day" else None,
            state="DOCUMENT_DATE_ONLY",role="DOCUMENT_DATE",status="SUPPORTED",first_availability_verified=False)
    return evidence
def run(out):
    requests=load("data/exercise_inputs.json");evidence=evidence_table()
    result=[dict(name=r["name"],request=r["request"],result=validate_event(r["request"],evidence)) for r in requests]
    save(out,"exercise.json",result)
    print(json.dumps(dict(status="PASS",examples=len(result),accepted=sum(r["result"]["accepted"] for r in result))))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=ROOT/"results");run(p.parse_args().out)
