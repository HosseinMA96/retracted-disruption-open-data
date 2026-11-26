"""E4: evaluation of SPEC.md §6. Checks the frozen E3 scores, then joins the E2 labels. Group-level outputs only.
usage: python e04_eval.py RUN_ID E2_RUN_ID E3_RUN_ID
Outputs in the run folder: results.json (all estimates), context_by_year.csv, thresholds.csv.
"""
import sys, json
import numpy as np, pandas as pd
from pathlib import Path
from common import Run, E_DATA, E_ROOT, sha256

SEED, NBOOT = 20261109, 2000
E2, E3 = sys.argv[2], sys.argv[3]
e3_info = json.loads((Path(__file__).resolve().parents[1] / "e03_cd5" / "runs" / E3 / "run.json").read_text())
frozen = e3_info["results"]["frozen"]["scores.parquet"]["sha256"]
scores_f, labels_f = E_DATA / "e03" / E3 / "scores.parquet", E_DATA / "e02" / E2 / "labels.parquet"
run = Run(sys.argv[1], __file__, {"e2_run": E2, "e3_run": E3, "seed": SEED, "n_boot": NBOOT,
                                   "spec_sha256": sha256(E_ROOT / "SPEC.md")})
assert e3_info["config"]["e2_run"] == E2, "E3 scores were computed for another E2 run"
assert sha256(scores_f) == frozen, "scores changed after freezing"
run.log("frozen_scores_verified", True)

S = pd.read_parquet(scores_f)
L = pd.read_parquet(labels_f)
D = L.merge(S.drop(columns="pub_year"), on="iid", how="left", validate="many_to_one")
assert D.ni_w0.notna().all(), "a labelled paper has no score row"
rng_root = np.random.SeedSequence(SEED)

def wilson(k, n, z=1.96):
    if n == 0: return [None, None, None]
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [p, c - h, c + h]

def mh_or(strata, exposed, y):
    g = pd.DataFrame({"s": strata, "e": exposed.astype(int), "y": y.astype(int)})
    g["a"] = g.e * g.y; g["b"] = g.e * (1 - g.y); g["c"] = (1 - g.e) * g.y; g["d"] = (1 - g.e) * (1 - g.y)
    t = g.groupby("s")[["a", "b", "c", "d"]].sum(); n = t.sum(axis=1)
    R, Sx = t.a * t.d / n, t.b * t.c / n
    if Sx.sum() == 0: return {"or": None}
    OR = R.sum() / Sx.sum()
    # Robins-Breslow-Greenland variance of log OR
    P, Q = (t.a + t.d) / n, (t.b + t.c) / n
    v = (P * R).sum() / (2 * R.sum() ** 2) + ((P * Sx + Q * R).sum()) / (2 * R.sum() * Sx.sum()) + (Q * Sx).sum() / (2 * Sx.sum() ** 2)
    se = np.sqrt(v)
    return {"or": OR, "ci": [OR * np.exp(-1.96 * se), OR * np.exp(1.96 * se)], "exposed_events": int(t.a.sum()),
            "exposed_n": int((t.a + t.b).sum()), "control_events": int(t.c.sum()), "control_n": int((t.c + t.d).sum())}

