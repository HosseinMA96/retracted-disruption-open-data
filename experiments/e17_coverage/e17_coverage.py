"""P17: citer reference coverage, coverage-restricted DI_nok/sign and journal-clustered primary intervals."""
import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from common import Run, C_WORK, E_DATA, E_ROOT, sha256
from coverage_lib import CUTOFFS, ST, attach, coverage_events, journal_mh, pooled_coverage, restricted_dinok

EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "e15_citers"))
from citer_lib import build_citers, journal_mean, matched_frame  # noqa: E402
sys.path.insert(0, str(EXP / "e13_article_types"))
from sensitivity_lib import mh_or  # noqa: E402

E2, E3, E4, P15 = "e02_pop_20261110_01", "e03_cd5_20261110_01", "e04_eval_20261110_01", "e15_citers_20261127_02"
HORIZON = 5
PRIMARY_COUNTS = (4586, 31662, 2239)


def record(exp, run, name="results.json"):
    return json.loads((EXP / exp / "runs" / run / name).read_text())


def same(a, b, tol=1e-12):
    return bool(np.isclose(a, b, rtol=0, atol=tol))


def main():
    run_id, plan = sys.argv[1], sys.argv[2]
    run = Run(run_id, __file__, {
        "posthoc": "P17", "plan_commit": plan, "seed": 20261109, "seed_offset": 5000, "n_boot": 2000,
        "bootstrap_unit": "journal", "cutoffs": list(CUTOFFS), "window": [0, HORIZON], "inputs": [E2, E3, E4, P15],
        "spec_sha256": sha256(E_ROOT / "SPEC.md"), "posthoc_sha256": sha256(E_ROOT / "POSTHOC.md"),
        "helper_hashes": {str(p.relative_to(EXP)): sha256(p) for p in
                          [Path(__file__).with_name("coverage_lib.py"), Path(__file__).with_name("common.py"),
                           EXP / "e15_citers/citer_lib.py", EXP / "e13_article_types/sensitivity_lib.py"]}})
    (run.dir / "run.json").write_text(json.dumps(run.info, indent=2))
    (run.dir / "manifest.json").write_text(json.dumps({
        "run_id": run_id, "plan_commit": plan, "inputs": [E2, E3, E4, P15],
        "script_sha256": run.info["script_sha256"], "helper_hashes": run.info["config"]["helper_hashes"],
        "outputs": ["results.json", "run.json", "manifest.json", "stdout.log", "SHA256SUMS"],
        "private_output": f"E_DATA/e17/{run_id}/per_paper.parquet",
        "release": "aggregate records only; citer degrees and per-paper values remain on the VM"}, indent=2))
    seeds = iter(np.random.SeedSequence(20261109).spawn(5100)[5000:])
    rng = lambda: np.random.default_rng(next(seeds))

    label, score = E_DATA / "e02" / E2 / "labels.parquet", E_DATA / "e03" / E3 / "scores.parquet"
    i2, i3 = record("e02_population", E2, "run.json"), record("e03_cd5", E3, "run.json")
    hashes = {"labels": sha256(label), "scores": sha256(score)}
    if (hashes["labels"] != i2["results"]["files"]["labels.parquet"]
            or hashes["scores"] != i3["results"]["frozen"]["scores.parquet"]["sha256"] or i3["config"]["e2_run"] != E2):
        raise ValueError("Frozen labels or scores changed")
    old_hashes = record("e15_citers", P15, "pre_count_input_hashes.json")
    for name, path in (("graph_edges", C_WORK / "edges.parquet"), ("graph_publications", C_WORK / "pubs_slim.parquet")):
        hashes[name] = sha256(path)
        if hashes[name] != old_hashes[name]:
            raise ValueError("Citation graph input changed since P15")
    run.log("frozen_and_graph_hashes_verified", hashes)

    full = pd.read_parquet(label).merge(pd.read_parquet(score).drop(columns="pub_year"),
                                        on="iid", how="left", validate="many_to_one")
    if full.ni_w0.isna().any():
        raise ValueError("A labelled paper lacks frozen counts")
    context = full[full.grp.eq("context") & full.cd_w0.notna()]
    thresholds = {q: context.groupby("pub_year").cd_w0.quantile(v).to_dict() for q, v in (("p95", .95), ("p99", .99))}
    old_thresholds = pd.read_csv(EXP / "e04_eval/runs" / E4 / "thresholds.csv", index_col="pub_year")
    for q in ("p95", "p99"):
        new = pd.Series(thresholds[q]).sort_index()
        if not new.index.equals(old_thresholds.index) or not np.allclose(
                new.to_numpy(), old_thresholds[f"w0_{q}"].to_numpy(), rtol=0, atol=1e-15):
            raise ValueError("Reference-sample thresholds not reproduced")
    d = full[(full.grp.eq("retracted") & full.primary_set.eq(True)) | full.grp.eq("control")].copy()
    if d.iid.duplicated().any():
        raise ValueError("Duplicate focal membership")

    out = E_DATA / "e17" / run_id
    out.mkdir(parents=True, exist_ok=False)
    con = duckdb.connect(str(out / "work.duckdb"))
    con.execute(f"SET threads=8; SET memory_limit='48GB'; SET temp_directory='{E_DATA / 'tmp'}'")
    con.execute("SET preserve_insertion_order=false")
    focal_frame = d[["iid", "pub_year"]].assign(end_year=d.pub_year + HORIZON)
    con.register("focal_frame", focal_frame)
    con.execute("CREATE TABLE focal AS SELECT * FROM focal_frame")
    con.unregister("focal_frame")
    edges = f"read_parquet('{C_WORK / 'edges.parquet'}')"
    pubs = f"read_parquet('{C_WORK / 'pubs_slim.parquet'}')"
    build_citers(con, "focal", edges, pubs)
    run.log("window_citing_events", con.execute("SELECT count(*) FROM citing").fetchone()[0])
    counts = coverage_events(con, edges)
    d = attach(d, counts)
    if not (np.array_equal(d.events.to_numpy(), d.cites_w0.to_numpy())
            and np.array_equal(d.ni_all.to_numpy(), d.ni_w0.to_numpy())
            and np.array_equal(d.nj_all.to_numpy(), d.nj_w0.to_numpy())):
        raise ValueError("Independent citer counts do not reproduce frozen n_i/n_j")
    run.log("frozen_counts_reproduced", {"papers": len(d), "citing_events": int(d.events.sum()),
                                         "distinct_citers": con.execute("SELECT count(*) FROM citer_degree").fetchone()[0]})

    d["dinok"] = ((d.ni_w0 - d.nj_w0) / d.cites_w0.where(d.cites_w0 > 0)).where(d.cites_w0 > 0)
    base = journal_mean(d, rng())
    p15 = record("e15_citers", P15)["windows"]["cd5"]["scenarios"]["unfiltered"]["mean"]
    if (not same(base["diff"], p15["diff"]) or any(base[k] != p15[k] for k in
            ("retracted_defined", "controls_defined", "retracted_compared", "controls_compared", "strata", "journals"))):
        raise ValueError("P15 unfiltered DI_nok gap/counts not reproduced")
    e4 = record("e04_eval", E4)["primary"]
    mean_cd = journal_mean(d.assign(dinok=d.cd_w0), rng())
    if (not same(mean_cd["diff"], e4["diff"]) or mean_cd["retracted_compared"] != e4["retracted_in_used_strata"]
            or mean_cd["strata"] != e4["strata_used"]):
        raise ValueError("E4 primary mean gap not reproduced")
    scored = d[d.cd_w0.notna()]
    sizes = scored.groupby(ST + ["grp"]).size().unstack(fill_value=0)
    used = sizes[(sizes.retracted > 0) & (sizes.control > 0)].index
    compared = scored[pd.MultiIndex.from_frame(scored[ST]).isin(used)].copy()
    if (int(compared.grp.eq("retracted").sum()), int(compared.grp.eq("control").sum()), len(used)) != PRIMARY_COUNTS:
        raise ValueError("Primary compared population not reproduced")
    compared["positive"] = compared.cd_w0 > 0
    compared["top5"] = compared.cd_w0 >= compared.pub_year.map(thresholds["p95"])
    compared["top1"] = compared.cd_w0 >= compared.pub_year.map(thresholds["p99"])
    key = compared[ST].astype(str).agg("|".join, axis=1)
    exposed = compared.grp.eq("retracted")
    original = {}
    for name, old in (("positive", e4["mh_cd_pos"]), ("top5", e4["mh_top_p95"]), ("top1", e4["mh_top_p99"])):
        original[name] = mh_or(key, exposed, compared[name])
        if not np.allclose([original[name]["or"], *original[name]["ci"]], [old["or"], *old["ci"]], rtol=1e-12, atol=0):
            raise ValueError(f"E4 {name} odds ratio not reproduced")
    run.log("baseline_replays", "passed: frozen counts, P15 unfiltered DI_nok, E4 mean gap and three odds ratios")

    result = {"definition": run.info["config"], "input_hashes": hashes,
              "replayed": {"p15_unfiltered_dinok": base, "e4_mean_gap": mean_cd["diff"],
                           "e4_odds_ratios_rgb": original}}
    journal_primary = {"mean_gap": mean_cd}
    for name in ("positive", "top5", "top1"):
        value = journal_mh(compared, name, rng())
        if not same(value["or"], original[name]["or"], 1e-12 * max(1.0, original[name]["or"])):
            raise ValueError("Journal-summed Mantel--Haenszel point differs from the original")
        value["rgb_ci"] = original[name]["ci"]
        journal_primary[name] = value
    result["journal_clustered_primary"] = journal_primary
    run.log("journal_clustered_primary", journal_primary)

    coverage = {}
    for column in ["mean_log_refs"] + [f"share_below_{k}" for k in CUTOFFS]:
        coverage[column] = journal_mean(d.assign(dinok=d[column]), rng())
        if (coverage[column]["retracted_compared"], coverage[column]["controls_compared"]) != (
                base["retracted_compared"], base["controls_compared"]):
            raise ValueError("Coverage comparison population differs from the unfiltered DI_nok population")
    matched, _ = matched_frame(d)
    coverage["pooled_citing_events"] = pooled_coverage(con, matched[["iid", "grp"]].reset_index(drop=True))
    result["citer_coverage"] = coverage
    run.log("citer_coverage", coverage)

    restricted = {}
    for k in CUTOFFS:
        frame = d.assign(dinok=restricted_dinok(d, k))
        mean = journal_mean(frame, rng())
        mean["cociting_share_retracted"] = (1 - mean["mean_retracted"]) / 2
        mean["cociting_share_controls"] = (1 - mean["mean_controls"]) / 2
        kept = {}
        for group, part in d.groupby("grp"):
            kept[group] = {"papers": len(part), "citing_events": int(part.events.sum()),
                           "retained_events": int((part[f"ni_{k}"] + part[f"nj_{k}"]).sum()),
                           "lost_defined_scores": int(((part.events > 0) & (part[f"ni_{k}"] + part[f"nj_{k}"] == 0)).sum())}
        compared[f"positive_{k}"] = compared[f"ni_{k}"] > compared[f"nj_{k}"]
        rgb = mh_or(key, exposed, compared[f"positive_{k}"])
        sign = journal_mh(compared, f"positive_{k}", rng())
        if not same(sign["or"], rgb["or"], 1e-12 * max(1.0, rgb["or"])):
            raise ValueError("Restricted sign odds-ratio points disagree")
        sign["rgb_ci"] = rgb["ci"]
        restricted[str(k)] = {"dinok": mean, "events": kept, "positive_score": sign}
    result["coverage_restricted"] = restricted
    run.log("coverage_restricted", restricted)

    d[["iid", "grp", "events", "ni_all", "nj_all", "sum_log_refs"] + [f"{p}_{k}" for k in CUTOFFS
                                                                     for p in ("ni", "nj", "below")]].to_parquet(
        out / "per_paper.parquet", index=False)
    result["private_output_sha256"] = sha256(out / "per_paper.parquet")
    (run.dir / "results.json").write_text(json.dumps(result, indent=2, default=float))
    con.close()
    (out / "work.duckdb").unlink()
    run.finish()


if __name__ == "__main__":
    main()
