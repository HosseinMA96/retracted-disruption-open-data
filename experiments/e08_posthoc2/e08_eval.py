"""E8: post hoc round 2 (POSTHOC.md P3-P8). Group-level outputs only.
Order: (1) verify the frozen E3 and E7 hashes; (2) replay the E4 analyses in E4's exact order and seeds and stop unless
every v1 estimate is reproduced; (3) P3 equivalence, P4 reviews, P5 DI_nok, P7 sign shift, P8 notices, P6 before/after.
usage: python e08_eval.py RUN_ID E2_CD5 E3_CD5 E4_CD5 E2_CD3 E3_CD3 E4_CD3 E7
Outputs in the run folder: results.json, event_time.csv (group means by year relative to retraction).
"""
import sys, json, warnings
import numpy as np, pandas as pd
from pathlib import Path
from scipy.stats import norm
from statsmodels.discrete.conditional_models import ConditionalLogit
from common import Run, E_DATA, E_ROOT, sha256

warnings.filterwarnings("ignore", message="The 'lsuffix' and 'rsuffix' keywords")   # compare() keeps e04's join call verbatim

SEED, NBOOT = 20261109, 2000
OR_MARGIN, DIFF_MARGIN_SD, Z90 = (0.80, 1.25), 0.1, norm.ppf(0.95)
Y0, Y_LAST = 2000, 2022                      # P6: citing years used (2023 is incomplete)
EXP = Path(__file__).resolve().parents[1]
A = dict(zip(["e2_cd5", "e3_cd5", "e4_cd5", "e2_cd3", "e3_cd3", "e4_cd3", "e7"], sys.argv[2:9]))
assert len(A) == 7, __doc__
run = Run(sys.argv[1], __file__, {**A, "seed": SEED, "n_boot": NBOOT, "or_margin": OR_MARGIN, "diff_margin_sd": DIFF_MARGIN_SD,
                                   "spec_sha256": sha256(E_ROOT / "SPEC.md"), "posthoc_sha256": sha256(E_ROOT / "POSTHOC.md")})
ST = ["journal_id", "pub_year"]
info = lambda exp, rid: json.loads((EXP / exp / "runs" / rid / "run.json").read_text())


def frozen(exp, sub, rid, fname):
    f = E_DATA / sub / rid / fname
    assert sha256(f) == info(exp, rid)["results"]["frozen"][fname]["sha256"], f"{f} changed after freezing"
    return f


def load(e2, e3):
    assert info("e03_cd5", e3)["config"]["e2_run"] == e2, "E3 scores were computed for another E2 run"
    S = pd.read_parquet(frozen("e03_cd5", "e03", e3, "scores.parquet"))
    L = pd.read_parquet(E_DATA / "e02" / e2 / "labels.parquet")
    D = L.merge(S.drop(columns="pub_year"), on="iid", how="left", validate="many_to_one")
    assert D.ni_w0.notna().all(), "a labelled paper has no score row"
    D["dinok_w0"] = ((D.ni_w0 - D.nj_w0) / D.cites_w0).where(D.cites_w0 > 0)
    return D


class Seeder:  # e04 draws one child of SeedSequence(SEED) per comparison, in call order
    def __init__(self): self.root = np.random.SeedSequence(SEED)
    def rng(self): return np.random.default_rng(self.root.spawn(1)[0])


def wilson(k, n, z=1.96):  # verbatim from e04_eval.py
    if n == 0: return [None, None, None]
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [p, c - h, c + h]


