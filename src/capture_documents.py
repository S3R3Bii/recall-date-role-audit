"""Select from captured official dossier links before reading PDF contents."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def write(path, value):
    path.write_bytes((json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-dir", required=True, type=Path)
    a = p.parse_args()
    cases = json.loads((ROOT / "data/source_plan.json").read_bytes())["campaigns"]
    assert not (ROOT / "data/document_plan.json").exists()
    records = []
    lists = []
    for cid in cases:
        source = a.source_dir / (cid + "-document-list-dom.json")
        raw = source.read_bytes()
        body = json.loads(raw)
        assert body["campaign"] == cid and len(body["links"]) == body["declared_documents"]
        lists.append(dict(campaign=cid,sha256=hashlib.sha256(raw).hexdigest(),documents=body["declared_documents"]))
        for row in body["links"]:
            u = urlparse(row["url"])
            filename = Path(u.path).name
            assert u.netloc == "static.nhtsa.gov" and u.path.startswith("/odi/rcl/2023/") and not u.query
            assert cid[:6] in filename and filename.lower().endswith(".pdf")
            assert row["parent_text"].endswith(row["label"])
            kind = row["parent_text"][:-len(row["label"])].strip()
            selected = "573" in kind or kind.lower() == "recall acknowledgement" or ("owner" in kind.lower() and ("notif" in kind.lower() or "letter" in kind.lower()))
            records.append(dict(campaign=cid,document_id=filename,url=row["url"],listed_type=kind,selected=selected,reason="fixed Part573/acknowledgement/owner-notice scope" if selected else "dealer instruction/notice or performance report outside fixed scope"))
    write(ROOT/"data/document_plan.json",dict(dossier_source_lists=lists,documents=records,selection_by_metadata_before_pdf_contents=True))
    print("DOCUMENT_METADATA_FIXED",len(records),"listed;",sum(r["selected"] for r in records),"selected",flush=True)
    folder = a.source_dir / "documents"
    folder.mkdir(exist_ok=False)
    manifest = []
    for row in records:
        if not row["selected"]:
            continue
        target = folder / row["document_id"]
        assert target.parent.resolve() == folder.resolve()
        assert not target.exists(), "duplicate document identity"
        with urlopen(Request(row["url"],headers={"User-Agent":"IndependentRecallDateResearch/1.0"}),timeout=45) as response:
            assert response.status == 200
            payload = response.read()
        assert payload.startswith(b"%PDF")
        target.write_bytes(payload)
        manifest.append(dict(**row,sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload),captured_utc=datetime.now(timezone.utc).isoformat()))
        write(a.source_dir/"document-capture-progress.json",manifest)
        print("CAPTURED_DOCUMENT",row["document_id"],len(payload),flush=True)
    write(ROOT/"data/document_manifest.json",manifest)
    print("SELECTED_NATIVE_DOCUMENTS_CAPTURED",len(manifest),sum(r["bytes"] for r in manifest),"bytes")


if __name__ == "__main__":
    main()
