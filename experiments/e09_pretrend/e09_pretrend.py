"""E9: post hoc round 3 (POSTHOC.md P9): pre-trend checks of the P6 before/after-retraction comparison.
(a) placebo event at R - 3 vs the real event on the same papers; (b) event-time means on a balanced set of papers.
Verifies the frozen E3/E7 hashes and reproduces the P6 point estimate of the given E8 run first. Group-level outputs.
usage: python e09_pretrend.py RUN_ID E2_CD3 E3_CD3 E7 E8
Outputs in the run folder: results.json, event_time_balanced.csv.
"""
import sys, json
import numpy as np, pandas as pd
from pathlib import Path
from common import Run, E_DATA, E_ROOT, sha256

SEED, NBOOT, Y0, Y_LAST = 20261109, 2000, 2000, 2022
EXP = Path(__file__).resolve().parents[1]
A = dict(zip(["e2_cd3", "e3_cd3", "e7", "e8"], sys.argv[2:6])); assert len(A) == 4, __doc__
run = Run(sys.argv[1], __file__, {**A, "seed": SEED, "n_boot": NBOOT, "posthoc_sha256": sha256(E_ROOT / "POSTHOC.md")})
ST = ["journal_id", "pub_year"]
info = lambda exp, rid: json.loads((EXP / exp / "runs" / rid / "run.json").read_text())

def frozen(exp, sub, rid, fname):
    f = E_DATA / sub / rid / fname
    assert sha256(f) == info(exp, rid)["results"]["frozen"][fname]["sha256"], f"{f} changed after freezing"
    return f

assert info("e03_cd5", A["e3_cd3"])["config"]["e2_run"] == A["e2_cd3"]
frozen("e03_cd5", "e03", A["e3_cd3"], "scores.parquet")
D3 = pd.read_parquet(E_DATA / "e02" / A["e2_cd3"] / "labels.parquet")
Y = pd.read_parquet(frozen("e07_yearly", "e07", A["e7"], "yearly.parquet"))
e8 = json.loads((EXP / "e08_posthoc2" / "runs" / A["e8"] / "results.json").read_text())["P6_before_after"]
run.log("frozen_inputs_verified", True)

# --- yearly arrays, notices excluded (as P6 main) -------------------------------------------------------------
ids = np.array(sorted(set(D3.iid[D3.grp.isin(["retracted", "control"])])))
pos = pd.Series(np.arange(len(ids)), index=ids)
Yp = Y[Y.iid.isin(ids) & (Y.y <= Y_LAST)]
NY = Y_LAST - Y0 + 1
arr = {}
for c in ("ni", "nj", "ni_ntc", "nj_ntc"):
    a = np.zeros((len(ids), NY)); np.add.at(a, (pos[Yp.iid].to_numpy(), Yp.y.to_numpy() - Y0), Yp[c].to_numpy()); arr[c] = a
NI, NJ = arr["ni"] - arr["ni_ntc"], arr["nj"] - arr["nj_ntc"]
cum = lambda x: np.concatenate([np.zeros((x.shape[0], 1)), np.cumsum(x, axis=1)], axis=1)
CI, CJ = cum(NI), cum(NJ)
def wsum(rows, y0, y1):
    a, b = y0 - Y0, y1 - Y0 + 1
    return CI[rows, b] - CI[rows, a], CJ[rows, b] - CJ[rows, a]
dinok = lambda ni_, nj_: np.where(ni_ + nj_ > 0, (ni_ - nj_) / np.maximum(ni_ + nj_, 1), np.nan)

ret3 = D3[D3.grp == "retracted"].drop_duplicates("iid").copy()
ret3["R"] = pd.to_datetime(ret3.first_notice).dt.year
ev = ret3[(ret3.R >= ret3.pub_year + 1) & (ret3.R <= Y_LAST - 1)].sort_values("iid")
ctl3 = D3[D3.grp == "control"].drop_duplicates("iid")
ctl_rows = {k: pos[g.iid].to_numpy() for k, g in ctl3.groupby(ST)}

REAL = lambda t, R: (max(t, R - 3), R - 1, R + 1, min(R + 3, Y_LAST))
PLACEBO = lambda t, R: (max(t, R - 6), R - 4, R - 2, R - 1)          # F = R - 3: before F-3..F-1, after F+1..R-1