def mh_or(strata, exposed, y):  # e04_eval.py, plus the 90% interval and the TOST p-value (P3)
    g = pd.DataFrame({"s": strata, "e": exposed.astype(int), "y": y.astype(int)})
    g["a"] = g.e * g.y; g["b"] = g.e * (1 - g.y); g["c"] = (1 - g.e) * g.y; g["d"] = (1 - g.e) * (1 - g.y)
    t = g.groupby("s")[["a", "b", "c", "d"]].sum(); n = t.sum(axis=1)
    R, Sx = t.a * t.d / n, t.b * t.c / n
    if Sx.sum() == 0: return {"or": None}
    OR = R.sum() / Sx.sum()
    counts = {"exposed_events": int(t.a.sum()), "exposed_n": int((t.a + t.b).sum()),
              "control_events": int(t.c.sum()), "control_n": int((t.c + t.d).sum())}
    if R.sum() == 0: return {"or": 0.0, "ci": None, "ci90": None, "tost_p": None, "equivalent": False, "min_margin": None, **counts}
    P, Q = (t.a + t.d) / n, (t.b + t.c) / n
    v = (P * R).sum() / (2 * R.sum() ** 2) + ((P * Sx + Q * R).sum()) / (2 * R.sum() * Sx.sum()) + (Q * Sx).sum() / (2 * Sx.sum() ** 2)
    se = np.sqrt(v); lo, hi = np.log(OR_MARGIN)
    p_tost = max(1 - norm.cdf((np.log(OR) - lo) / se), 1 - norm.cdf((hi - np.log(OR)) / se))
    ci90 = [OR * np.exp(-Z90 * se), OR * np.exp(Z90 * se)]
    return {"or": OR, "ci": [OR * np.exp(-1.96 * se), OR * np.exp(1.96 * se)], "ci90": ci90, "se_log": se,
            "tost_p": p_tost, "equivalent": bool(ci90[0] > OR_MARGIN[0] and ci90[1] < OR_MARGIN[1]),
            "min_margin": max(ci90[1], 1 / ci90[0]), **counts}


def compare(ret, ctl, col, strata, th, seeder, margin=None):
    """e04's compare() for any score column: stratified mean difference (retracted - controls) weighted by retracted
    papers, bootstrap over strata (95% and 90% intervals from the same draws), MH odds ratios for score > 0 and for the
    yearly top 5% / 1% thresholds th[p][pub_year]. margin: equivalence margin for the difference (P3)."""
    r, c = ret[ret[col].notna()], ctl[ctl[col].notna()]
    res = {"retracted_n": len(ret), "retracted_defined": len(r), "controls_n": len(ctl), "controls_defined": len(c)}
    gr = r.groupby(strata)[col].agg(["mean", "size"]); gc = c.groupby(strata)[col].agg(["mean", "size"])
    m = gr.join(gc, lsuffix="_r", rsuffix="_c", how="inner").sort_index()
    res["strata_used"] = len(m); res["retracted_in_used_strata"] = int(m.size_r.sum())
    if len(m) == 0: return res
    diff = (m.mean_r - m.mean_c).to_numpy(); wt = m.size_r.to_numpy()
    est = float(np.average(diff, weights=wt))
    rng = seeder.rng()
    idx = rng.integers(0, len(m), size=(NBOOT, len(m)))
    boots = (diff[idx] * wt[idx]).sum(1) / wt[idx].sum(1)
    res.update({"mean_retracted": float(np.average(m.mean_r, weights=wt)), "mean_controls_matched": float(np.average(m.mean_c, weights=wt)),
                "diff": est, "diff_ci": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))],
                "diff_ci90": [float(np.quantile(boots, 0.05)), float(np.quantile(boots, 0.95))]})
    res["diff_min_margin"] = max(abs(res["diff_ci90"][0]), abs(res["diff_ci90"][1]))
    if margin is not None:
        res["diff_margin"] = margin
        res["diff_equivalent"] = bool(-margin < res["diff_ci90"][0] and res["diff_ci90"][1] < margin)
    both = pd.concat([r.assign(e=1), c.assign(e=0)])
    key = both[strata].astype(str).agg("|".join, axis=1)
    res["mh_pos"] = mh_or(key, both.e, both[col] > 0)
    for p in ("p95", "p99"):
        res[f"mh_top_{p}"] = mh_or(key, both.e, both[col] >= both.pub_year.map(th[p]))
        res[f"share_top_{p}_retracted"] = wilson(int((r[col] >= r.pub_year.map(th[p])).sum()), len(r))
        res[f"share_top_{p}_controls"] = wilson(int((c[col] >= c.pub_year.map(th[p])).sum()), len(c))
    return res


