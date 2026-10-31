"""Original figures bound to every fixed campaign result."""

from pathlib import Path
from datetime import datetime
import json, hashlib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "figures"
out.mkdir(exist_ok=True)
read = lambda name: json.loads((ROOT / name).read_bytes())
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "svg.fonttype": "none",
        "svg.hashsalt": "recall-date-role-audit-v1",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.edgecolor": "#68747b",
        "text.color": "#172b36",
        "axes.labelcolor": "#172b36",
    }
)
blue = "#176b93"
amber = "#a65e00"
green = "#236f51"
gray = "#71808a"
manifest = {}


def finish(fig, name, artists):
    for extension in ["svg", "png", "pdf"]:
        meta = (
            {"Date": None}
            if extension == "svg"
            else (
                {"CreationDate": None, "ModDate": None}
                if extension == "pdf"
                else {"Software": "Matplotlib"}
            )
        )
        fig.savefig(
            out / (name + "." + extension), dpi=160, facecolor="white", metadata=meta
        )
        if extension == "svg":
            target = out / (name + ".svg")
            target.write_bytes(
                b"\n".join(line.rstrip() for line in target.read_bytes().splitlines())
                + b"\n"
            )
    manifest[name] = dict(
        artists=artists,
        sha256={
            e: hashlib.sha256((out / (name + "." + e)).read_bytes()).hexdigest()
            for e in ["svg", "png", "pdf"]
        },
    )
    plt.close(fig)


cases = read("results/cases.json")
summary = read("results/summary.json")
labels = [
    "MATCH_GENERIC_NOTICE",
    "CONFLICTING_DATES",
    "UNRESOLVED",
    "MATCH_INTERIM",
    "MATCH_REMEDY_NOTICE",
]
display = [
    "Matching generic notice",
    "Conflicting reported dates",
    "No past-event binding",
    "Exact interim binding",
    "Exact remedy/final binding",
]
fig = plt.figure(figsize=(9, 3.4))
ax = fig.add_axes([0.33, 0.25, 0.62, 0.55])
ax.set_xlim(0, 12)
ax.set_ylim(4.7, -0.7)
values = [summary["category_counts"][x] for x in labels]
bars = ax.barh(range(5), values, height=0.56, color=[blue, amber, gray, green, green])
artists = []
for bar, key, value in zip(bars, labels, values):
    bar.set_gid("count-" + key)
    ax.text(
        value + 0.14,
        bar.get_y() + bar.get_height() / 2,
        str(value),
        va="center",
        fontweight="bold",
    )
    artists.append(dict(id="count-" + key, kind="bar", value=float(bar.get_width())))
ax.set_yticks(range(5), display)
ax.set_xticks([0, 3, 6, 9, 12])
ax.set_xlabel("Campaigns (fixed cohort n = 12)")
ax.grid(axis="x", alpha=0.16)
ax.set_axisbelow(True)
fig.text(
    0.04,
    0.94,
    "Notification fields do not establish a first-availability date",
    fontsize=14,
    fontweight="bold",
    va="top",
)
fig.text(
    0.04,
    0.84,
    "Conservative event-role coding preserves unsupported and conflicting bindings.",
    fontsize=10,
)
fig.text(
    0.04,
    0.035,
    "No physical first-availability date is established for any of the 12 campaigns.",
    fontsize=9,
)
finish(fig, "event_role_counts", artists)

fig = plt.figure(figsize=(9, 5.7))
ax = fig.add_axes([0.16, 0.23, 0.79, 0.64])
lower = datetime(2023, 1, 1)
upper = datetime(2023, 4, 1)
ax.set_xlim(lower, upper)
ax.set_ylim(12.7, 0.3)
artists = []
for y, row in enumerate(cases, 1):
    campaign = row["campaign"]
    stamp = datetime.fromisoformat(row["owner_field_date"])
    (artist,) = ax.plot(
        stamp, y, "o", ms=7, color=blue, label="Flat ODATE" if y == 1 else None
    )
    artist.set_gid("field-" + campaign)
    artists.append(
        dict(id="field-" + campaign, kind="point", date=row["owner_field_date"], row=y)
    )
    a = row["api_assertions"][0]
    past = a["state"] == "REPORTED"
    stamp = datetime.fromisoformat(a["date"])
    (artist,) = ax.plot(
        stamp,
        y,
        "D" if past else "^",
        ms=6.5,
        mfc=green if past else "white",
        mec=green if past else amber,
        linestyle="none",
    )
    artist.set_gid("api-" + campaign)
    artists.append(
        dict(
            id="api-" + campaign, kind="point", date=a["date"], row=y, state=a["state"]
        )
    )
