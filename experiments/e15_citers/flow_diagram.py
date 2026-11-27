"""Population flow from immutable E2/E4 records and the completed P15 aggregate result."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from common import Run, sha256

EXP = Path(__file__).resolve().parents[1]
e2path = EXP / "e02_population/runs/e02_pop_20261110_01/run.json"
e4path = EXP / "e04_eval/runs/e04_eval_20261110_01/results.json"
e11path = EXP / "e11_controls/runs/e11_controls_20261126_01/controls.json"
p15path = EXP / "e15_citers/runs" / sys.argv[2] / "results.json"
e2 = json.loads(e2path.read_text())["results"]
e4 = json.loads(e4path.read_text())["primary"]
e11 = json.loads(e11path.read_text())["cd5"]
p15 = json.loads(p15path.read_text())["windows"]["cd5"]
raw = p15["scenarios"]["unfiltered"]["mean"]
clean = p15["scenarios"]["all"]["mean"]
if e2["eligible"] != e2["with_journal_not_dup"] - e2["with_journal_not_dup_zero_refs"]:
    raise ValueError("Eligibility flow does not reconcile")
run = Run(sys.argv[1], __file__, {"e2_sha256": sha256(e2path), "e4_sha256": sha256(e4path),
                                  "e11_sha256": sha256(e11path),
                                  "p15_sha256": sha256(p15path), "matplotlib": matplotlib.__version__})
plt.rcParams.update({"font.size": 11.5, "font.family": "sans-serif", "pdf.fonttype": 42})
fig, ax = plt.subplots(figsize=(7.2, 7.8))
fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
ax.set(xlim=(0, 1), ylim=(0, 1))
ax.axis("off")


def box(x, y, width, height, text, colour="#edf3fa"):
    ax.add_patch(FancyBboxPatch((x - width / 2, y - height / 2), width, height,
                               boxstyle="round,pad=0.008", facecolor=colour, edgecolor="#657b91", linewidth=0.9))
    ax.text(x, y, text, ha="center", va="center", fontsize=11.5, linespacing=1.25)


def arrow(start, end):
    ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "color": "#657b91", "lw": 1.1})


box(0.5, 0.92, 0.9, 0.11,
    f"Eligible biomedical papers, 2000\u20132017: {e2['eligible']:,}\n"
    f"Journal/DOI rules: {e2['with_journal_not_dup']:,}\nNo references excluded: "
    f"{e2['with_journal_not_dup_zero_refs']:,}")
box(0.25, 0.735, 0.43, 0.12, f"Eligible retracted papers\n{e2['retracted_secondary_all']:,}")
box(0.75, 0.735, 0.43, 0.12,
    f"Controls drawn for all\n{e2['retracted_secondary_all']:,} retracted papers\n"
    f"{e2['controls']:,} controls; {e2['strata']:,} strata")
arrow((0.4, 0.857), (0.25, 0.803))
arrow((0.6, 0.857), (0.75, 0.803))
box(0.25, 0.55, 0.43, 0.12,
    f"First notice after window\n{e2['retracted_primary_after_window']:,} primary papers\n"
    f"{e2['retracted_secondary_all'] - e2['retracted_primary_after_window']:,} earlier retractions excluded")
box(0.75, 0.55, 0.43, 0.12,
    f"Defined CD5 controls\n{e4['controls_defined']:,}\n"
    f"{e4['controls_n'] - e4['controls_defined']:,} zero denominators excluded")
arrow((0.25, 0.667), (0.25, 0.618))
arrow((0.75, 0.667), (0.75, 0.618))
box(0.5, 0.36, 0.9, 0.12,
    f"Primary CD5 comparison: {e4['retracted_in_used_strata']:,} retracted papers\n"
    f"{e11['controls_used_strata']['controls_defined']:,} scored controls; {e4['strata_used']:,} journal\u2013year strata\n"
    f"{e4['retracted_defined'] - e4['retracted_in_used_strata']:,} primary paper lacks a scored stratum control")
arrow((0.25, 0.482), (0.4, 0.428))
arrow((0.75, 0.482), (0.6, 0.428))
box(0.5, 0.165, 0.9, 0.14,
    f"DI_nok: unfiltered comparison {raw['retracted_compared']:,} retracted / {raw['controls_compared']:,} controls\n"
    f"After excluding notice, comment/letter and retracted citing records:\n"
    f"{clean['retracted_compared']:,} retracted / {clean['controls_compared']:,} controls\n"
    f"{clean['strata']:,} strata; {clean['journals']:,} journals", "#f8efdf")
arrow((0.5, 0.292), (0.5, 0.243))
ax.text(0.5, 0.035, f"Reference sample: {e2['context_sample']:,} eligible papers (0.2%)",
        ha="center", va="center", fontsize=11.5)
for ext in ["pdf", "png"]:
    fig.savefig(run.dir / f"fig3_population_flow.{ext}", dpi=200,
                metadata={"CreationDate": None} if ext == "pdf" else None)
plt.close(fig)
run.log("comparison_counts", {"cd5_retracted": e4["retracted_in_used_strata"],
                             "cd5_controls": e11["controls_used_strata"]["controls_defined"], "p15": clean})
run.finish()
