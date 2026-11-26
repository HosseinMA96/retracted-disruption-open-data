"""E6: figure for the paper from run records only (results.json of the E4 runs). Runs on a laptop.
usage: python e06_figures.py RUN_ID E4_CD5_RUN E4_CD3_RUN    -> fig1_forest.pdf (+ .png preview) in the run folder."""
import sys, json
from pathlib import Path
import matplotlib; matplotlib.use("Agg"); import matplotlib.ticker
import matplotlib.pyplot as plt
from common import Run
HERE = Path(__file__).resolve().parents[1]
R5, R3 = sys.argv[2], sys.argv[3]
run = Run(sys.argv[1], __file__, {"e4_cd5": R5, "e4_cd3": R3, "palette": ["#2a78d6", "#eb6834"], "palette_check": "dataviz validate_palette.js light: all pass"})
load = lambda r: json.loads((HERE / "e04_eval" / "runs" / r / "results.json").read_text())
res = {"CD5 (papers 2000–2017)": load(R5), "CD3 (papers 2000–2019, post hoc)": load(R3)}
ROWS = [("All retracted", None), ("Misconduct", "misconduct"), ("Paper mill", "paper_mill"), ("Honest error", "honest_error"), ("Other", "other")]
pick = lambda r, k: r["primary"] if k is None else r["by_class"][k]
STY = [("#2a78d6", "o", -0.14), ("#eb6834", "s", 0.14)]
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "font.family": "sans-serif"})
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.6), sharey=True, gridspec_kw={"wspace": 0.12})
panels = [("Mean difference in CD (×10$^{-3}$)\n(retracted − controls)", "diff", False, 0),
          ("Odds ratio, CD > 0", "mh_cd_pos", True, 1), ("Odds ratio, top 5% of year", "mh_top_p95", True, 1)]
for ax, (title, key, is_or, ref) in zip(axes, panels):
    for (lab, r), (col, mk, dy) in zip(res.items(), STY):
        for i, (_, k) in enumerate(ROWS):
            x = pick(r, k)
            if is_or:
                m = x[key]; est, lo, hi = m["or"], m["ci"][0], m["ci"][1]
            else:
                est, (lo, hi) = 1e3 * x["diff"], [1e3 * v for v in x["diff_ci"]]
            ax.plot([lo, hi], [i + dy] * 2, color=col, lw=1.5, solid_capstyle="round")
            ax.plot(est, i + dy, marker=mk, ms=5, color=col, mec="white", mew=0.8, ls="none", label=lab if i == 0 else None)
    ax.axvline(ref, color="#8a8a85", lw=0.8, ls=(0, (3, 2)), zorder=0)
    if is_or:
        ax.set_xscale("log"); ax.set_xlim(0.45, 2.6); ax.set_xticks([0.5, 1, 2]); ax.set_xticklabels(["0.5", "1", "2"])
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_title(title, fontsize=8, color="#333330"); ax.tick_params(colors="#55554f", length=2)
    ax.grid(axis="x", color="#e6e6e1", lw=0.5); ax.set_axisbelow(True)
axes[0].set_yticks(range(len(ROWS))); axes[0].set_yticklabels([r[0] for r in ROWS]); axes[0].invert_yaxis()
fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.0))
fig.subplots_adjust(bottom=0.27, left=0.12, right=0.99, top=0.84)
for ext in ("pdf", "png"): fig.savefig(run.dir / f"fig1_forest.{ext}", dpi=200, metadata={"CreationDate": None} if ext == "pdf" else None)
run.log("figures", ["fig1_forest.pdf", "fig1_forest.png"]); run.finish()
