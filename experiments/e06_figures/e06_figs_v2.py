"""E6 v2: paper figures from run records only (results.json / CSV files of the E4, E8 and E9 runs). Runs on a laptop.
Fig. 1: forest plot by retraction reason, CD5 and CD3 (v1 + P2), DI_nok (P5) and the review positive control (P4).
Fig. 2: event time around the retraction notice, balanced set (P9b); optional P12 adds paired-gap confidence intervals.
usage: python e06_figs_v2.py RUN_ID E4_CD5 E4_CD3 E8 E9 [E12] -> PDF figures (+ PNG previews).
Without E12, the earlier marginal-score figure is reproduced.
"""
import sys, json
from pathlib import Path
import matplotlib; matplotlib.use("Agg"); import matplotlib.ticker
import matplotlib.pyplot as plt
import pandas as pd
from common import Run, sha256

HERE = Path(__file__).resolve().parents[1]
R5, R3, R8, R9 = sys.argv[2:6]
R12 = sys.argv[6] if len(sys.argv) == 7 else None
BLUE, ORANGE, GREY, DARK = "#2a78d6", "#eb6834", "#7a7a74", "#333330"
run = Run(sys.argv[1], __file__, {"e4_cd5": R5, "e4_cd3": R3, "e8": R8, "e9": R9, "matplotlib": matplotlib.__version__,
                                   "palette": [BLUE, ORANGE, GREY], "pdf_fonttype": 42, "e12": R12})
load = lambda exp, r, f="results.json": json.loads((HERE / exp / "runs" / r / f).read_text())
e4 = {"5": load("e04_eval", R5), "3": load("e04_eval", R3)}
e8 = load("e08_posthoc2", R8)
plt.rcParams.update({"font.size": 11.5, "axes.spines.top": False, "axes.spines.right": False, "font.family": "sans-serif",
                     "pdf.fonttype": 42})

# ---------------- Fig. 1 -------------------------------------------------------------------------------------
ROWS = [("All retracted", None), ("Misconduct", "misconduct"), ("Paper mill", "paper_mill"), ("Honest error", "honest_error"),
        ("Other", "other"), ("Reviews vs\nother controls", "REVIEWS")]
ROW_Y = [0, 1, 2, 3, 4, 5.6]
SER = [("5", BLUE, "o", -0.14, "CD$_5$, papers 2000–2017"), ("3", ORANGE, "s", 0.14, "CD$_3$, papers 2000–2019 (post hoc)")]
def cd_cell(w, k):
    if k == "REVIEWS": return e8["P4_reviews"]["cd5"] if w == "5" else None
    return e4[w]["primary"] if k is None else e4[w]["by_class"][k]
def dinok_cell(w, k):
    if k == "REVIEWS": return e8["P4_reviews"]["dinok"] if w == "5" else None
    P = e8["P5_dinok"]["cd5" if w == "5" else "cd3"]
    return P["primary"] if k is None else P["by_class"][k]
panels = [("Mean difference in CD (×10$^{-3}$)", "diff", False, 0, cd_cell, 1e3),
          ("Odds ratio, CD > 0", ("mh_cd_pos", "mh_pos"), True, 1, cd_cell, None),
          ("Odds ratio, top 5% of year", ("mh_top_p95", "mh_top_p95"), True, 1, cd_cell, None),
          ("Mean difference in DI$_{nok}$\n(post hoc)", "diff", False, 0, dinok_cell, 1.0)]
fig, grid = plt.subplots(2, 2, figsize=(7.2, 5.6), sharey=True, gridspec_kw={"wspace": 0.25, "hspace": 0.45})
axes = grid.ravel()
for ax, (title, key, is_or, ref, cell, scale) in zip(axes, panels):
    for w, col, mk, dy, lab in SER:
        for i, (_, k) in enumerate(ROWS):
            x = cell(w, k)
            if x is None: continue
            c, m, y = (GREY, "D", ROW_Y[i]) if k == "REVIEWS" else (col, mk, ROW_Y[i] + dy)
            if is_or:
                kk = key[1] if k == "REVIEWS" else key[0]
                o = x[kk]; est, (lo, hi) = o["or"], o["ci"]
            else:
                est, (lo, hi) = scale * x["diff"], [scale * v for v in x["diff_ci"]]
            ax.plot([lo, hi], [y] * 2, color=c, lw=1.5, solid_capstyle="round")
            ax.plot(est, y, marker=m, ms=4.5, color=c, mec="white", mew=0.7, ls="none", label=lab if (i == 0 and k != "REVIEWS") else None)
    ax.axvline(ref, color=DARK, lw=1.1, ls=(0, (3, 2)), zorder=1.5)
    if is_or:
        ax.set_xscale("log"); ax.set_xlim(0.3, 2.6); ax.set_xticks([0.5, 1, 2]); ax.set_xticklabels(["0.5", "1", "2"])
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_title(title, fontsize=11.5, color=DARK); ax.tick_params(colors="#55554f", length=2)
    ax.grid(axis="x", color="#e6e6e1", lw=0.5); ax.set_axisbelow(True)