def thresholds(ctx, col):
    d = ctx[ctx[col].notna()]
    return {p: d.groupby("pub_year")[col].quantile(qq).to_dict() for p, qq in (("p95", 0.95), ("p99", 0.99))}


def replay_e04(D, e4_run, tag):
    """E4's analyses in E4's order (same seeds); asserts that every estimate equals E4's results.json."""
    ctx = D[D.grp == "context"]
    TH = {w: thresholds(ctx, f"cd_{w}") for w in ("w0", "w1")}
    sd = Seeder(); margin = DIFF_MARGIN_SD * float(ctx.cd_w0.std())
    ret_all, ctl = D[D.grp == "retracted"], D[D.grp == "control"]
    P = ret_all[ret_all.primary_set == True]
    out = {"primary": compare(P, ctl, "cd_w0", ST, TH["w0"], sd, margin)}
    out["by_class"] = {k: compare(g, ctl, "cd_w0", ST, TH["w0"], sd, margin) for k, g in P.groupby("cls")}
    rob = {}
    rob["a_no_cd1"] = compare(P[~P.cd1_w0], ctl[~ctl.cd1_w0], "cd_w0", ST, TH["w0"], sd)
    rob["b_no_reviews"] = compare(P[~P.review], ctl[~ctl.review], "cd_w0", ST, TH["w0"], sd)
    both = pd.concat([P, ctl]); dec = pd.qcut(both.n_refs.rank(method="first"), 10, labels=False)
    rob["c_ref_deciles"] = compare(P.assign(dec=dec.loc[P.index]), ctl.assign(dec=dec.loc[ctl.index]), "cd_w0", ST + ["dec"], TH["w0"], sd)
    rob["d_window_t1_t5"] = compare(P, ctl, "cd_w1", ST, TH["w1"], sd)
    rob["e_secondary_all_retracted"] = compare(ret_all, ctl, "cd_w0", ST, TH["w0"], sd, margin)
    rob["f_ge5_citations"] = compare(P[P.cites_w0 >= 5], ctl[ctl.cites_w0 >= 5], "cd_w0", ST, TH["w0"], sd)
    out["robustness"] = rob
    ref = json.loads((EXP / "e04_eval" / "runs" / e4_run / "results.json").read_text())
    pairs = [("primary", out["primary"], ref["primary"])] + [(f"class {k}", out["by_class"][k], ref["by_class"][k]) for k in ref["by_class"]] \
        + [(f"robustness {k}", rob[k], ref["robustness"][k]) for k in ref["robustness"]]
    for name, a, b in pairs:
        assert a["retracted_defined"] == b["retracted_defined"] and a["strata_used"] == b["strata_used"], (tag, name)
        assert abs(a["diff"] - b["diff"]) < 1e-12 and np.allclose(a["diff_ci"], b["diff_ci"], rtol=0, atol=1e-12), (tag, name, "diff")
        for k_new, k_old in (("mh_pos", "mh_cd_pos"), ("mh_top_p95", "mh_top_p95"), ("mh_top_p99", "mh_top_p99")):
            assert (a[k_new]["or"] is None and b[k_old]["or"] is None) or abs(a[k_new]["or"] - b[k_old]["or"]) < 1e-9, (tag, name, k_new)
    run.log(f"replay_{tag}_reproduces_{e4_run}", f"{len(pairs)} comparisons identical")
    return out, TH, margin, sd


# ===== 1-2. frozen inputs, replay of E4 =========================================================================
D5, D3 = load(A["e2_cd5"], A["e3_cd5"]), load(A["e2_cd3"], A["e3_cd3"])
e7 = info("e07_yearly", A["e7"])
assert set(e7["config"]["e2_runs"]) >= {A["e2_cd5"], A["e2_cd3"]}, "E7 counts do not cover both populations"
Y = pd.read_parquet(frozen("e07_yearly", "e07", A["e7"], "yearly.parquet"))
run.log("frozen_inputs_verified", True)
R5, TH5, M5, SD5 = replay_e04(D5, A["e4_cd5"], "cd5")
R3, TH3, M3, SD3 = replay_e04(D3, A["e4_cd3"], "cd3")
res = {"P3_equivalence": {}, "P4_reviews": {}, "P5_dinok": {}, "P7_sign_shift": {}, "P8_notices": {}, "P6_before_after": {}}

