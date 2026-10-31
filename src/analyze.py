"""Compare typed source dates while preserving all twelve campaign outcomes."""
from pathlib import Path
from datetime import date,datetime
from collections import Counter
import argparse,json

ROOT=Path(__file__).resolve().parents[1]
def load(name):return json.loads((ROOT/name).read_bytes())
def save(folder,name,obj):
    folder.mkdir(parents=True,exist_ok=True)
    (folder/name).write_bytes((json.dumps(obj,indent=2,sort_keys=True)+"\n").encode())
def flat_date(token):
    if not isinstance(token,str) or len(token)!=8 or not token.isdigit():return None
    try:parsed=datetime.strptime(token,"%Y%m%d").date()
    except ValueError:return None
    return parsed.isoformat() if parsed.strftime("%Y%m%d")==token else None
def classify(tokens,assertions):
    usable=sorted({flat_date(x) for x in tokens if flat_date(x)})
    past=[a for a in assertions if a["state"]=="REPORTED"]
    dates=sorted({a["date"] for a in past})
    if len(usable)>1:return "CONFLICTING_DATES"
    if len(usable)!=1 or len(usable)!=len(tokens):return "UNRESOLVED"
    if not dates:return "UNRESOLVED"
    if dates!=usable:return "CONFLICTING_DATES"
    roles={a["role"] for a in past}
    if roles=={"INTERIM_NOTICE"}:return "MATCH_INTERIM"
    if roles=={"REMEDY_NOTICE"}:return "MATCH_REMEDY_NOTICE"
    if roles=={"GENERIC_NOTICE"}:return "MATCH_GENERIC_NOTICE"
    return "UNRESOLVED"

def run(out):
    flat=load("data/flat_projection.json")
    api={r["campaign"]:r for r in load("data/api_notice_assertions.json")}
    docs=load("data/document_adjudication.json")
    cases=[];plans=[]
    for item in flat:
        campaign=item["campaign"];assertions=api[campaign]["assertions"]
        dates=[flat_date(x) for x in item["owner_date_tokens"]]
        field=dates[0] if len(dates)==1 and dates[0] else None
        past=[a for a in assertions if a["state"]=="REPORTED"]
        category=classify(item["owner_date_tokens"],assertions)
        rows=[d for d in docs if d["campaign"]==campaign]
        differences=[dict(source_date=a["date"],days=(date.fromisoformat(field)-date.fromisoformat(a["date"])).days)
                     for a in past] if field else []
        cases.append(dict(campaign=campaign,owner_field_tokens=item["owner_date_tokens"],owner_field_date=field,
                          flat_rows=item["flat_row_count"],api_records=api[campaign]["native_records"],category=category,
                          api_assertions=assertions,field_minus_reported_notice_days=differences or None,
                          document_count=len(rows),physical_first_availability_date=None,
                          exact_interim_binding=False,exact_remedy_binding=False))
        for d in rows:
            if "planned_owner_start" in d:
                plans.append(dict(campaign=campaign,document_id=d["document_id"],submission_date=d["printed_date"],
                                  planned_start=d["planned_owner_start"],planned_end=d["planned_owner_end"],
                                  owner_field_date=field,state="PLANNED_REFERENCE_ONLY",
                                  field_minus_start_days=(date.fromisoformat(field)-date.fromisoformat(d["planned_owner_start"])).days if field else None,
                                  field_minus_end_days=(date.fromisoformat(field)-date.fromisoformat(d["planned_owner_end"])).days if field else None))
    categories={name:sum(c["category"]==name for c in cases) for name in
                ["MATCH_INTERIM","MATCH_REMEDY_NOTICE","MATCH_GENERIC_NOTICE","CONFLICTING_DATES","UNRESOLVED"]}
    counts=Counter(d["notice_role"] for d in docs)
    summary=dict(campaigns_requested=12,campaigns_returned=len(cases),usable_field_campaigns=sum(c["owner_field_date"] is not None for c in cases),
                 category_counts=categories,api_past_assertion_campaigns=sum(any(a["state"]=="REPORTED" for a in c["api_assertions"]) for c in cases),
                 api_planned_only_campaigns=sum(all(a["state"]=="PLANNED" for a in c["api_assertions"]) for c in cases),
                 document_counts_by_role=dict(sorted(counts.items())),adjudicated_documents=len(docs),
                 document_pages=sum(d["page_count"] for d in docs),flat_model_rows=sum(c["flat_rows"] for c in cases),
                 api_model_records=sum(c["api_records"] for c in cases),planned_report_rows=len(plans),
                 physical_first_availability_known=0,actual_remedy_delay_distribution=None,
                 qualification="Finite source-informed campaign audit; source equality is not verified delivery or physical first availability.")
    save(out,"cases.json",cases);save(out,"planned_references.json",plans);save(out,"summary.json",summary)
    print(json.dumps(dict(status="PASS",cases=len(cases),categories=categories,actual_remedy_delay_distribution="UNAVAILABLE")))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=ROOT/"results");run(p.parse_args().out)
