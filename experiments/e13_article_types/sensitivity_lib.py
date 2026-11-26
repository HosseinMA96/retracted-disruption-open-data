"""P13 estimators following E4/E8; original results are replayed before filtering."""
import numpy as np
import pandas as pd

ST = ["journal_id", "pub_year"]
EXCLUDED = ["D016454", "D000078182", "D017418", "D016421", "D016422", "D016420",
            "D016425", "D016440", "D000075742"]


def is_article(types):
    return bool(types) and "D016428" in types and not set(types).intersection(EXCLUDED)


def matched(ret, ctl, column):
    r, c = ret[ret[column].notna()], ctl[ctl[column].notna()]
    gr = r.groupby(ST)[column].agg(["mean", "size"])
    gc = c.groupby(ST)[column].agg(["mean", "size"])
    m = gr.join(gc, lsuffix="_r", rsuffix="_c", how="inner").sort_index()
    if m.empty:
        raise ValueError("No strata with defined scores in both groups")
    r = r[pd.MultiIndex.from_frame(r[ST]).isin(m.index)]
    c = c[pd.MultiIndex.from_frame(c[ST]).isin(m.index)]
    return r, c, m


def mh_or(strata, exposed, outcome):
    g = pd.DataFrame({"s": strata, "e": exposed.astype(int), "y": outcome.astype(int)})
    g["a"], g["b"] = g.e * g.y, g.e * (1 - g.y)
    g["c"], g["d"] = (1 - g.e) * g.y, (1 - g.e) * (1 - g.y)
    t = g.groupby("s")[["a", "b", "c", "d"]].sum()
    n = t.sum(axis=1)
    r, s = t.a * t.d / n, t.b * t.c / n
    if s.sum() == 0:
        return {"or": None, "ci": None, "status": "No denominator events; odds ratio not estimable"}
    if r.sum() == 0:
        return {"or": 0.0, "ci": None, "status": "No numerator events; confidence interval not estimable"}
    ratio = r.sum() / s.sum()
    p, q = (t.a + t.d) / n, (t.b + t.c) / n
    variance = ((p * r).sum() / (2 * r.sum() ** 2)
                + ((p * s + q * r).sum()) / (2 * r.sum() * s.sum())
                + (q * s).sum() / (2 * s.sum() ** 2))
    se = np.sqrt(variance)
    return {"or": float(ratio), "ci": [float(ratio * np.exp(-1.96 * se)), float(ratio * np.exp(1.96 * se))]}


def compare(ret, ctl, column, thresholds, rng, nboot=2000):
    r, c, m = matched(ret, ctl, column)
    d, w = (m.mean_r - m.mean_c).to_numpy(), m.size_r.to_numpy()
    draws = rng.integers(0, len(m), size=(nboot, len(m)))
    boot = (d[draws] * w[draws]).sum(1) / w[draws].sum(1)
    out = {"retracted_scored": int(ret[column].notna().sum()), "controls_scored": int(ctl[column].notna().sum()),
           "retracted_compared": len(r), "controls_compared": len(c), "strata": len(m),
           "diff": float(np.average(d, weights=w)), "diff_ci": np.quantile(boot, [0.025, 0.975]).tolist()}
    if column.startswith("cd_"):
        both = pd.concat([r.assign(e=1), c.assign(e=0)])
        key = both[ST].astype(str).agg("|".join, axis=1)
        out["positive"] = mh_or(key, both.e, both[column] > 0)
        out["top5"] = mh_or(key, both.e, both[column] >= both.pub_year.map(thresholds))
    return out


def clogit(ret, ctl, thresholds):
    from statsmodels.discrete.conditional_models import ConditionalLogit
    r, c, _ = matched(ret, ctl, "cd_w0")
    b = pd.concat([r.assign(e=1), c.assign(e=0)], ignore_index=True)
    b["pos"], b["top5"] = b.cd_w0 > 0, b.cd_w0 >= b.pub_year.map(thresholds)
    b["lrefs"], b["lcites"] = np.log1p(b.n_refs), np.log1p(b.cites_w0)
    groups = b.groupby(ST).ngroup().to_numpy()
    out = {}
    for outcome in ("pos", "top5"):
        y = b[outcome].astype(float).to_numpy()
        keep = pd.Series(y).groupby(groups).transform(lambda s: s.nunique() > 1).to_numpy()
        if not keep.any():
            raise ValueError(f"No outcome-varying strata for {outcome}")
        for name, columns in (("unadjusted", ["e"]), ("refs", ["e", "lrefs"]),
                              ("refs_cites", ["e", "lrefs", "lcites"])):
            model = ConditionalLogit(y[keep], b[columns].astype(float).to_numpy()[keep],
                                     groups=groups[keep]).fit(disp=0)
            beta, se = float(model.params[0]), float(model.bse[0])
            out[f"{outcome}_{name}"] = {"or": float(np.exp(beta)),
                                       "ci": [float(np.exp(beta - 1.96 * se)), float(np.exp(beta + 1.96 * se))],
                                       "retracted_in_model": int(b.e.to_numpy()[keep].sum()),
                                       "strata": int(len(np.unique(groups[keep])))}
    return out
