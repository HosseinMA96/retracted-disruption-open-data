"""P15 excluded-citer counts and journal-bootstrap matched/fixed-effect estimates."""
import numpy as np
import pandas as pd

ST = ["journal_id", "pub_year"]
FILTERS = {
    "notices": "notice",
    "notices_comments_letters": "(notice OR comment_letter)",
    "all": "(notice OR comment_letter OR retracted)",
}


def build_citers(con, focal, edges, pubs):
    con.execute(f"""CREATE TABLE fr AS SELECT DISTINCT f.iid AS f, e.cited_iid AS r
        FROM {focal} f JOIN {edges} e ON e.citing_iid=f.iid
        WHERE e.cited_iid<>f.iid""")
    con.execute(f"""CREATE TABLE incoming AS SELECT DISTINCT e.cited_iid AS f, e.citing_iid AS c
        FROM {edges} e SEMI JOIN {focal} f ON e.cited_iid=f.iid
        WHERE e.citing_iid<>e.cited_iid""")
    con.execute(f"""CREATE TABLE citer_years AS SELECT DISTINCT p.iid AS c,p.pub_year AS y
        FROM {pubs} p SEMI JOIN (SELECT DISTINCT c FROM incoming) a ON p.iid=a.c
        WHERE p.pub_year IS NOT NULL""")
    con.execute(f"""CREATE TABLE citing AS SELECT DISTINCT a.f,a.c,p.y
        FROM incoming a JOIN citer_years p USING (c) JOIN {focal} f ON a.f=f.iid
        WHERE p.y BETWEEN f.pub_year AND f.end_year""")


def removed_counts(con, edges, flags):
    con.execute(f"""CREATE TABLE excluded AS SELECT a.*, n.notice, n.comment_letter, n.retracted
        FROM citing a JOIN {flags} n ON a.c=n.iid
        WHERE n.notice OR n.comment_letter OR n.retracted""")
    con.execute(f"""CREATE TABLE excluded_edges AS SELECT DISTINCT e.citing_iid AS c, e.cited_iid AS r
        FROM {edges} e SEMI JOIN (SELECT DISTINCT c FROM excluded) a ON e.citing_iid=a.c
        WHERE e.citing_iid<>e.cited_iid""")
    con.execute("""CREATE TABLE also_ref AS SELECT DISTINCT a.f, a.c
        FROM excluded a JOIN excluded_edges e ON a.c=e.c JOIN fr ON fr.f=a.f AND fr.r=e.r""")
    columns = []
    for name, predicate in FILTERS.items():
        columns.extend([f"count(*) FILTER (b.c IS NULL AND {predicate}) AS ni_{name}",
                        f"count(*) FILTER (b.c IS NOT NULL AND {predicate}) AS nj_{name}"])
    return con.execute(f"""SELECT a.f AS iid, a.y, {', '.join(columns)}
        FROM excluded a LEFT JOIN also_ref b ON a.f=b.f AND a.c=b.c
        GROUP BY a.f,a.y ORDER BY a.f,a.y""").df()


def filter_scores(frame, removed, horizon, scenario):
    d = frame.copy()
    if scenario == "unfiltered":
        d["ni_removed"], d["nj_removed"] = 0, 0
    else:
        z = removed.merge(d[["iid", "pub_year"]], on="iid", validate="many_to_one")
        z = z[z.y.between(z.pub_year, z.pub_year + horizon)]
        z = z.groupby("iid")[[f"ni_{scenario}", f"nj_{scenario}"]].sum()
        d["ni_removed"] = d.iid.map(z[f"ni_{scenario}"]).fillna(0).astype("int64")
        d["nj_removed"] = d.iid.map(z[f"nj_{scenario}"]).fillna(0).astype("int64")
    if (d.ni_removed > d.ni_w0).any() or (d.nj_removed > d.nj_w0).any():
        raise ValueError("Excluded counts exceed original counts")
    d["ni"], d["nj"] = d.ni_w0 - d.ni_removed, d.nj_w0 - d.nj_removed
    if (d[["ni", "nj"]] < 0).any().any():
        raise ValueError("Excluded counts exceed original counts")
    d["cites_remaining"] = d.ni + d.nj
    d["dinok"] = ((d.ni - d.nj) / d.cites_remaining).where(d.cites_remaining > 0)
    return d


