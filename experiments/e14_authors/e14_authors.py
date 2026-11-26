"""P14: remove primary papers linked to author names with >=10 retractions; aggregates only."""
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from common import Run, E_DATA, D_WORK, E_ROOT, sha256
from author_lib import author_exclusions

EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "e13_article_types"))
from sensitivity_lib import compare, ST

IDS = {"cd5": ("e02_pop_20261110_01", "e03_cd5_20261110_01", "e04_eval_20261110_01"),
       "cd3": ("e02_pop_cd3_20261110_01", "e03_cd5_cd3_20261110_01", "e04_eval_cd3_20261110_01")}
CSV_SHA = "7a729a87837985954a34326202cb98c4bff4b2b142fda8695febb613cf45a7f4"
D2_SHA = "809945a3ead91850c313fee2515da1220231460d9561c427d0c0d4f33114b135"


def evaluate(ret, ctl, column, thresholds, rng):
    ri = pd.MultiIndex.from_frame(ret.loc[ret[column].notna(), ST])
    ci = pd.MultiIndex.from_frame(ctl.loc[ctl[column].notna(), ST])
    if ri.intersection(ci).empty:
        return {"status": "not estimable: no retained defined comparison strata",
                "retracted_scored": int(ret[column].notna().sum()), "retracted_compared": 0,
                "controls_compared": 0, "strata": 0}
    return compare(ret, ctl, column, thresholds, rng)


