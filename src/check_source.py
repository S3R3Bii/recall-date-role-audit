"""Verify saved factual projections and complete document accounting."""
from pathlib import Path
from datetime import datetime
import json,re
ROOT=Path(__file__).resolve().parents[1]
read=lambda name:json.loads((ROOT/name).read_bytes())
n=0
def check(value,label):
    global n
    assert value,label;n+=1
wanted={f"23V{i:03d}000" for i in range(1,13)}
flat=read("data/flat_projection.json");api=read("data/api_projection.json")
assertions=read("data/api_notice_assertions.json");docs=read("data/document_adjudication.json")
manifest=read("data/document_manifest.json");elig=read("data/document_eligibility.json")
for name,rows in [("flat",flat),("API",api),("assertions",assertions)]:
    check(len(rows)==12 and {x["campaign"] for x in rows}==wanted,name+" complete fixed cohort")
check(len(manifest)==64,"64 captured PDFs")
check(len(docs)==60,"60 eligible documents")
check({x["document_id"] for x in docs}=={x["document_id"] for x in manifest if "envelope" not in x["listed_type"].lower()},"envelopes alone excluded")
check(len({x["document_id"] for x in docs})==60,"unique document IDs")
by_id={x["document_id"]:x for x in manifest}
for d in docs:
    check(d["campaign"] in wanted,"document campaign")
    check(d["source_sha256"]==by_id[d["document_id"]]["sha256"],"native source hash linkage")
    check(bool(re.fullmatch("[0-9a-f]{64}",d["source_sha256"])),"native SHA")
    check(d["page_count"]>=1,"page count")
    check(d["physical_first_availability_date"] is None,"no availability imputation")
    check(d["date_precision"] in ["day","month","none"],"date precision")
    if d["date_precision"]=="day":
        check(datetime.strptime(d["printed_date"],"%Y-%m-%d").date().isoformat()==d["printed_date"],"printed day")
    elif d["date_precision"]=="month":check(bool(re.fullmatch(r"\d{4}-\d{2}",d["printed_date"])),"month retained")
    else:check(d["printed_date"] is None,"missing retained")
    for cell in d.get("two_reader_cells",[]):
        check(1<=cell["page"]<=d["page_count"],"cell source page")
        check(cell["role"] in ["submission","planned_owner"],"typed structured cell")
    for e in d["evidence"]:check(1<=e["page"]<=d["page_count"] and bool(e["clause"]),"evidence page/clause")
for a in assertions:
    base=next(x for x in api if x["campaign"]==a["campaign"])
    check(a["source_sha256"]==base["source_sha256"],"API source linkage")
    check(a["native_records"]==base["response_records"],"API record denominator")
    check(a["distinct_remedy_texts"]==len(a["assertions"]),"all distinct assertions")
    for x in a["assertions"]:
        check(x["role"]=="GENERIC_NOTICE","no inferred final role")
        check(x["state"] in ["PLANNED","REPORTED"],"source certainty")
        check(datetime.strptime(x["date"],"%Y-%m-%d").date().isoformat()==x["date"],"source exact date")
check(read("data/document_verification.json")["status"]=="PASS","retained native source check")
print(json.dumps(dict(status="PASS",finite_conditions=n,scope="Saved public projection and lineage; native originals verified separately, not downloaded by this check.")))