def did(E, windows):
    rows = []
    for r in E.itertuples():
        b0, b1, a0, a1 = windows(r.pub_year, r.R); i = pos[r.iid]; cr = ctl_rows.get((r.journal_id, r.pub_year))
        bi, bj = wsum(i, b0, b1); ai, aj = wsum(i, a0, a1)
        rec = {"stratum": f"{r.journal_id}|{r.pub_year}", "cls": r.cls, "d_r": float(dinok(ai, aj) - dinok(bi, bj)), "d_c": np.nan}
        if cr is not None and len(cr):
            cbi, cbj = wsum(cr, b0, b1); cai, caj = wsum(cr, a0, a1); dc = dinok(cai, caj) - dinok(cbi, cbj)
            if np.isfinite(dc).any(): rec["d_c"] = float(np.nanmean(dc))
        rows.append(rec)
    T = pd.DataFrame(rows); T["did"] = T.d_r - T.d_c
    return T

root = np.random.SeedSequence(SEED)
def boot_mean(T, col="did"):
    d = T[T[col].notna()]; g = d.groupby("stratum")[col].agg(["sum", "size"]).sort_index()
    s, n = g["sum"].to_numpy(), g["size"].to_numpy()
    idx = np.random.default_rng(root.spawn(1)[0]).integers(0, len(g), size=(NBOOT, len(g)))
    bt = s[idx].sum(1) / n[idx].sum(1)
    return {"n": int(n.sum()), "strata": len(g), "mean": float(s.sum() / n.sum()),
            "ci": [float(np.quantile(bt, 0.025)), float(np.quantile(bt, 0.975))],
            "mean_change_retracted": float(d.d_r.mean()), "mean_change_controls": float(d.d_c.mean())}

# reproduce P6 (point estimate and n) before anything new
T6 = did(ev, REAL); ok = T6.did.notna()
assert int(ok.sum()) == e8["without_notices"]["did"]["n"] and abs(float(T6.did[ok].mean()) - e8["without_notices"]["did"]["mean"]) < 1e-12
run.log("reproduces_P6_of", A["e8"])

res = {"population": {"P6": len(ev)}}
sub = ev[ev.R >= ev.pub_year + 4]
res["population"]["R_ge_t_plus_4"] = len(sub)
res["a_real_same_papers"] = boot_mean(did(sub, REAL))
res["a_placebo_R_minus_3"] = boot_mean(did(sub, PLACEBO))
res["a_by_class"] = {k: {"real": boot_mean(did(g, REAL)), "placebo": boot_mean(did(g, PLACEBO))} for k, g in sub.groupby("cls")}
run.log("P9a_real", res["a_real_same_papers"]); run.log("P9a_placebo", res["a_placebo_R_minus_3"])

# (b) balanced event time: tau = -3..+3 all inside [t, 2022]
bal = ev[(ev.R >= ev.pub_year + 3) & (ev.R <= Y_LAST - 3)]
res["population"]["balanced"] = len(bal)
recs = []
for r in bal.itertuples():
    cr = ctl_rows.get((r.journal_id, r.pub_year)); i = pos[r.iid]
    for tau in range(-3, 4):
        j = r.R + tau - Y0; nr = NI[i, j] + NJ[i, j]
        rec = {"tau": tau, "dinok_r": (NI[i, j] - NJ[i, j]) / nr if nr > 0 else np.nan, "cites_r": nr, "dinok_c": np.nan, "cites_c": np.nan}
        if cr is not None and len(cr):
            nc = NI[cr, j] + NJ[cr, j]; dc = np.where(nc > 0, (NI[cr, j] - NJ[cr, j]) / np.maximum(nc, 1), np.nan)
            rec.update({"dinok_c": float(np.nanmean(dc)) if np.isfinite(dc).any() else np.nan, "cites_c": float(nc.mean())})
        recs.append(rec)
E = pd.DataFrame(recs); E["pair"] = E.dinok_r - E.dinok_c
et = E.groupby("tau").agg(n_ret=("cites_r", "size"), n_ret_cited=("dinok_r", "count"), dinok_ret=("dinok_r", "mean"),
                          n_ctl_cited=("dinok_c", "count"), dinok_ctl=("dinok_c", "mean"), n_pairs=("pair", "count"),
                          paired_diff=("pair", "mean"), cites_ret=("cites_r", "mean"), cites_ctl=("cites_c", "mean"))
et.to_csv(run.dir / "event_time_balanced.csv")
res["b_event_time_balanced"] = "event_time_balanced.csv"
(run.dir / "results.json").write_text(json.dumps(res, indent=1, default=float))
run.log("outputs", ["results.json", "event_time_balanced.csv"])
run.finish()