ax.set_yticks(range(1, 13), [r["campaign"][:6] for r in cases])
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.grid(axis="x", alpha=0.16)
ax.set_xlabel("Printed source dates in 2023; not a repair-availability timeline")
from matplotlib.lines import Line2D

ax.legend(
    handles=[
        Line2D([], [], marker="o", color=blue, ls="", label="Flat ODATE"),
        Line2D(
            [], [], marker="D", color=green, ls="", label="API: reported notice (7)"
        ),
        Line2D(
            [],
            [],
            marker="^",
            mfc="white",
            mec=amber,
            color=amber,
            ls="",
            label="API: expected notice (5)",
        ),
    ],
    loc="upper center",
    bbox_to_anchor=(0.44, -0.18),
    ncol=3,
    frameon=False,
    fontsize=9,
)
fig.text(
    0.04,
    0.96,
    "The same date column can sit beside different source assertions",
    fontsize=14,
    fontweight="bold",
    va="top",
)
fig.text(
    0.04,
    0.895,
    "All 12 campaigns retained. Expected dates remain planned, even when the calendar date has passed.",
    fontsize=9,
)
fig.text(
    0.04,
    0.025,
    "Source: captured NHTSA flat file and current campaign API. No independent mailing delivery or historical first-vintage proof.",
    fontsize=8.5,
)
finish(fig, "field_and_api_dates", artists)

past = [r for r in cases if r["field_minus_reported_notice_days"] is not None]
fig = plt.figure(figsize=(9, 3.8))
ax = fig.add_axes([0.2, 0.24, 0.73, 0.6])
ax.set_xlim(-30, 5)
ax.set_ylim(len(past) - 0.3, -0.7)
artists = []
for y, row in enumerate(past):
    value = row["field_minus_reported_notice_days"][0]["days"]
    key = "difference-" + row["campaign"]
    bar = ax.barh([y], [value], height=0.48, color=amber if value else blue)[0]
    bar.set_gid(key)
    if value == 0:
        ax.plot(0, y, "o", ms=4, color=blue)
    ax.text(
        value - 0.6 if value < 0 else 0.45,
        y,
        str(value) + " d",
        ha="right" if value < 0 else "left",
        va="center",
        fontweight="bold",
    )
    artists.append(dict(id=key, kind="bar", value=float(bar.get_width())))
ax.axvline(0, color="#65757c", lw=0.8)
ax.set_yticks(range(len(past)), [r["campaign"][:6] for r in past])
ax.set_xticks([-30, -20, -10, 0])
ax.set_xlabel("Flat ODATE minus current API reported notice date (calendar days)")
ax.grid(axis="x", alpha=0.16)
ax.set_axisbelow(True)
fig.text(
    0.04,
    0.96,
    "One source discrepancy needs investigation",
    fontsize=14,
    fontweight="bold",
    va="top",
)
fig.text(
    0.04,
    0.86,
    "7 reported-notice cases; the other 5 have no comparable past API assertion.",
    fontsize=10,
)
fig.text(
    0.04,
    0.035,
    "Negative means the flat date is earlier. Zero means source-date equality, not zero repair delay.",
    fontsize=9,
)
finish(fig, "reported_date_differences", artists)
(out / "manifest.json").write_bytes(
    (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
)
print(
    json.dumps(
        dict(
            status="CREATED",
            figures=len(manifest),
            source_bound_artists=sum(len(x["artists"]) for x in manifest.values()),
            assets=9,
        )
    )
)
