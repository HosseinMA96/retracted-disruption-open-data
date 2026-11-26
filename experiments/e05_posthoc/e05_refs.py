"""E5 P1 (post hoc, POSTHOC.md): reference length and window citations by group and class.
usage: python e05_refs.py RUN_ID E2_RUN_ID E3_RUN_ID     Output: refs.json (group-level only)."""
import sys, json
import numpy as np, pandas as pd
from pathlib import Path
from common import Run, E_DATA, sha256
E2, E3 = sys.argv[2], sys.argv[3]
e3 = json.loads((Path(__file__).resolve().parents[1] / "e03_cd5" / "runs" / E3 / "run.json").read_text())
sf = E_DATA / "e03" / E3 / "scores.parquet"
run = Run(sys.argv[1], __file__, {"e2_run": E2, "e3_run": E3, "posthoc": "P1"})
assert sha256(sf) == e3["results"]["frozen"]["scores.parquet"]["sha256"]
D = pd.read_parquet(E_DATA / "e02" / E2 / "labels.parquet").merge(pd.read_parquet(sf).drop(columns="pub_year"), on="iid")
D["grp2"] = np.where(D.grp == "retracted", np.where(D.primary_set == True, "retracted_primary", "retracted_in_window"), D.grp)
desc = lambda s: {"n": int(len(s)), "median": float(s.median()), "q1": float(s.quantile(.25)), "q3": float(s.quantile(.75)), "mean": float(s.mean())}
out = {"n_refs": {g: desc(x.n_refs) for g, x in D.groupby("grp2")}, "cites_w0": {g: desc(x.cites_w0) for g, x in D.groupby("grp2")},
       "n_refs_by_class_primary": {c: desc(x.n_refs) for c, x in D[D.grp2 == "retracted_primary"].groupby("cls")}}
P, C = D[D.grp2 == "retracted_primary"], D[D.grp == "control"]
ST = ["journal_id", "pub_year"]
for col in ("n_refs", "cites_w0"):
    lr = np.log1p(P.groupby(ST)[col].mean()); lc = np.log1p(C.groupby(ST)[col].mean())
    m = pd.concat([lr.rename("r"), lc.rename("c"), P.groupby(ST).size().rename("w")], axis=1, join="inner")
    out[f"within_stratum_diff_log1p_{col}"] = float(np.average(m.r - m.c, weights=m.w))
ctx = D[(D.grp == "context") & D.cd_w0.notna()]
out["spearman_cd_vs_nrefs_context"] = float(ctx.cd_w0.rank().corr(ctx.n_refs.rank()))
out["spearman_cd_vs_cites_context"] = float(ctx.cd_w0.rank().corr(ctx.cites_w0.rank()))
(run.dir / "refs.json").write_text(json.dumps(out, indent=1))
for k in ("within_stratum_diff_log1p_n_refs", "within_stratum_diff_log1p_cites_w0", "spearman_cd_vs_nrefs_context"): run.log(k, out[k])
run.log("median_refs", {g: v["median"] for g, v in out["n_refs"].items()})
run.finish()
