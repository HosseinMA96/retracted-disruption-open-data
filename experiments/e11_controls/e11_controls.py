"""E11 (POSTHOC.md P11, descriptive): the controls behind the primary comparisons, CD5 and CD3 windows.
Order, per window: (1) verify the frozen E3 hash; (2) reproduce every E4 value used here (and E2's counts of strata and
controls) and stop unless all match; (3) P11: strata and controls of the primary comparison, papers without a defined
score, and shares of controls with score > 0 / >= the yearly top-5% / top-1% threshold, pooled and weighted like the
SPEC mean difference. Group-level outputs only.
usage: python e11_controls.py RUN_ID E2_CD5 E3_CD5 E4_CD5 E2_CD3 E3_CD3 E4_CD3
Output in the run folder: controls.json
"""
import sys, json, warnings
import numpy as np, pandas as pd
from pathlib import Path
from common import Run, E_DATA, E_ROOT, sha256

warnings.filterwarnings("ignore", message="The 'lsuffix' and 'rsuffix' keywords")   # join call kept verbatim from e04

SEED, NBOOT, TOL = 20261109, 2000, 1e-12
EXP = Path(__file__).resolve().parents[1]
A = dict(zip(["e2_cd5", "e3_cd5", "e4_cd5", "e2_cd3", "e3_cd3", "e4_cd3"], sys.argv[2:8]))
assert len(A) == 6, __doc__
run = Run(sys.argv[1], __file__, {**A, "posthoc": "P11", "seed": SEED, "n_boot": NBOOT,
                                   "spec_sha256": sha256(E_ROOT / "SPEC.md"), "posthoc_sha256": sha256(E_ROOT / "POSTHOC.md")})
ST = ["journal_id", "pub_year"]
info = lambda exp, rid: json.loads((EXP / exp / "runs" / rid / "run.json").read_text())


def load(e2, e3):  # as e04/e08: the frozen hash is checked before any label is read
    i3 = info("e03_cd5", e3)
    assert i3["config"]["e2_run"] == e2, "E3 scores were computed for another E2 run"
    f = E_DATA / "e03" / e3 / "scores.parquet"
    assert sha256(f) == i3["results"]["frozen"]["scores.parquet"]["sha256"], f"{f} changed after freezing"
    S = pd.read_parquet(f)
    L = pd.read_parquet(E_DATA / "e02" / e2 / "labels.parquet")
    D = L.merge(S.drop(columns="pub_year"), on="iid", how="left", validate="many_to_one")
    assert D.ni_w0.notna().all(), "a labelled paper has no score row"
    return D


def wilson(k, n, z=1.96):  # verbatim from e04_eval.py
    if n == 0: return [None, None, None]
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [p, c - h, c + h]


def mh_or(strata, exposed, y):  # verbatim from e04_eval.py
    g = pd.DataFrame({"s": strata, "e": exposed.astype(int), "y": y.astype(int)})
    g["a"] = g.e * g.y; g["b"] = g.e * (1 - g.y); g["c"] = (1 - g.e) * g.y; g["d"] = (1 - g.e) * (1 - g.y)
    t = g.groupby("s")[["a", "b", "c", "d"]].sum(); n = t.sum(axis=1)
    R, Sx = t.a * t.d / n, t.b * t.c / n
    if Sx.sum() == 0: return {"or": None}
    OR = R.sum() / Sx.sum()
    P, Q = (t.a + t.d) / n, (t.b + t.c) / n
    v = (P * R).sum() / (2 * R.sum() ** 2) + ((P * Sx + Q * R).sum()) / (2 * R.sum() * Sx.sum()) + (Q * Sx).sum() / (2 * Sx.sum() ** 2)
    se = np.sqrt(v)
    return {"or": OR, "ci": [OR * np.exp(-1.96 * se), OR * np.exp(1.96 * se)], "exposed_events": int(t.a.sum()),
            "exposed_n": int((t.a + t.b).sum()), "control_events": int(t.c.sum()), "control_n": int((t.c + t.d).sum())}