# ===== P3 equivalence ===========================================================================================
def tost_view(x):
    keep = ("retracted_defined", "diff", "diff_ci", "diff_ci90", "diff_margin", "diff_equivalent", "diff_min_margin")
    o = {k: x[k] for k in keep if k in x}
    for k in ("mh_pos", "mh_top_p95", "mh_top_p99"):
        o[k] = {kk: x[k].get(kk) for kk in ("or", "ci", "ci90", "tost_p", "equivalent", "min_margin")}
    return o
for tag, R, M, D in (("cd5", R5, M5, D5), ("cd3", R3, M3, D3)):
    res["P3_equivalence"][tag] = {"diff_margin": M, "context_sd": M / DIFF_MARGIN_SD, "or_margin": OR_MARGIN,
                                  "primary": tost_view(R["primary"]), "by_class": {k: tost_view(v) for k, v in R["by_class"].items()},
                                  "e_secondary_all_retracted": tost_view(R["robustness"]["e_secondary_all_retracted"])}
run.log("P3_cd5_primary", {k: res["P3_equivalence"]["cd5"]["primary"][k] for k in ("diff_ci90", "diff_margin", "diff_equivalent")}
        | {"top5": res["P3_equivalence"]["cd5"]["primary"]["mh_top_p95"]})

# ===== P4 positive control: reviews vs other never-retracted papers (CD5 controls) ==============================
ctx5, ctl5 = D5[D5.grp == "context"], D5[D5.grp == "control"]
TH5n = thresholds(ctx5, "dinok_w0")
sdx = Seeder(); [sdx.rng() for _ in range(100)]          # P4-P8 draws start after a fixed offset (independent of E4's)
res["P4_reviews"]["cd5"] = compare(ctl5[ctl5.review], ctl5[~ctl5.review], "cd_w0", ST, TH5["w0"], sdx, M5)
res["P4_reviews"]["dinok"] = compare(ctl5[ctl5.review], ctl5[~ctl5.review], "dinok_w0", ST, TH5n, sdx)
res["P4_reviews"]["standardized_diff_cd5"] = res["P4_reviews"]["cd5"]["diff"] / (M5 / DIFF_MARGIN_SD)
run.log("P4_reviews_cd5", {k: res["P4_reviews"]["cd5"][k] for k in ("retracted_defined", "diff", "diff_ci")} | {"or_pos": res["P4_reviews"]["cd5"]["mh_pos"]["or"]})

# ===== P5 DI_nok ==============================================================================================
for tag, D in (("cd5", D5), ("cd3", D3)):
    ctx, ctl = D[D.grp == "context"], D[D.grp == "control"]; P = D[(D.grp == "retracted") & (D.primary_set == True)]
    th = thresholds(ctx, "dinok_w0"); mg = DIFF_MARGIN_SD * float(ctx.dinok_w0.std())
    res["P5_dinok"][tag] = {"thresholds": th, "diff_margin": mg, "context_mean_by_year": ctx.groupby("pub_year").dinok_w0.mean().to_dict(),
                            "share_defined": {"retracted": float(P.dinok_w0.notna().mean()), "controls": float(ctl.dinok_w0.notna().mean())},
                            "primary": compare(P, ctl, "dinok_w0", ST, th, sdx, mg),
                            "by_class": {k: compare(g, ctl, "dinok_w0", ST, th, sdx, mg) for k, g in P.groupby("cls")}}
run.log("P5_cd5_primary", {k: res["P5_dinok"]["cd5"]["primary"][k] for k in ("retracted_defined", "diff", "diff_ci")})

