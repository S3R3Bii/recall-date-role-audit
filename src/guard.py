"""A local typed-event guard. Source assertions retain their original role and certainty."""
from datetime import date
import re

ROLES={"GENERIC_NOTICE","INTERIM_NOTICE","REMEDY_NOTICE","PHYSICAL_FIRST_AVAILABILITY","DOCUMENT_DATE","PLANNED_OWNER_NOTICE"}
def validate_event(request,evidence):
    def reject(reason):return dict(accepted=False,reason=reason,event=None)
    key=request.get("evidence_id")
    if key not in evidence:return reject("MISSING_EVIDENCE")
    source=evidence[key]
    if source.get("status")!="SUPPORTED":return reject("AMBIGUOUS_OR_CONFLICTING_EVIDENCE")
    if request.get("campaign")!=source.get("campaign"):return reject("CAMPAIGN_MISMATCH")
    token=request.get("date")
    if token is None or source.get("date") is None:return reject("MISSING_DATE")
    if not isinstance(token,str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}",token):return reject("AMBIGUOUS_OR_INVALID_DATE")
    try:date.fromisoformat(token)
    except ValueError:return reject("AMBIGUOUS_OR_INVALID_DATE")
    if token!=source["date"]:return reject("DATE_MISMATCH")
    if request.get("state")!="REPORTED" or source.get("state")!="REPORTED":return reject("NOT_A_REPORTED_EVENT")
    role=request.get("role")
    if role not in ROLES or role!=source.get("role"):return reject("UNSUPPORTED_ROLE_CONVERSION")
    if role=="PHYSICAL_FIRST_AVAILABILITY" and source.get("first_availability_verified") is not True:return reject("FIRST_AVAILABILITY_UNVERIFIED")
    return dict(accepted=True,reason="RETAIN_SOURCE_ROLE",event={k:request[k] for k in ["campaign","role","date","state","evidence_id"]})