def same(a, b):
    """True if a reproduces b: recursively for dicts and lists, None only equals None, numbers within TOL (relative)."""
    if isinstance(b, dict): return isinstance(a, dict) and a.keys() == b.keys() and all(same(a[k], b[k]) for k in b)
    if isinstance(b, (list, tuple)): return isinstance(a, (list, tuple)) and len(a) == len(b) and all(map(same, a, b))
    if a is None or b is None: return a is None and b is None
    return abs(float(a) - float(b)) <= TOL * max(1.0, abs(float(b)))


def share(y):
    k, n = int(y.sum()), int(len(y))
    return {"k": k, "n": n, "share_ci": wilson(k, n)}


def window(tag, e2, e3, e4, rng):
    D = load(e2, e3)
    v1 = json.loads((EXP / "e04_eval" / "runs" / e4 / "results.json").read_text())["primary"]
    i2 = info("e02_population", e2)["results"]
    # --- (2) reproduce E4 (same code path as e04 compare(), primary set, window w0) and E2's counts ----------------
    ctx = D[D.grp == "context"]
    TH = {p: ctx[ctx.cd_w0.notna()].groupby("pub_year").cd_w0.quantile(q).to_dict() for p, q in (("p95", 0.95), ("p99", 0.99))}
    th1 = pd.read_csv(EXP / "e04_eval" / "runs" / e4 / "thresholds.csv", index_col="pub_year")
    for p in TH:
        assert sorted(TH[p]) == sorted(th1.index) and all(same(TH[p][y], th1.loc[y, f"w0_{p}"]) for y in TH[p]), \
            f"{tag}: yearly {p} thresholds differ from {e4}"
    ret_all, ctl = D[D.grp == "retracted"], D[D.grp == "control"]
    P = ret_all[ret_all.primary_set == True]
    r, c = P[P.cd_w0.notna()], ctl[ctl.cd_w0.notna()]
    gr = r.groupby(ST)["cd_w0"].agg(["mean", "size"]); gc = c.groupby(ST)["cd_w0"].agg(["mean", "size"])
    m = gr.join(gc, lsuffix="_r", rsuffix="_c", how="inner").sort_index()
    both = pd.concat([r.assign(e=1), c.assign(e=0)])
    key = both[ST].astype(str).agg("|".join, axis=1)
    rep = {"retracted_n": len(P), "retracted_defined": len(r), "controls_n": len(ctl), "controls_defined": len(c),
           "strata_used": len(m), "retracted_in_used_strata": int(m.size_r.sum()),
           "mean_cd_controls_matched": float(np.average(m.mean_c, weights=m.size_r)),
           "mh_cd_pos": mh_or(key, both.e, both.cd_w0 > 0)}
    for p in ("p95", "p99"):
        rep[f"mh_top_{p}"] = mh_or(key, both.e, both.cd_w0 >= both.pub_year.map(TH[p]))
        rep[f"share_top_{p}_controls"] = wilson(int((c.cd_w0 >= c.pub_year.map(TH[p])).sum()), len(c))
    bad = [k for k in rep if not same(rep[k], v1[k])]
    strata_all = ret_all[ST].drop_duplicates()
    if len(strata_all) != i2["strata"]: bad.append("e02 strata")
    if len(ctl) != i2["controls"]: bad.append("e02 controls")
    assert not bad, f"{tag}: not reproduced: {bad}"
    run.log(f"{tag}_reproduced", sorted(rep) + ["e02 strata", "e02 controls"])

    # --- (3a) strata and controls ------------------------------------------------------------------------------------
    sk = lambda d: pd.MultiIndex.from_frame(d[ST])
    used = m.index
    ctl_used, c_used = sk(ctl).isin(used), sk(c).isin(used)
    strata_p = P[ST].drop_duplicates()
    out = {"population": {"retracted": len(ret_all), "strata": len(strata_all), "controls": len(ctl),
                          "controls_defined": len(c)},
           "primary": {"papers": len(P), "papers_defined": len(r), "strata_with_primary_paper": len(strata_p),
                       "strata_used": len(m), "papers_in_used_strata": int(m.size_r.sum())},
           "controls_used_strata": {"controls": int(ctl_used.sum()), "controls_defined": int(c_used.sum())},
           "controls_other_strata": {"controls": int((~ctl_used).sum()), "controls_defined": int((~c_used).sum()),
                                     "strata_not_used": len(strata_all) - len(m)},
           "controls_in_strata_with_primary_paper": int(sk(ctl).isin(sk(strata_p)).sum())}

    # --- (3b) papers without a defined score -------------------------------------------------------------------------
    den = D.ni_w0 + D.nj_w0 + D.nk_w0
    assert (D.cd_w0.isna() == (den == 0)).all(), f"{tag}: an undefined score with a non-zero denominator"
    prim = D.primary_set.astype(object).eq(True).to_numpy()      # NULL for rows that are not retracted papers
    g4 = pd.Series(np.where(D.grp == "retracted", np.where(prim, "retracted_primary", "retracted_secondary"), D.grp), index=D.index)
    out["undefined"] = {"label_rows_by_group": {k: int(v) for k, v in D[D.cd_w0.isna()].groupby(g4).size().items()},
                        "label_rows": len(D), "distinct_papers": int(D.iid.nunique()),
                        "distinct_papers_undefined": int(D.loc[D.cd_w0.isna(), "iid"].nunique()),
                        "all_have_zero_denominator": True}

    # --- (3c) shares: retracted in used strata; controls pooled and weighted by scored primary papers per stratum -----
    y_of = {"pos": lambda d: d.cd_w0 > 0, "p95": lambda d: d.cd_w0 >= d.pub_year.map(TH["p95"]),
            "p99": lambda d: d.cd_w0 >= d.pub_year.map(TH["p99"])}
    r_used = r[sk(r).isin(used)]; cu, co = c[c_used], c[~c_used]
    w = m.size_r.to_numpy(float)
    idx = rng.integers(0, len(m), size=(NBOOT, len(m)))
    out["shares"] = {}
    for o, f in y_of.items():
        ps = cu.assign(y=f(cu)).groupby(ST).y.mean().reindex(used).to_numpy(float)
        pr = r_used.assign(y=f(r_used)).groupby(ST).y.mean().reindex(used).to_numpy(float)
        assert not np.isnan(ps).any() and not np.isnan(pr).any()
        est = float(np.average(ps, weights=w)); boots = (ps[idx] * w[idx]).sum(1) / w[idx].sum(1)
        out["shares"][o] = {"retracted_used_strata": share(f(r_used)), "retracted_all_primary_v1": share(f(r)),
                            "controls_weighted": [est, float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))],
                            "retracted_weighted_check": float(np.average(pr, weights=w)),
                            "controls_pooled_used_strata": share(f(cu)), "controls_pooled_other_strata": share(f(co)),
                            "controls_pooled_all_v1": share(f(c))}
        assert abs(out["shares"][o]["retracted_weighted_check"] - f(r_used).mean()) < 1e-12
    out["shares"]["v1_mh_control_counts_are_all_scored_controls"] = (
        rep["mh_cd_pos"]["control_n"] == len(c) and rep["mh_top_p95"]["control_n"] == len(c))
    run.log(f"{tag}_controls_used_strata", out["controls_used_strata"])
    run.log(f"{tag}_undefined", out["undefined"]["label_rows_by_group"])
    run.log(f"{tag}_shares_retracted_vs_controls_weighted",
            {o: [round(out["shares"][o]["retracted_used_strata"]["share_ci"][0], 5),
                 [round(x, 5) for x in out["shares"][o]["controls_weighted"]]] for o in y_of})
    return out


seeds = np.random.SeedSequence(SEED).spawn(2)
res = {"cd5": window("cd5", A["e2_cd5"], A["e3_cd5"], A["e4_cd5"], np.random.default_rng(seeds[0])),
       "cd3": window("cd3", A["e2_cd3"], A["e3_cd3"], A["e4_cd3"], np.random.default_rng(seeds[1]))}
(run.dir / "controls.json").write_text(json.dumps(res, indent=1, default=float))
run.log("outputs", ["controls.json"])
run.finish()