def matched_frame(frame):
    d = frame[frame.dinok.notna()].copy()
    counts = d.groupby(ST + ["grp"]).size().unstack(fill_value=0)
    if not {"retracted", "control"}.issubset(counts.columns):
        raise ValueError("No defined observations in both groups")
    counts = counts[(counts.retracted > 0) & (counts.control > 0)]
    if counts.empty:
        raise ValueError("No defined comparison strata")
    d = d[pd.MultiIndex.from_frame(d[ST]).isin(counts.index)].copy()
    d["exposed"] = d.grp.eq("retracted").astype(float)
    ratio = counts.retracted / counts.control
    d["weight"] = np.where(d.exposed.eq(1), 1.0,
                           ratio.reindex(pd.MultiIndex.from_frame(d[ST])).to_numpy())
    return d, counts


def journal_mean(frame, rng, nboot=2000):
    d, counts = matched_frame(frame)
    means = d.groupby(ST + ["grp"]).dinok.mean().unstack()
    terms = pd.DataFrame({"num": (means.retracted - means.control) * counts.retracted,
                          "den": counts.retracted})
    grouped = terms.groupby(level="journal_id").sum().sort_index()
    a, w = grouped.num.to_numpy(), grouped.den.to_numpy()
    ix = rng.integers(0, len(grouped), size=(nboot, len(grouped)))
    boot = a[ix].sum(1) / w[ix].sum(1)
    r = d[d.grp.eq("retracted")]
    c = d[d.grp.eq("control")]
    output = {"diff": float(a.sum() / w.sum()), "ci": np.quantile(boot, [0.025, 0.975]).tolist(),
              "mean_retracted": float(np.average(r.dinok, weights=r.weight)),
              "mean_controls": float(np.average(c.dinok, weights=c.weight)),
              "retracted_defined": int(frame.loc[frame.grp.eq("retracted"), "dinok"].notna().sum()),
              "controls_defined": int(frame.loc[frame.grp.eq("control"), "dinok"].notna().sum()),
              "retracted_compared": len(r), "controls_compared": len(c),
              "strata": len(counts), "journals": len(grouped), "bootstrap_unit": "journal"}
    return output


def within_model(frame, covariates, rng, nboot=2000):
    d, counts = matched_frame(frame)
    columns = ["exposed", *covariates]
    if not np.isfinite(d[columns + ["dinok", "weight"]].to_numpy(dtype=float)).all():
        raise ValueError("Non-finite model inputs")
    x = d[columns].to_numpy(dtype=float)
    y, w = d.dinok.to_numpy(), d.weight.to_numpy()
    groups = d.groupby(ST, sort=True).ngroup().to_numpy()
    total = np.bincount(groups, weights=w)
    mx = np.column_stack([np.bincount(groups, weights=w * x[:, j]) / total
                          for j in range(x.shape[1])])
    my = np.bincount(groups, weights=w * y) / total
    x, y = x - mx[groups], y - my[groups]
    journals = d.groupby("journal_id", sort=True).ngroup().to_numpy()
    p, jn = x.shape[1], int(journals.max()) + 1
    gram, rhs = np.zeros((jn, p, p)), np.zeros((jn, p))
    for a in range(p):
        rhs[:, a] = np.bincount(journals, weights=w * x[:, a] * y, minlength=jn)
        for b in range(p):
            gram[:, a, b] = np.bincount(journals, weights=w * x[:, a] * x[:, b], minlength=jn)
    ix = rng.integers(0, jn, size=(nboot, jn))
    bg, br = gram[ix].sum(1), rhs[ix].sum(1)
    if np.linalg.cond(gram.sum(0)) > 1e12 or np.any(np.linalg.cond(bg) > 1e12):
        raise ValueError("Rank-deficient or ill-conditioned within-stratum regression")
    beta = np.linalg.solve(gram.sum(0), rhs.sum(0))
    boot = np.linalg.solve(bg, br[..., None])[..., 0]
    return {"retracted_coefficient": float(beta[0]),
            "ci": np.quantile(boot[:, 0], [0.025, 0.975]).tolist(),
            "coefficients": dict(zip(columns, map(float, beta))),
            "retracted_compared": int(d.exposed.sum()), "controls_compared": int((1 - d.exposed).sum()),
            "strata": len(counts), "journals": jn, "bootstrap_unit": "journal",
            "weighting": "retracted=1; control=n_retracted/n_control within stratum"}