def main():
    run = Run(sys.argv[1], __file__, {
        "posthoc": "P14", "threshold": 10, "seed": 20261109, "n_boot": 2000, "seed_offset": 2000,
        "spec_sha256": sha256(E_ROOT / "SPEC.md"), "posthoc_sha256": sha256(E_ROOT / "POSTHOC.md"),
        "author_helper_sha256": sha256(Path(__file__).with_name("author_lib.py")),
        "common_helper_sha256": sha256(Path(__file__).with_name("common.py")),
        "estimator_helper_sha256": sha256(EXP / "e13_article_types/sensitivity_lib.py"), "inputs": IDS})
    (run.dir / "run.json").write_text(json.dumps(run.info, indent=2))
    csv = D_WORK.parent / "raw/retraction-watch-data/retraction_watch.csv"
    paper_file = D_WORK / "rw_papers_d02_rw_20261101_01.parquet"
    mapping_file = D_WORK / "rw_iid_d05_match_20261101_02.parquet"
    if sha256(csv) != CSV_SHA or sha256(paper_file) != D2_SHA:
        raise ValueError("Frozen Retraction Watch CSV or D2 paper table changed")
    raw = pd.read_csv(csv, dtype=str, keep_default_na=False,
                      usecols=["OriginalPaperDOI", "OriginalPaperPubMedID", "RetractionNature", "Author"])
    keys, known, excluded, summary = author_exclusions(raw.to_dict("records"))
    papers = pd.read_parquet(paper_file, columns=["key", "reinstated"])
    if keys != set(papers.key):
        raise ValueError("D2 paper keys not reproduced from raw CSV")
    if summary["non_reinstated_paper_keys"] != int((~papers.reinstated).sum()):
        raise ValueError("D2 reinstatement exclusions not reproduced")
    mapping_sha = sha256(mapping_file)
    mapping = pd.read_parquet(mapping_file, columns=["key", "iid"])
    if not mapping.key.isin(keys).all():
        raise ValueError("D5 mapping contains keys absent from the frozen D2 table")
    excluded_ids = set(mapping.loc[mapping.key.isin(excluded), "iid"])
    known_ids = set(mapping.loc[mapping.key.isin(known), "iid"])
    if sha256(mapping_file) != mapping_sha:
        raise ValueError("D5 mapping changed during the join")
    run.log("author_coverage_and_exclusion_rule", summary)
    old_di = json.loads((EXP / "e08_posthoc2/runs/e08_posthoc2_20261123_02/results.json").read_text())["P5_dinok"]
    seeds = iter(np.random.SeedSequence(20261109).spawn(2040)[2000:])
    result = {"author_summary": summary,
              "input_hashes": {"rw_csv": CSV_SHA, "d2_papers": D2_SHA, "d5_mapping": mapping_sha},
              "windows": {}}
    for window, (e2, e3, e4) in IDS.items():
        score_file = E_DATA / "e03" / e3 / "scores.parquet"
        label_file = E_DATA / "e02" / e2 / "labels.parquet"
        i2 = json.loads((EXP / "e02_population/runs" / e2 / "run.json").read_text())
        i3 = json.loads((EXP / "e03_cd5/runs" / e3 / "run.json").read_text())
        if i3["config"]["e2_run"] != e2:
            raise ValueError("Frozen scores refer to another population")
        if sha256(score_file) != i3["results"]["frozen"]["scores.parquet"]["sha256"]:
            raise ValueError("Frozen score hash changed")
        if sha256(label_file) != i2["results"]["files"]["labels.parquet"]:
            raise ValueError("Frozen label hash changed")
        result["input_hashes"][window] = {"scores": sha256(score_file), "labels": sha256(label_file)}
        d = pd.read_parquet(label_file).merge(pd.read_parquet(score_file).drop(columns="pub_year"),
                                            on="iid", how="left", validate="many_to_one")
        if d.ni_w0.isna().any():
            raise ValueError("A labelled paper lacks a score row")
        d["dinok"] = ((d.ni_w0 - d.nj_w0) / d.cites_w0).where(d.cites_w0 > 0)
        ret, ctl = d[(d.grp == "retracted") & d.primary_set.eq(True)], d[d.grp == "control"]
        ctx = d[(d.grp == "context") & d.cd_w0.notna()]
        thresholds = ctx.groupby("pub_year").cd_w0.quantile(0.95).to_dict()
        replay = compare(ret, ctl, "cd_w0", thresholds,
                         np.random.default_rng(np.random.SeedSequence(20261109).spawn(1)[0]))
        old = json.loads((EXP / "e04_eval/runs" / e4 / "results.json").read_text())["primary"]
        if replay["retracted_compared"] != old["retracted_in_used_strata"] or not np.allclose(
                [replay["diff"], *replay["diff_ci"]], [old["diff"], *old["diff_ci"]], rtol=0, atol=1e-12):
            raise ValueError("Original CD mean/interval/count not reproduced")
        for key, field in (("positive", "mh_cd_pos"), ("top5", "mh_top_p95")):
            if not np.allclose([replay[key]["or"], *replay[key]["ci"]],
                               [old[field]["or"], *old[field]["ci"]], rtol=0, atol=1e-12):
                raise ValueError("Original CD odds ratio not reproduced")
        di = compare(ret, ctl, "dinok", thresholds, np.random.default_rng(next(seeds)))
        original_di = old_di[window]["primary"]
        if di["retracted_compared"] != original_di["retracted_in_used_strata"] or not np.isclose(
                di["diff"], original_di["diff"], rtol=0, atol=1e-12):
            raise ValueError("Original DI_nok point/count not reproduced")
        run.log(f"{window}_baseline_reproduced", True)
        retained = ret[~ret.iid.isin(excluded_ids)]
        output = {"coverage": {"primary_total": len(ret), "with_author_names": int(ret.iid.isin(known_ids).sum()),
                               "missing_author_names_retained": int((~ret.iid.isin(known_ids)).sum()),
                               "removed": len(ret) - len(retained), "retained": len(retained)},
                  "cd": evaluate(retained, ctl, "cd_w0", thresholds, np.random.default_rng(next(seeds))),
                  "dinok": evaluate(retained, ctl, "dinok", thresholds, np.random.default_rng(next(seeds))),
                  "baseline_dinok": {k: original_di[k] for k in ("diff", "diff_ci", "retracted_in_used_strata")},
                  "by_class": {}}
        for name, group in ret.groupby("cls"):
            selected = group[~group.iid.isin(excluded_ids)]
            output["by_class"][name] = {
                "removed": len(group) - len(selected),
                "cd": evaluate(selected, ctl, "cd_w0", thresholds, np.random.default_rng(next(seeds))),
                "dinok": evaluate(selected, ctl, "dinok", thresholds, np.random.default_rng(next(seeds)))}
        result["windows"][window] = output
        run.log(f"{window}_author_name_exclusion", output)
    (run.dir / "results.json").write_text(json.dumps(result, indent=2))
    run.finish()


if __name__ == "__main__":
    main()