# ===== P7 the sign shift (CD5 primary set) ======================================================================
P5set, ctl5 = D5[(D5.grp == "retracted") & (D5.primary_set == True)], D5[D5.grp == "control"]
both = pd.concat([P5set.assign(e=1), ctl5.assign(e=0)])
key = both[ST].astype(str).agg("|".join, axis=1)
p7 = {"uncited_share": {"retracted": float((P5set.cites_w0 == 0).mean()), "controls": float((ctl5.cites_w0 == 0).mean())},
      "mh_uncited": mh_or(key, both.e, both.cites_w0 == 0),
      "cited_only": compare(P5set[P5set.cites_w0 >= 1], ctl5[ctl5.cites_w0 >= 1], "cd_w0", ST, TH5["w0"], sdx)}
b = both[both.cd_w0.notna()].copy()
b = b[b.groupby(ST).e.transform("max") == 1]                # strata with a primary-set paper (all have controls)
b["top5"] = b.cd_w0 >= b.pub_year.map(TH5["w0"]["p95"]); b["pos"] = b.cd_w0 > 0
b["lrefs"], b["lcites"] = np.log1p(b.n_refs), np.log1p(b.cites_w0)
grp = b.groupby(ST).ngroup().to_numpy()
def clogit(ycol, xcols):
    y = b[ycol].astype(float).to_numpy()
    keep = pd.Series(y).groupby(grp).transform(lambda s: s.nunique() > 1).to_numpy()   # strata without variation carry no information
    m = ConditionalLogit(y[keep], b[xcols].astype(float).to_numpy()[keep], groups=grp[keep]).fit(disp=0)
    be, se = float(m.params[0]), float(m.bse[0])
    return {"or": float(np.exp(be)), "ci": [float(np.exp(be - 1.96 * se)), float(np.exp(be + 1.96 * se))], "n": int(keep.sum()),
            "strata": int(len(np.unique(grp[keep]))), "retracted_in_model": int(b.e.to_numpy()[keep].sum()),
            "coef": [float(v) for v in m.params], "covariates": xcols}
p7["clogit"] = {f"{yc}_{nm}": clogit(yc, xc) for yc in ("pos", "top5")
                for nm, xc in (("unadjusted", ["e"]), ("refs", ["e", "lrefs"]), ("refs_cites", ["e", "lrefs", "lcites"]))}
res["P7_sign_shift"] = p7
run.log("P7_clogit", {k: [round(v["or"], 3)] + [round(x, 3) for x in v["ci"]] for k, v in p7["clogit"].items()})

# ===== P8 editorial-notice citations (CD5 population) ===========================================================
def window_sums(D, lo, hi):
    t = D[["iid", "pub_year"]].drop_duplicates()
    y = Y.merge(t, on="iid"); y = y[(y.y >= y.pub_year + lo) & (y.y <= y.pub_year + hi)]
    return y.groupby("iid")[["ni_ntc", "nj_ntc", "nk_ntc"]].sum()
ws = window_sums(D5, 0, 5)
D5x = D5.join(ws, on="iid").fillna({"ni_ntc": 0, "nj_ntc": 0, "nk_ntc": 0})
D5x["ntc_cites"] = D5x.ni_ntc + D5x.nj_ntc
ni, nj, nk = D5x.ni_w0 - D5x.ni_ntc, D5x.nj_w0 - D5x.nj_ntc, D5x.nk_w0 - D5x.nk_ntc
assert (ni >= 0).all() and (nj >= 0).all() and (nk >= 0).all()
D5x["cdx_w0"] = ((ni - nj) / (ni + nj + nk)).where((ni + nj + nk) > 0)
ret5 = D5x[D5x.grp == "retracted"]; P5x = ret5[ret5.primary_set == True]; ctl5x = D5x[D5x.grp == "control"]
inw = ret5[ret5.primary_set == False]
share = lambda d: {"n": len(d), "with_notice_citation": int((d.ntc_cites > 0).sum()), "share": float((d.ntc_cites > 0).mean()),
                   "mean_notice_citations": float(d.ntc_cites.mean())}
