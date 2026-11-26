"""E10 (POSTHOC.md P10, descriptive): size of n_k relative to the citing papers, CD5 window. Group-level outputs only.
usage: python e10_nk.py RUN_ID E2_CD5 E3_CD5     Output: nk.json"""
import sys, json
import numpy as np, pandas as pd
from pathlib import Path
from common import Run, E_DATA, E_ROOT, sha256
E2, E3 = sys.argv[2], sys.argv[3]
EXP = Path(__file__).resolve().parents[1]
info = json.loads((EXP / "e03_cd5" / "runs" / E3 / "run.json").read_text())
sf = E_DATA / "e03" / E3 / "scores.parquet"
run = Run(sys.argv[1], __file__, {"e2_run": E2, "e3_run": E3, "posthoc": "P10", "posthoc_sha256": sha256(E_ROOT / "POSTHOC.md")})
assert info["config"]["e2_run"] == E2 and sha256(sf) == info["results"]["frozen"]["scores.parquet"]["sha256"]
S = pd.read_parquet(sf); L = pd.read_parquet(E_DATA / "e02" / E2 / "labels.parquet")
S = S[(S.ni_w0 + S.nj_w0 + S.nk_w0) > 0].copy()
S["cites"] = S.ni_w0 + S.nj_w0; S["share_k"] = S.nk_w0 / (S.cites + S.nk_w0)
Q = [0.05, 0.25, 0.5, 0.75, 0.95]
def desc(d):
    return {"n": int(len(d)), **{c: [float(v) for v in d[c].quantile(Q)] for c in ("nk_w0", "cites", "share_k")},
            "share_k_ge_0.9": float((d.share_k >= 0.9).mean()), "share_k_ge_0.99": float((d.share_k >= 0.99).mean())}
out = {"quantiles": Q, "all_scored": desc(S)}
prim = L.primary_set.astype(object).eq(True).to_numpy()   # NULL for non-retracted rows
L = L.assign(g=np.where(L.grp == "retracted", np.where(prim, "retracted_primary", "retracted_inside_window"), L.grp))
for g, d in L.groupby("g"):
    out[g] = desc(S[S.iid.isin(d.iid)])
(run.dir / "nk.json").write_text(json.dumps(out, indent=1))
run.log("all_scored_median_nk_cites_sharek", [out["all_scored"][c][2] for c in ("nk_w0", "cites", "share_k")])
run.finish()
