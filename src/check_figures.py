"""Check actual SVG coordinates and artist values against independent source tables."""

from pathlib import Path
from datetime import date
import hashlib, json, re, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
read = lambda n: json.loads((ROOT / n).read_bytes())
manifest = read("figures/manifest.json")
cases = read("results/cases.json")
summary = read("results/summary.json")
n = 0


def require(ok, label):
    global n
    assert ok, label
    n += 1


expected = {}
for key, value in summary["category_counts"].items():
    expected["count-" + key] = value
for c in cases:
    expected["field-" + c["campaign"]] = c["owner_field_date"]
    expected["api-" + c["campaign"]] = c["api_assertions"][0]["date"]
    if c["field_minus_reported_notice_days"] is not None:
        expected["difference-" + c["campaign"]] = c["field_minus_reported_notice_days"][
            0
        ]["days"]
for name, info in manifest.items():
    for extension, sha in info["sha256"].items():
        require(
            hashlib.sha256(
                (ROOT / "figures" / (name + "." + extension)).read_bytes()
            ).hexdigest()
            == sha,
            name + " " + extension + " hash",
        )
    tree = ET.fromstring((ROOT / "figures" / (name + ".svg")).read_bytes())
    ns = {"s": "http://www.w3.org/2000/svg"}
    groups = {g.attrib["id"]: g for g in tree.findall(".//s:g[@id]", ns)}
    for a in info["artists"]:
        require(a["id"] in groups, "actual SVG element")
        group = groups[a["id"]]
        value = expected[a["id"]]
        if a["kind"] == "bar":
            require(a["value"] == value, "artist matches result")
            path = group.find(".//s:path", ns)
            require(path is not None, "bar path")
            nums = [
                float(x)
                for x in re.findall(
                    r"-?\d+(?:\.\d+)?(?:e[-+]?\d+)?", path.attrib["d"], re.I
                )
            ]
            xs = nums[0::2]
            if name == "event_role_counts":
                width = value / 12 * 0.62 * 648
            else:
                width = abs(value) / 35 * 0.73 * 648
            require(abs((max(xs) - min(xs)) - width) < 0.00002, "actual SVG bar width")
            displayed = [t.text or "" for t in tree.findall(".//s:text", ns)]
            require(
                str(value) in displayed or str(value) + " d" in displayed,
                "numeric label in SVG",
            )
        else:
            require(a["date"] == value, "artist date matches source")
            point = group.find(".//s:use", ns)
            require(point is not None, "rendered marker")
            x = (
                0.16 * 648
                + (date.fromisoformat(value) - date(2023, 1, 1)).days / 90 * 0.79 * 648
            )
            y = (1 - 0.23 - 0.64) * 410.4 + (a["row"] - 0.3) / 12.4 * 0.64 * 410.4
            require(
                abs(float(point.attrib["x"]) - x) < 0.00002,
                "actual SVG date coordinate",
            )
            require(
                abs(float(point.attrib["y"]) - y) < 0.00002,
                "actual SVG campaign coordinate",
            )
require(len(expected) == 36, "all 5 counts,24 dates,7 differences")
receipt = dict(
    status="PASS",
    finite_conditions=n,
    source_bound_artists=len(expected),
    svg_coordinate_conditions=48 + 12,
    asset_hashes=9,
    scope="Actual SVG bars/markers/labels and artist values matched to results. Visual inspection recorded separately; no accessibility certification.",
)
(ROOT / "figures/verification.json").write_bytes(
    (json.dumps(receipt, indent=2) + "\n").encode()
)
print(json.dumps(receipt))
