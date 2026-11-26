import numpy as np
import pandas as pd

ST = ["journal_id", "pub_year"]


def boot_mean(frame, column, rng, nboot=2000):
    groups = frame.groupby(ST)[column].agg(["sum", "count"]).sort_index()
    if groups.empty:
        raise ValueError("No defined observations in the comparison strata")
    sums, counts = groups["sum"].to_numpy(), groups["count"].to_numpy()
    draws = rng.integers(0, len(groups), size=(nboot, len(groups)))
    estimates = sums[draws].sum(axis=1) / counts[draws].sum(axis=1)
    return {"n": int(counts.sum()), "strata": len(groups), "mean": float(sums.sum() / counts.sum()),
            "ci": np.quantile(estimates, [0.025, 0.975]).tolist()}


def event_pairs(labels, yearly):
    retracted = labels[labels.grp == "retracted"].drop_duplicates("iid").copy()
    retracted["R"] = pd.to_datetime(retracted.first_notice).dt.year
    balanced = retracted[(retracted.R >= retracted.pub_year + 3) & (retracted.R <= 2019)]
    controls = labels[labels.grp == "control"].drop_duplicates("iid")
    counts = yearly[["iid", "y", "ni", "nj", "ni_ntc", "nj_ntc"]].copy()
    if counts.duplicated(["iid", "y"]).any():
        raise ValueError("Duplicate paper-year count rows")
    counts["cites"] = counts.ni + counts.nj - counts.ni_ntc - counts.nj_ntc
    if (counts.cites < 0).any():
        raise ValueError("Notice counts exceed citation counts")
    counts["dinok"] = ((counts.ni - counts.ni_ntc - counts.nj + counts.nj_ntc) / counts.cites).where(counts.cites > 0)
    ctl = controls[["iid", *ST]].merge(counts, on="iid", validate="one_to_many")
    ctl = ctl[ctl.dinok.notna()].groupby([*ST, "y"]).dinok.mean().rename("dinok_ctl").reset_index()
    grid = balanced[["iid", *ST, "R"]].merge(pd.DataFrame({"tau": range(-3, 4)}), how="cross")
    grid["y"] = grid.R + grid.tau
    grid = grid.merge(counts[["iid", "y", "dinok"]], on=["iid", "y"], how="left", validate="one_to_one")
    grid = grid.rename(columns={"dinok": "dinok_ret"})
    grid = grid.merge(ctl, on=[*ST, "y"], how="left", validate="many_to_one")
    grid["paired_diff"] = grid.dinok_ret - grid.dinok_ctl
    return balanced, grid[grid.paired_diff.notna()].sort_values(["tau", *ST, "iid"])


def matched_logs(labels, scores):
    data = labels.merge(scores.drop(columns="pub_year"), on="iid", validate="many_to_one")
    r = data[(data.grp == "retracted") & data.primary_set.eq(True) & data.cd_w0.notna()].copy()
    c = data[(data.grp == "control") & data.cd_w0.notna()].copy()
    weights = r.groupby(ST).size().rename("weight")
    out = {}
    for column in ("n_refs", "cites_w0"):
        r["log_count"], c["log_count"] = np.log1p(r[column]), np.log1p(c[column])
        groups = pd.concat([r.groupby(ST).log_count.mean().rename("r"),
                            c.groupby(ST).log_count.mean().rename("c"), weights], axis=1, join="inner")
        groups["difference"] = groups.r - groups.c
        r_all = data[(data.grp == "retracted") & data.primary_set.eq(True)]
        c_all = data[data.grp == "control"]
        old = pd.concat([np.log1p(r_all.groupby(ST)[column].mean()).rename("r"),
                         np.log1p(c_all.groupby(ST)[column].mean()).rename("c"),
                         r_all.groupby(ST).size().rename("weight")], axis=1, join="inner")
        out[column] = {"groups": groups, "mean_retracted": float(np.average(groups.r, weights=groups.weight)),
                       "mean_controls": float(np.average(groups.c, weights=groups.weight)),
                       "difference": float(np.average(groups.difference, weights=groups.weight)),
                       "log_of_mean_difference": float(np.average(old.r - old.c, weights=old.weight)),
                       "retracted_compared": int(groups.weight.sum()),
                       "controls_compared": int(c.set_index(ST).index.isin(groups.index).sum())}
    return out


def boot_weighted(groups, rng, nboot=2000):
    g = groups.sort_index()
    d, w = g.difference.to_numpy(), g.weight.to_numpy()
    draws = rng.integers(0, len(g), size=(nboot, len(g)))
    values = (d[draws] * w[draws]).sum(axis=1) / w[draws].sum(axis=1)
    return np.quantile(values, [0.025, 0.975]).tolist()