axes[0].set_yticks(ROW_Y); axes[0].set_yticklabels([r[0] for r in ROWS]); axes[0].invert_yaxis()
axes[0].axhline(4.8, color="#d0d0ca", lw=0.6)
for ax in axes[1:]: ax.axhline(4.8, color="#d0d0ca", lw=0.6)
h, l = axes[0].get_legend_handles_labels()
h.append(plt.Line2D([], [], color=GREY, marker="D", ms=4.5, mec="white", lw=1.5)); l.append("Reviews vs other controls, CD$_5$ window")
fig.legend(h, l, loc="lower center", ncol=1, frameon=False, bbox_to_anchor=(0.55, 0.0), fontsize=11.5)
fig.subplots_adjust(bottom=0.20, left=0.20, right=0.99, top=0.90)
for ext in ("pdf", "png"):
    fig.savefig(run.dir / f"fig1_forest.{ext}", dpi=200, metadata={"CreationDate": None} if ext == "pdf" else None)
plt.close(fig)

# ---------------- Fig. 2 -------------------------------------------------------------------------------------
et = pd.read_csv(HERE / "e09_pretrend" / "runs" / R9 / "event_time_balanced.csv")
e9 = load("e09_pretrend", R9)
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6), gridspec_kw={"wspace": 0.40})
ax = axes[0]
if R12:
    paired_path = HERE / "e12_diagnostics" / "runs" / R12 / "paired_event.csv"
    paired = pd.read_csv(paired_path)
    if not (paired.tau.equals(et.tau) and paired.n_pairs.equals(et.n_pairs)
            and ((paired.paired_diff - et.paired_diff).abs() < 1e-12).all()):
        raise ValueError("Paired figure input does not reproduce P9 points and counts")
    ax.errorbar(paired.tau, paired.paired_diff,
                yerr=[paired.paired_diff - paired.ci_lo, paired.ci_hi - paired.paired_diff],
                color=ORANGE, marker="o", ms=4, lw=1.4, capsize=3)
    ax.axhline(0, color="#8a8a85", lw=0.7, zorder=0)
    ax.set_ylabel("Mean paired DI$_{nok}$ gap\n(retracted − controls)", fontsize=11.5)
    ax.set_title("Citation-composition gap\n(95% intervals)", fontsize=11.5, color=DARK)
    run.log("paired_event_sha256", sha256(paired_path))
    run.log("plotted_paired_points", paired.to_dict("records"))
else:
    ax.plot(et.tau, et.dinok_ret, color=ORANGE, marker="o", ms=4, lw=1.4, label="Retracted papers")
    ax.plot(et.tau, et.dinok_ctl, color=GREY, marker="s", ms=3.5, lw=1.4, label="Controls (same journal × year)")
    ax.set_ylabel("Mean DI$_{nok}$ from that year's citing papers", fontsize=11.5)
    ax.set_title("DI$_{nok}$\n(citing papers ignore the references)", fontsize=11.5, color=DARK)
ax2 = axes[1]
ax2.plot(et.tau, et.cites_ret, color=ORANGE, marker="o", ms=4, lw=1.4, label="Retracted papers")
ax2.plot(et.tau, et.cites_ctl, color=GREY, marker="s", ms=3.5, lw=1.4, label="Controls\n(same journal × year)")
ax2.set_ylabel("Citing papers per paper and year", fontsize=11.5); ax2.set_ylim(bottom=0)
ax2.set_title("Citations", fontsize=11.5, color=DARK)
for a in axes:
    a.axvline(0, color="#8a8a85", lw=0.8, ls=(0, (3, 2)), zorder=0); a.set_xticks(range(-3, 4))
    a.set_xlabel("Years relative to the\nfirst retraction notice", fontsize=11.5)
    a.tick_params(colors="#55554f", length=2); a.grid(axis="y", color="#e6e6e1", lw=0.5); a.set_axisbelow(True)
if R12:
    handles, labels = ax2.get_legend_handles_labels()
    fig.legend(handles, [label.replace("\n", " ") for label in labels], frameon=False, fontsize=11.5,
               loc="lower center", ncol=2, bbox_to_anchor=(0.55, 0.01))
else:
    axes[0].legend(frameon=False, fontsize=11.5, loc="upper left")
fig.subplots_adjust(bottom=0.34 if R12 else 0.27, left=0.15, right=0.99, top=0.82)
for ext in ("pdf", "png"):
    fig.savefig(run.dir / f"fig2_event.{ext}", dpi=200, metadata={"CreationDate": None} if ext == "pdf" else None)
run.log("balanced_papers", int(et.n_ret.iloc[0]))
run.log("figures", ["fig1_forest.pdf", "fig1_forest.png", "fig2_event.pdf", "fig2_event.png"])
run.finish()
