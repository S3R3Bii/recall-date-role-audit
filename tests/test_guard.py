"""Authored boundary fixtures for typed events and source-date reconciliation."""
from pathlib import Path
import unittest,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from guard import validate_event
from analyze import classify,flat_date

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.source=dict(campaign="fixture",date="2024-02-29",state="REPORTED",role="GENERIC_NOTICE",status="SUPPORTED",first_availability_verified=False)
        self.evidence={"proof":self.source}
        self.request=dict(campaign="fixture",date="2024-02-29",state="REPORTED",role="GENERIC_NOTICE",evidence_id="proof")
    def test_valid_leap_day_notice(self):self.assertTrue(validate_event(self.request,self.evidence)["accepted"])
    def test_missing_evidence(self):
        self.request["evidence_id"]="absent";self.assertEqual(validate_event(self.request,self.evidence)["reason"],"MISSING_EVIDENCE")
    def test_ambiguous_evidence(self):
        self.source["status"]="AMBIGUOUS";self.assertFalse(validate_event(self.request,self.evidence)["accepted"])
    def test_campaign_mismatch(self):
        self.request["campaign"]="different";self.assertFalse(validate_event(self.request,self.evidence)["accepted"])
    def test_missing_date(self):
        self.source["date"]=None;self.assertEqual(validate_event(self.request,self.evidence)["reason"],"MISSING_DATE")
    def test_month_only(self):
        self.request["date"]="2024-02";self.assertFalse(validate_event(self.request,self.evidence)["accepted"])
    def test_invalid_leap_day(self):
        self.request["date"]="2023-02-29";self.assertFalse(validate_event(self.request,self.evidence)["accepted"])
    def test_ambiguous_slash_date(self):
        self.request["date"]="02/03/2024";self.assertFalse(validate_event(self.request,self.evidence)["accepted"])
    def test_wrong_day(self):
        self.request["date"]="2024-03-01";self.assertEqual(validate_event(self.request,self.evidence)["reason"],"DATE_MISMATCH")
    def test_plan_is_not_past(self):
        self.source["state"]="PLANNED";self.assertEqual(validate_event(self.request,self.evidence)["reason"],"NOT_A_REPORTED_EVENT")
    def test_document_date_is_not_mailing(self):
        self.source["state"]="DOCUMENT_DATE_ONLY";self.assertFalse(validate_event(self.request,self.evidence)["accepted"])
    def test_notification_is_not_physical_availability(self):
        self.request["role"]="PHYSICAL_FIRST_AVAILABILITY";self.assertEqual(validate_event(self.request,self.evidence)["reason"],"UNSUPPORTED_ROLE_CONVERSION")
    def test_typed_but_unverified_availability(self):
        self.request["role"]=self.source["role"]="PHYSICAL_FIRST_AVAILABILITY";self.assertEqual(validate_event(self.request,self.evidence)["reason"],"FIRST_AVAILABILITY_UNVERIFIED")
    def test_separately_verified_availability_fixture(self):
        self.request["role"]=self.source["role"]="PHYSICAL_FIRST_AVAILABILITY";self.source["first_availability_verified"]=True
        self.assertTrue(validate_event(self.request,self.evidence)["accepted"])
    def test_generic_cannot_be_final(self):
        self.request["role"]="REMEDY_NOTICE";self.assertFalse(validate_event(self.request,self.evidence)["accepted"])

class ReconciliationTests(unittest.TestCase):
    def a(self,date="2024-02-29",role="GENERIC_NOTICE",state="REPORTED"):return [dict(date=date,role=role,state=state)]
    def test_equal_generic(self):self.assertEqual(classify(["20240229"],self.a()),"MATCH_GENERIC_NOTICE")
    def test_equal_interim(self):self.assertEqual(classify(["20240229"],self.a(role="INTERIM_NOTICE")),"MATCH_INTERIM")
    def test_equal_remedy_notice(self):self.assertEqual(classify(["20240229"],self.a(role="REMEDY_NOTICE")),"MATCH_REMEDY_NOTICE")
    def test_planned_equality_is_unresolved(self):self.assertEqual(classify(["20240229"],self.a(state="PLANNED")),"UNRESOLVED")
    def test_conflicting_dates(self):self.assertEqual(classify(["20240228"],self.a()),"CONFLICTING_DATES")
    def test_multiple_field_dates(self):self.assertEqual(classify(["20240228","20240229"],self.a()),"CONFLICTING_DATES")
    def test_empty_denominator(self):self.assertEqual(classify([],[]),"UNRESOLVED")
    def test_invalid_native_day(self):self.assertIsNone(flat_date("20230229"))
    def test_missing_native_token(self):self.assertEqual(classify(["00000000"],self.a()),"UNRESOLVED")
    def test_mixed_missing_and_usable(self):self.assertEqual(classify(["","20240229"],self.a()),"UNRESOLVED")
    def test_conflicting_reported_roles(self):self.assertEqual(classify(["20240229"],self.a()+self.a(role="INTERIM_NOTICE")),"UNRESOLVED")
if __name__=="__main__":unittest.main()