THx = {"w0": thresholds(D5x[D5x.grp == "context"], "cdx_w0")}
res["P8_notices"] = {"cd5_window_share": {"retracted_after_window": share(P5x), "retracted_inside_window": share(inw),
                                          "controls": share(ctl5x), "context": share(D5x[D5x.grp == "context"])},
                     "primary_without_notices": compare(P5x, ctl5x, "cdx_w0", ST, THx["w0"], sdx, M5),
                     "e_all_retracted_without_notices": compare(ret5, ctl5x, "cdx_w0", ST, THx["w0"], sdx, M5),
                     "inside_window_only_with_notices": compare(inw, ctl5x, "cd_w0", ST, TH5["w0"], sdx),
                     "inside_window_only_without_notices": compare(inw, ctl5x, "cdx_w0", ST, THx["w0"], sdx)}
run.log("P8_share_inside_window_with_notice", res["P8_notices"]["cd5_window_share"]["retracted_inside_window"])
run.log("P8_e_or_pos_with_vs_without", [R5["robustness"]["e_secondary_all_retracted"]["mh_pos"]["or"],
                                        res["P8_notices"]["e_all_retracted_without_notices"]["mh_pos"]["or"]])

# ===== P6 before / after the retraction (CD3 population, 2000-2019) ==============================================
ids = np.array(sorted(set(D3.iid[D3.grp.isin(["retracted", "control"])])))
pos = pd.Series(np.arange(len(ids)), index=ids)
Yp = Y[Y.iid.isin(ids) & (Y.y <= Y_LAST)]
NY = Y_LAST - Y0 + 1
arr = {}
for c in ("ni", "nj", "ni_ntc", "nj_ntc"):
    a = np.zeros((len(ids), NY)); np.add.at(a, (pos[Yp.iid].to_numpy(), Yp.y.to_numpy() - Y0), Yp[c].to_numpy())
    arr[c] = a
def cum(x): return np.concatenate([np.zeros((x.shape[0], 1)), np.cumsum(x, axis=1)], axis=1)
CUM = {True: (cum(arr["ni"] - arr["ni_ntc"]), cum(arr["nj"] - arr["nj_ntc"])), False: (cum(arr["ni"]), cum(arr["nj"]))}
YR = {True: (arr["ni"] - arr["ni_ntc"], arr["nj"] - arr["nj_ntc"]), False: (arr["ni"], arr["nj"])}
def wsum(rows, y0, y1, excl):  # window sums [y0, y1] for row indices (arrays broadcast)
    ci, cj = CUM[excl]; a, b2 = np.asarray(y0) - Y0, np.asarray(y1) - Y0 + 1
    return ci[rows, b2] - ci[rows, a], cj[rows, b2] - cj[rows, a]
def dinok(ni_, nj_): return np.where(ni_ + nj_ > 0, (ni_ - nj_) / np.maximum(ni_ + nj_, 1), np.nan)

ret3 = D3[D3.grp == "retracted"].drop_duplicates("iid").copy()
ret3["R"] = pd.to_datetime(ret3.first_notice).dt.year
ev = ret3[(ret3.R >= ret3.pub_year + 1) & (ret3.R <= Y_LAST - 1)].sort_values("iid")
ctl3 = D3[D3.grp == "control"].drop_duplicates("iid")
ctl_rows = {k: pos[g.iid].to_numpy() for k, g in ctl3.groupby(ST)}
res["P6_before_after"]["population"] = {"retracted_cd3_population": len(ret3), "eligible_t1_le_R_le_2021": len(ev),
                                        "by_class": ev.cls.value_counts().to_dict(), "R_range": [int(ev.R.min()), int(ev.R.max())]}

def did(excl):
    rows = []
    for r in ev.itertuples():
        k = (r.journal_id, r.pub_year); cr = ctl_rows.get(k)
        b0, b1, a0, a1 = max(r.pub_year, r.R - 3), r.R - 1, r.R + 1, min(r.R + 3, Y_LAST)
        i = pos[r.iid]
        bi, bj = wsum(i, b0, b1, excl); ai, aj = wsum(i, a0, a1, excl)
        d_r = dinok(ai, aj) - dinok(bi, bj)
        rec = {"iid": r.iid, "stratum": f"{r.journal_id}|{r.pub_year}", "cls": r.cls, "R": r.R, "d_r": float(d_r),
               "cites_before_r": float(bi + bj) / (b1 - b0 + 1), "cites_after_r": float(ai + aj) / (a1 - a0 + 1)}
        if cr is not None and len(cr):
            cbi, cbj = wsum(cr, b0, b1, excl); cai, caj = wsum(cr, a0, a1, excl)
            d_c = dinok(cai, caj) - dinok(cbi, cbj)
            rec.update({"n_ctl": len(cr), "n_ctl_defined": int(np.isfinite(d_c).sum()),
                        "d_c": float(np.nanmean(d_c)) if np.isfinite(d_c).any() else np.nan,
                        "cites_before_c": float((cbi + cbj).mean()) / (b1 - b0 + 1), "cites_after_c": float((cai + caj).mean()) / (a1 - a0 + 1)})
        rows.append(rec)
    T = pd.DataFrame(rows)
    T["did"] = T.d_r - T.d_c
    return T

