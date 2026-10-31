"""Independently stream native TSV fields and verify projected campaign dates."""
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile
from collections import defaultdict, Counter
import argparse
import csv
import hashlib
import io
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-dir", type=Path, required=True)
    a = p.parse_args()
    manifest = json.loads((ROOT / "data/flat_manifest.json").read_bytes())
    plan = json.loads((ROOT / "data/source_plan.json").read_bytes())
    checks = 0
    archive = a.source_dir / "FLAT_RCL_POST_2010.zip"
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest["archive_sha256"]
    assert archive.stat().st_size == manifest["archive_bytes"]
    assert hashlib.sha256((a.source_dir/"RCL.txt").read_bytes()).hexdigest() == manifest["dictionary_sha256"]
    checks += 3
    found = defaultdict(list)
    shape = Counter()
    total = 0
    digest = hashlib.sha256()
    with ZipFile(archive) as z:
        assert z.namelist() == [manifest["member"]]
        with z.open(manifest["member"]) as stream:
            while chunk := stream.read(1 << 20):
                digest.update(chunk)
        assert digest.hexdigest() == manifest["payload_sha256"]
        with z.open(manifest["member"]) as stream:
            reader = csv.reader(io.TextIOWrapper(stream, encoding="latin1", newline=""), delimiter="\t", quoting=csv.QUOTE_NONE)
            for row in reader:
                total += 1
                shape[len(row)] += 1
                assert len(row) == 29
                checks += 1
                if row[1].strip() in plan["campaigns"]:
                    found[row[1].strip()].append((row[0].strip(), row[12].strip(), row[15].strip()))
    assert {str(k):v for k,v in shape.items()} == manifest["native_row_shapes"]
    projected = json.loads((ROOT / "data/flat_projection.json").read_bytes())
    assert [r["campaign"] for r in projected] == plan["campaigns"]
    api = {r["campaign"]:r for r in json.loads((ROOT / "data/api_projection.json").read_bytes())}
    for case in projected:
        cid = case["campaign"]
        rows = found[cid]
        assert len(rows) == case["flat_row_count"] and len({r[0] for r in rows}) == len(rows)
        assert sorted({r[1] for r in rows}) == case["owner_date_tokens"]
        assert sorted({r[2] for r in rows}) == case["report_date_tokens"]
        checks += 4
        for token in case["owner_date_tokens"] + case["report_date_tokens"]:
            if token not in ["", "00000000", "99999999"]:
                assert datetime.strptime(token,"%Y%m%d").strftime("%Y%m%d") == token
                checks += 1
        body = (a.source_dir / (cid + ".json")).read_bytes()
        assert hashlib.sha256(body).hexdigest() == api[cid]["source_sha256"]
        native = json.loads(body)
        assert len(native["results"]) == native["Count"] == api[cid]["response_records"]
        assert {r["NHTSACampaignNumber"] for r in native["results"]} == {cid}
        tokens = sorted({r["ReportReceivedDate"] for r in native["results"]})
        assert tokens == api[cid]["report_received_tokens"]
        # The documented 2012 example establishes day/month/year; reconcile to
        # unambiguous native YYYYMMDD rather than silently selecting a format.
        parsed = sorted({datetime.strptime(t,"%d/%m/%Y").strftime("%Y%m%d") for t in tokens})
        assert parsed == case["report_date_tokens"], (cid, "API/native report-date disagreement")
        checks += 5
    result = dict(status="PASS_NATIVE_PROJECTION_ONLY", native_rows=total, campaigns=len(projected), selected_native_rows=sum(len(x) for x in found.values()), api_records=sum(x["response_records"] for x in api.values()), conditions=checks, source_sha256=manifest["archive_sha256"], scope="Independent CSV stream, native schema, exact campaign/date projection, API body hashes and documented date-format reconciliation; no document role or remedy-availability validation yet")
    (ROOT/"data/native_verification.json").write_bytes((json.dumps(result,indent=2)+"\n").encode())
    print(json.dumps(result))


if __name__ == "__main__":
    main()
