"""Check actual manuscript bindings, complete cases, qualifiers and scoped bytes."""

from pathlib import Path
import hashlib, json, re, unicodedata
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
read = lambda n: json.loads((ROOT / n).read_bytes())
n = 0


def require(ok, label):
    global n
    assert ok, label
    n += 1


tex = (ROOT / "paper/main.tex").read_text(encoding="utf-8")
pdf = PdfReader(ROOT / "paper/manuscript.pdf")
text = unicodedata.normalize(
    "NFKC", "\n".join(p.extract_text() or "" for p in pdf.pages)
).replace("\u2212", "-")
compact = re.sub(r"\s+", " ", text)
require(len(pdf.pages) == 5, "five current pages")
bindings = read("paper/bindings.json")
require(
    len(bindings) == 48 and len({x["name"] for x in bindings}) == 48,
    "48 unique used bindings",
)
for b in bindings:
    v = read(b["file"])
    if b["query"]:
        rows = [r for r in v if all(r[k] == x for k, x in b["query"].items())]
        require(len(rows) == 1, "source row")
        v = rows[0]
    for key in b["field"]:
        v = v[key]
    if b["operation"] == "length":
        v = len(v)
    require(str(v) == b["display"], "source display")
    definition = "\\newcommand{\\" + b["name"] + "}{" + b["display"] + "}"
    require(definition in tex, "actual TeX value")
    require(
        len(re.findall(r"\\" + re.escape(b["name"]) + r"\b", tex)) >= 2,
        "macro used beyond definition",
    )
    require(b["display"] in text, "actual PDF display")
for phrase in [
    "Not peer reviewed",
    "remains unexecuted",
    "not independently verified delivery",
    "source informed",
    "no blinded",
    "nine cells",
    "not every page",
    "physical first availability is unknown",
    "current sources",
    "not a distribution of actual remedy delay",
    "guard relies on the curated evidence",
    "not redownload native sources",
    "no production users",
    "Azure optimization",
]:
    require(phrase.lower() in compact.lower(), ("scope qualification", phrase))
for c in read("results/cases.json"):
    require(c["campaign"][:6] in text, "complete PDF case table")
require(len(read("data/document_plan.json")["documents"]) == 197, "197 listed links")
require(len(read("data/document_manifest.json")) == 64, "64 retained PDFs")
require(len(read("data/document_adjudication.json")) == 60, "60 coded documents")
require(
    read("data/native_verification.json")["conditions"] == 247156,
    "native finite-check claim",
)
require(
    read("data/document_verification.json")["finite_conditions"] == 712,
    "native document-check claim",
)
require(
    read("data/document_verification.json")["manual_native_page_cells"] == 9,
    "manual source cell claim",
)
for label in ["310", "312"]:
    replay = read("results/reproduction_cpython" + label + ".json")
    require(replay["status"] == "PASS" and replay["full_history"], "isolated replay")
    require(
        len(replay["reproduced_files"]) == 4 and replay["unchanged_source_files"] == 13,
        "four outputs/13 sources",
    )
scope = read("paper/PUBLICATION_SCOPE.json")
require(
    scope["scope"] == "independent-program-study"
    and scope["formal_submission_target"] is False,
    "publication scope",
)
require(len(scope["public_files"]) == 5, "five scoped paper files")
for name, sha in scope["public_files"].items():
    require(
        hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha, "scoped bytes"
    )
for name in ["event_role_counts", "field_and_api_dates", "reported_date_differences"]:
    require(
        (ROOT / "paper/images" / (name + ".pdf")).read_bytes()
        == (ROOT / "figures" / (name + ".pdf")).read_bytes(),
        "current figure copy",
    )
visual = read("paper/visual_review.json")
require(
    visual["manuscript_sha256"]
    == hashlib.sha256((ROOT / "paper/manuscript.pdf").read_bytes()).hexdigest(),
    "reviewed PDF bytes",
)
require(visual["pages_reviewed"] == [1, 2, 3, 4, 5], "five actual reviewed pages")
receipt = dict(
    status="PASS",
    finite_conditions=n,
    used_numeric_bindings=len(bindings),
    pages=5,
    scope_files=5,
    scope="Actual TeX usage, source values, PDF text and case coverage, finite provenance facts, explicit limitations and reviewed scoped hashes. Native visual/source review recorded separately.",
)
(ROOT / "paper/verification.json").write_bytes(
    (json.dumps(receipt, indent=2) + "\n").encode()
)
print(json.dumps(receipt))
