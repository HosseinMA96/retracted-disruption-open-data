"""P12: paired annual confidence intervals and matched mean-log diagnostics.
usage: python e12_diagnostics.py RUN_ID
Reads the fixed E2/E3/E7 inputs used by P9 and P11; never writes per-paper outputs.
"""
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from common import Run, E_DATA, E_ROOT, sha256
from diagnostics_lib import event_pairs, boot_mean, matched_logs, boot_weighted

EXP = Path(__file__).resolve().parents[1]
SEED, NBOOT = 20261109, 2000
info = lambda exp, rid: json.loads((EXP / exp / "runs" / rid / "run.json").read_text())


def frozen(exp, sub, rid, name):
    path = E_DATA / sub / rid / name
    expected = info(exp, rid)["results"]["frozen"][name]["sha256"]
    if sha256(path) != expected:
        raise ValueError(f"{path} changed after freezing")
    return path


def main():
    run = Run(sys.argv[1], __file__, {"posthoc": "P12", "seed": SEED, "n_boot": NBOOT,
                                    "posthoc_sha256": sha256(E_ROOT / "POSTHOC.md")})
    e2_5, e2_3 = "e02_pop_20261110_01", "e02_pop_cd3_20261110_01"
    e3_5, e3_3, e7 = "e03_cd5_20261110_01", "e03_cd5_cd3_20261110_01", "e07_yearly_20261123_02"
    scores = pd.read_parquet(frozen("e03_cd5", "e03", e3_5, "scores.parquet"))
    frozen("e03_cd5", "e03", e3_3, "scores.parquet")
    yearly = pd.read_parquet(frozen("e07_yearly", "e07", e7, "yearly.parquet"))
    labels5 = pd.read_parquet(E_DATA / "e02" / e2_5 / "labels.parquet")
    labels3 = pd.read_parquet(E_DATA / "e02" / e2_3 / "labels.parquet")
    seeds = iter(np.random.SeedSequence(SEED).spawn(9))
    balanced, pairs = event_pairs(labels3, yearly)
    ref = pd.read_csv(EXP / "e09_pretrend/runs/e09_pretrend_20261123_01/event_time_balanced.csv").set_index("tau")
    if len(balanced) != 3083:
        raise ValueError("P9 balanced population was not reproduced")
    rows = []
    for tau, group in pairs.groupby("tau", sort=True):
        result = boot_mean(group, "paired_diff", np.random.default_rng(next(seeds)), NBOOT)
        if result["n"] != int(ref.loc[tau, "n_pairs"]) or not np.isclose(result["mean"], ref.loc[tau, "paired_diff"], rtol=0, atol=1e-12):
            raise ValueError(f"P9 paired point/count not reproduced at {tau}")
        rows.append({"tau": int(tau), "n_pairs": result["n"], "strata": result["strata"],
                     "paired_diff": result["mean"], "ci_lo": result["ci"][0], "ci_hi": result["ci"][1]})
    event = pd.DataFrame(rows)
    event.to_csv(run.dir / "paired_event.csv", index=False)
    logs = matched_logs(labels5, scores)
    p1 = json.loads((EXP / "e05_posthoc/runs/e05_refs_20261110_01/refs.json").read_text())
    for column, result in logs.items():
        if result["retracted_compared"] != 4586 or result["controls_compared"] != 31662:
            raise ValueError("P11 compared population was not reproduced")
        expected = p1[f"within_stratum_diff_log1p_{column}"]
        if not np.isclose(result["log_of_mean_difference"], expected, rtol=0, atol=1e-12):
            raise ValueError(f"P1 point not reproduced for {column}")
        result["ci"] = boot_weighted(result.pop("groups"), np.random.default_rng(next(seeds)), NBOOT)
    result = {"paired_event": rows, "matched_mean_logs": logs,
              "author_identifier_columns_in_labels": [c for c in labels5 if "author" in c.lower()],
              "frozen_hashes_verified": True, "P9_P11_P1_reproduced": True}
    (run.dir / "results.json").write_text(json.dumps(result, indent=2))
    run.log("paired_points_and_counts_reproduced", True)
    run.log("matched_mean_logs", logs)
    run.log("author_identifier_columns_in_labels", result["author_identifier_columns_in_labels"])
    run.finish()


if __name__ == "__main__":
    main()