def boot_mean(T, col, rng):
    d = T[T[col].notna()]
    g = d.groupby("stratum")[col].agg(["sum", "size"]).sort_index()
    s, n = g["sum"].to_numpy(), g["size"].to_numpy()
    idx = rng.integers(0, len(g), size=(NBOOT, len(g)))
    bt = s[idx].sum(1) / n[idx].sum(1)
    return {"n": int(n.sum()), "strata": len(g), "mean": float(s.sum() / n.sum()),
            "ci": [float(np.quantile(bt, 0.025)), float(np.quantile(bt, 0.975))]}

for excl in (True, False):
    T = did(excl); lab = "without_notices" if excl else "with_notices"
    o = {"retracted_with_defined_change": int(T.d_r.notna().sum()), "with_control_change": int((T.d_r.notna() & T.d_c.notna()).sum()),
         "did": boot_mean(T, "did", sdx.rng()),
         "mean_change_retracted": float(T.loc[T.did.notna(), "d_r"].mean()), "mean_change_controls": float(T.loc[T.did.notna(), "d_c"].mean()),
         "citations_per_year": {c: float(T[c].mean()) for c in ("cites_before_r", "cites_after_r", "cites_before_c", "cites_after_c")},
         "by_class": {k: boot_mean(g, "did", sdx.rng()) for k, g in T.groupby("cls")}}
    res["P6_before_after"][lab] = o
    run.log(f"P6_did_{lab}", o["did"])

# event time (without notices): yearly DI_nok of retracted papers and the mean over their stratum controls
ni_y, nj_y = YR[True]
recs = []
for r in ev.itertuples():
    cr = ctl_rows.get((r.journal_id, r.pub_year)); i = pos[r.iid]
    for tau in range(-5, 6):
        y = r.R + tau
        if y < r.pub_year or y > Y_LAST: continue
        j = y - Y0; nr = ni_y[i, j] + nj_y[i, j]
        rec = {"tau": tau, "dinok_r": (ni_y[i, j] - nj_y[i, j]) / nr if nr > 0 else np.nan, "cites_r": nr}
        if cr is not None and len(cr):
            nc = ni_y[cr, j] + nj_y[cr, j]; dc = np.where(nc > 0, (ni_y[cr, j] - nj_y[cr, j]) / np.maximum(nc, 1), np.nan)
            rec.update({"dinok_c": float(np.nanmean(dc)) if np.isfinite(dc).any() else np.nan, "cites_c": float(nc.mean())})
        recs.append(rec)
E = pd.DataFrame(recs)
E["pair"] = E.dinok_r - E.dinok_c
et = E.groupby("tau").agg(n_ret=("cites_r", "size"), n_ret_cited=("dinok_r", "count"), dinok_ret=("dinok_r", "mean"),
                          n_ctl_cited=("dinok_c", "count"), dinok_ctl=("dinok_c", "mean"), n_pairs=("pair", "count"),
                          paired_diff=("pair", "mean"), cites_ret=("cites_r", "mean"), cites_ctl=("cites_c", "mean"))
et.to_csv(run.dir / "event_time.csv")
res["P6_before_after"]["event_time"] = "event_time.csv"

(run.dir / "results.json").write_text(json.dumps(res, indent=1, default=float))
run.log("outputs", ["results.json", "event_time.csv"])
run.finish()
