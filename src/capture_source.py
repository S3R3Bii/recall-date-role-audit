"""Capture native recall source and project only fixed campaign/date metadata."""
from pathlib import Path
from datetime import datetime, timezone
from io import BytesIO
from zipfile import ZipFile
from collections import Counter
import argparse
import hashlib
import json
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def sha(content):
    return hashlib.sha256(content).hexdigest()


def save(path, value):
    path.write_bytes((json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode())


def retrieve(url):
    with urlopen(Request(url, headers={"User-Agent": "IndependentRecallDateResearch/1.0"}), timeout=45) as r:
        assert r.status == 200
        content = r.read()
    return content


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-dir", type=Path, required=True)
    a = p.parse_args()
    assert not a.source_dir.exists(), "Preserve previous capture evidence"
    a.source_dir.mkdir()
    plan = json.loads((ROOT / "data/source_plan.json").read_bytes())
    assert plan["target_data_retrieved"] is False
    assert not (ROOT / "data/flat_projection.json").exists()
    dictionary = retrieve(plan["source_dictionary"])
    (a.source_dir / "RCL.txt").write_bytes(dictionary)
    require_fields = [b"ODATE", b"Date Manufacturer Notified Owners", b"RCDATE", b"YYYYMMDD", b"29"]
    assert all(item in dictionary for item in require_fields)
    archive = retrieve(plan["source_flat_zip"])
    (a.source_dir / "FLAT_RCL_POST_2010.zip").write_bytes(archive)
    metadata = dict(url=plan["source_flat_zip"], retrieved_utc=datetime.now(timezone.utc).isoformat(), archive_sha256=sha(archive), archive_bytes=len(archive), dictionary_sha256=sha(dictionary))
    with ZipFile(BytesIO(archive)) as z:
        members = z.namelist()
        assert len(members) == 1 and members[0].lower().endswith(".txt")
        native = z.read(members[0])
    metadata.update(member=members[0], payload_sha256=sha(native), payload_bytes=len(native))
    chosen = {x: [] for x in plan["campaigns"]}
    shape = Counter()
    for line_number, line in enumerate(native.splitlines(), 1):
        fields = line.split(b"\t")
        shape[len(fields)] += 1
        assert len(fields) >= 16
        campaign = fields[1].strip().decode("ascii")
        if campaign in chosen:
            assert len(fields) == 29, (campaign, "native schema", len(fields))
            chosen[campaign].append(dict(source_line=line_number, record_id=fields[0].strip().decode("ascii"), campaign=campaign, owner_date_token=fields[12].strip().decode("ascii"), report_date_token=fields[15].strip().decode("ascii")))
    metadata["native_row_shapes"] = dict(shape)
    save(a.source_dir / "flat_selected_native.json", chosen)
    public = []
    for campaign in plan["campaigns"]:
        rows = chosen[campaign]
        assert len({r["record_id"] for r in rows}) == len(rows), "duplicate selected record identity"
        public.append(dict(campaign=campaign, flat_row_count=len(rows), owner_date_tokens=sorted({r["owner_date_token"] for r in rows}), report_date_tokens=sorted({r["report_date_token"] for r in rows})))
    save(ROOT / "data/flat_projection.json", public)
    save(ROOT / "data/flat_manifest.json", metadata)
    api_projections = []
    for campaign in plan["campaigns"]:
        url = plan["source_api"].format(campaign=campaign)
        raw = retrieve(url)
        (a.source_dir / (campaign + ".json")).write_bytes(raw)
        body = json.loads(raw)
        rows = body["results"]
        assert body["Count"] == len(rows)
        assert all(r["NHTSACampaignNumber"] == campaign for r in rows)
        api_projections.append(dict(campaign=campaign, response_records=len(rows), report_received_tokens=sorted({r["ReportReceivedDate"] for r in rows}), source_url=url, source_sha256=sha(raw), source_bytes=len(raw), captured_utc=datetime.now(timezone.utc).isoformat()))
        print("CAPTURED_CAMPAIGN_SOURCE", campaign, len(rows), flush=True)
    save(ROOT / "data/api_projection.json", api_projections)
    save(a.source_dir / "capture_receipt.json", dict(flat=metadata, campaigns=len(plan["campaigns"]), api_requests=len(api_projections), target_comparisons_run=False))
    print("FIXED_SOURCE_CAPTURE_COMPLETE_NO_COMPARISONS", len(plan["campaigns"]))


if __name__ == "__main__":
    main()
