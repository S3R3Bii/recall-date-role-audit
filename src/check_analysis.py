"""Independent SQLite reconstruction. No production analysis or guard imports."""
from pathlib import Path
import json,sqlite3
ROOT=Path(__file__).resolve().parents[1]
read=lambda name:json.loads((ROOT/name).read_bytes())
db=sqlite3.connect(":memory:")
db.executescript("create table f(campaign text, token text); create table a(campaign text, stamp text, state text, role text); create table p(campaign text,document text,start text,end text);")
for r in read("data/flat_projection.json"):
    db.executemany("insert into f values(?,?)",[(r["campaign"],t) for t in r["owner_date_tokens"]])
for r in read("data/api_notice_assertions.json"):
    db.executemany("insert into a values(?,?,?,?)",[(r["campaign"],x["date"],x["state"],x["role"]) for x in r["assertions"]])
for r in read("data/document_adjudication.json"):
    if "planned_owner_start" in r:db.execute("insert into p values(?,?,?,?)",(r["campaign"],r["document_id"],r["planned_owner_start"],r["planned_owner_end"]))
db.executescript("""create view field as select campaign, substr(token,1,4)||'-'||substr(token,5,2)||'-'||substr(token,7,2) stamp from f;
create view past as select * from a where state='REPORTED';""")
conditions=0
def eq(actual,expected,label):
    global conditions
    assert actual==expected,(label,actual,expected);conditions+=1
cases=read("results/cases.json")
for r in cases:
    c=r["campaign"];field=db.execute("select stamp from field where campaign=?",(c,)).fetchall()
    past=db.execute("select stamp,role from past where campaign=?",(c,)).fetchall()
    status=db.execute("""select case
      when (select count(*) from field where campaign=:c)<>1 then 'UNRESOLVED'
      when (select count(*) from past where campaign=:c)=0 then 'UNRESOLVED'
      when exists(select 1 from past a join field f using(campaign) where campaign=:c and a.stamp<>f.stamp) then 'CONFLICTING_DATES'
      when (select count(distinct role) from past where campaign=:c)>1 then 'UNRESOLVED'
      when (select min(role) from past where campaign=:c)='INTERIM_NOTICE' then 'MATCH_INTERIM'
      when (select min(role) from past where campaign=:c)='REMEDY_NOTICE' then 'MATCH_REMEDY_NOTICE'
      else 'MATCH_GENERIC_NOTICE' end""",dict(c=c)).fetchone()[0]
    eq(r["category"],status,c+" category")
    eq(r["owner_field_date"],field[0][0],c+" field")
    expected=[dict(source_date=x[0],days=int(db.execute("select julianday(?)-julianday(?)",(field[0][0],x[0])).fetchone()[0])) for x in past] or None
    eq(r["field_minus_reported_notice_days"],expected,c+" signed source differences")
    eq(r["physical_first_availability_date"],None,c+" no imputation")
    eq(r["exact_interim_binding"],False,c+" no exact interim binding")
    eq(r["exact_remedy_binding"],False,c+" no exact final binding")
plan_rows=read("results/planned_references.json")
for r in plan_rows:
    expected=db.execute("""select p.start,p.end,cast(julianday(f.stamp)-julianday(p.start) as integer),
                    cast(julianday(f.stamp)-julianday(p.end) as integer)
                    from p join field f using(campaign) where document=?""",(r["document_id"],)).fetchone()
    eq([r["planned_start"],r["planned_end"],r["field_minus_start_days"],r["field_minus_end_days"]],list(expected),r["document_id"]+" range")
    eq(r["state"],"PLANNED_REFERENCE_ONLY","plan cannot become actual")
summary=read("results/summary.json")
for name,value in summary["category_counts"].items():eq(value,sum(x["category"]==name for x in cases),name+" count")
eq(sum(summary["category_counts"].values()),12,"category denominator")
eq(summary["api_past_assertion_campaigns"],db.execute("select count(distinct campaign) from past").fetchone()[0],"past denominator")
eq(summary["api_planned_only_campaigns"],12-summary["api_past_assertion_campaigns"],"planned denominator")
eq(summary["planned_report_rows"],db.execute("select count(*) from p").fetchone()[0],"report denominator")
eq(summary["physical_first_availability_known"],0,"unknown first availability")
eq(summary["actual_remedy_delay_distribution"],None,"unavailable is not zero")
expected_exercise={
"retain_reported_notice":(True,"RETAIN_SOURCE_ROLE"),
"reject_notification_as_availability":(False,"UNSUPPORTED_ROLE_CONVERSION"),
"reject_plan_as_reported":(False,"NOT_A_REPORTED_EVENT"),
"reject_undated_interim":(False,"MISSING_DATE"),
"reject_conflicting_source":(False,"AMBIGUOUS_OR_CONFLICTING_EVIDENCE"),
"reject_missing_evidence":(False,"MISSING_EVIDENCE")}
for row in read("results/exercise.json"):
    eq((row["result"]["accepted"],row["result"]["reason"]),expected_exercise[row["name"]],row["name"])
    if not row["result"]["accepted"]:eq(row["result"]["event"],None,row["name"]+" no fabricated event")
print(json.dumps(dict(status="PASS",finite_conditions=conditions,method="Independent SQLite joins, CASE logic and julianday arithmetic; authored exercise expectations",compared_cases=len(cases),compared_plans=len(plan_rows))))
