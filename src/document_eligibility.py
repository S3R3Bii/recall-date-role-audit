"""Keep the capture ledger and exclude envelope templates from event coding."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
plan=json.loads((ROOT/"data/document_plan.json").read_bytes())
manifest=json.loads((ROOT/"data/document_manifest.json").read_bytes())
assert len(manifest)==64 and sum(r["selected"] for r in plan["documents"])==64
rows=[]
for doc in manifest:
    envelope="envelope" in doc["listed_type"].lower()
    rows.append(dict(document_id=doc["document_id"],campaign=doc["campaign"],eligible=not envelope,reason="Envelope template is not an event notice" if envelope else "Prespecified Part573/acknowledgement/owner-letter evidence"))
assert sum(not r["eligible"] for r in rows)==4
(ROOT/"data/document_eligibility.json").write_bytes((json.dumps(dict(stage="Metadata-only correction before semantic PDF content review or comparisons",original_capture_preserved=True,native_captured=64,envelope_templates_excluded=4,event_documents=60,documents=rows),indent=2)+"\n").encode())
print("EVENT_DOCUMENTS_60;4_ENVELOPE_TEMPLATES_EXCLUDED;ORIGINAL64_CAPTURE_RETAINED")