def compare(ret, ctl, w, strata_cols, tag):
    """Stratified mean difference of CD (retracted - controls), weighted by retracted papers; bootstrap over strata."""
    cd = f"cd_{w}"
    r, c = ret[ret[cd].notna()], ctl[ctl[cd].notna()]
    res = {"retracted_n": len(ret), "retracted_defined": len(r), "controls_n": len(ctl), "controls_defined": len(c)}
    gr = r.groupby(strata_cols)[cd].agg(["mean", "size"]); gc = c.groupby(strata_cols)[cd].agg(["mean", "size"])
    m = gr.join(gc, lsuffix="_r", rsuffix="_c", how="inner").sort_index()
    res["strata_used"] = len(m); res["retracted_in_used_strata"] = int(m.size_r.sum())
    if len(m) == 0: return res
    diff = (m.mean_r - m.mean_c).to_numpy(); wt = m.size_r.to_numpy()
    est = float(np.average(diff, weights=wt))
    rng = np.random.default_rng(rng_root.spawn(1)[0])
    idx = rng.integers(0, len(m), size=(NBOOT, len(m)))
    boots = (diff[idx] * wt[idx]).sum(1) / wt[idx].sum(1)
    res.update({"mean_cd_retracted": float(np.average(m.mean_r, weights=wt)), "mean_cd_controls_matched": float(np.average(m.mean_c, weights=wt)),
                "diff": est, "diff_ci": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]})
    both = pd.concat([r.assign(e=1), c.assign(e=0)])
    key = both[strata_cols].astype(str).agg("|".join, axis=1)
    res["mh_cd_pos"] = mh_or(key, both.e, both[cd] > 0)
    for p in ("p95", "p99"):
        thr = both.pub_year.map(TH[w][p])
        res[f"mh_top_{p}"] = mh_or(key, both.e, both[cd] >= thr)
        res[f"share_top_{p}_retracted"] = wilson(int((r[cd] >= r.pub_year.map(TH[w][p])).sum()), len(r))
        res[f"share_top_{p}_controls"] = wilson(int((c[cd] >= c.pub_year.map(TH[w][p])).sum()), len(c))
    res["cd1_share_retracted"] = float(r[f"cd1_{w}"].mean()); res["cd1_share_controls"] = float(c[f"cd1_{w}"].mean())
    run.log(tag, {k: res[k] for k in ("retracted_defined", "strata_used", "diff", "diff_ci") if k in res})
    return res

# thresholds from the context sample (SPEC §6 RQ3), per window and publication year
ctx = D[D.grp == "context"]
TH = {w: {p: ctx[ctx[f"cd_{w}"].notna()].groupby("pub_year")[f"cd_{w}"].quantile(qq).to_dict()
          for p, qq in (("p95", 0.95), ("p99", 0.99))} for w in ("w0", "w1")}
pd.DataFrame({f"{w}_{p}": pd.Series(TH[w][p]) for w in TH for p in TH[w]}).rename_axis("pub_year").to_csv(run.dir / "thresholds.csv")

ret_all, ctl = D[D.grp == "retracted"], D[D.grp == "control"]
ST = ["journal_id", "pub_year"]
out = {"primary": compare(ret_all[ret_all.primary_set == True], ctl, "w0", ST, "RQ1_primary")}
out["by_class"] = {k: compare(g, ctl, "w0", ST, f"RQ2_{k}") for k, g in ret_all[ret_all.primary_set == True].groupby("cls")}
P = ret_all[ret_all.primary_set == True]
rob = {}
rob["a_no_cd1"] = compare(P[~P.cd1_w0], ctl[~ctl.cd1_w0], "w0", ST, "rob_a_no_cd1")
rob["b_no_reviews"] = compare(P[~P.review], ctl[~ctl.review], "w0", ST, "rob_b_no_reviews")
both = pd.concat([P, ctl]); dec = pd.qcut(both.n_refs.rank(method="first"), 10, labels=False)
rob["c_ref_deciles"] = compare(P.assign(dec=dec.loc[P.index]), ctl.assign(dec=dec.loc[ctl.index]), "w0", ST + ["dec"], "rob_c_ref_deciles")
rob["d_window_t1_t5"] = compare(P, ctl, "w1", ST, "rob_d_window_w1")
rob["e_secondary_all_retracted"] = compare(ret_all, ctl, "w0", ST, "rob_e_secondary")
rob["f_ge5_citations"] = compare(P[P.cites_w0 >= 5], ctl[ctl.cites_w0 >= 5], "w0", ST, "rob_f_ge5_cites")
out["robustness"] = rob

cy = ctx.groupby("pub_year").agg(n=("iid", "size"), defined=("cd_w0", lambda s: int(s.notna().sum())),
                                  mean_cd=("cd_w0", "mean"), cd1_share=("cd1_w0", "mean"))
cy["mean_cd_without_cd1"] = ctx[~ctx.cd1_w0].groupby("pub_year").cd_w0.mean()
cy.to_csv(run.dir / "context_by_year.csv")
(run.dir / "results.json").write_text(json.dumps(out, indent=1, default=float))
run.log("outputs", ["results.json", "context_by_year.csv", "thresholds.csv"])
run.finish()
