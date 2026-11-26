"""P13: filter frozen CD5/CD3 comparisons using linked PubMed publication types; aggregate output only."""
import json
import sys
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
from common import Run, E_DATA, D_WORK, E_ROOT, sha256
from sensitivity_lib import EXCLUDED, compare, clogit

EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "e12_diagnostics"))
from diagnostics_lib import matched_logs, boot_weighted

IDS = {"cd5": ("e02_pop_20261110_01", "e03_cd5_20261110_01", "e04_eval_20261110_01"),
       "cd3": ("e02_pop_cd3_20261110_01", "e03_cd5_cd3_20261110_01", "e04_eval_cd3_20261110_01")}


def main():
    run = Run(sys.argv[1], __file__, {"posthoc": "P13", "seed": 20261109, "n_boot": 2000, "inputs": IDS,
                                    "excluded_types": EXCLUDED, "required_type": "D016428",
                                    "spec_sha256": sha256(E_ROOT / "SPEC.md"),
                                    "posthoc_sha256": sha256(E_ROOT / "POSTHOC.md"),
                                    "helper_sha256": sha256(Path(__file__).with_name("sensitivity_lib.py"))})
    (run.dir / "run.json").write_text(json.dumps(run.info, indent=2))
    data, scores, labels, th = {}, {}, {}, {}
    input_hashes = {}
    for tag, (e2, e3, e4) in IDS.items():
        i2 = json.loads((EXP / "e02_population/runs" / e2 / "run.json").read_text())
        i3 = json.loads((EXP / "e03_cd5/runs" / e3 / "run.json").read_text())
        sf, lf = E_DATA / "e03" / e3 / "scores.parquet", E_DATA / "e02" / e2 / "labels.parquet"
        if i3["config"]["e2_run"] != e2 or sha256(sf) != i3["results"]["frozen"]["scores.parquet"]["sha256"]:
            raise ValueError(f"{tag}: frozen scores changed or population mismatch")
        if sha256(lf) != i2["results"]["files"]["labels.parquet"]:
            raise ValueError(f"{tag}: labels changed")
        input_hashes[tag] = {"scores": sha256(sf), "labels": sha256(lf)}
        scores[tag], labels[tag] = pd.read_parquet(sf), pd.read_parquet(lf)
        d = labels[tag].merge(scores[tag].drop(columns="pub_year"), on="iid", validate="many_to_one")
        d["dinok"] = ((d.ni_w0 - d.nj_w0) / d.cites_w0).where(d.cites_w0 > 0)
        if d.ni_w0.isna().any():
            raise ValueError("Missing score row")
        ctx = d[(d.grp == "context") & d.cd_w0.notna()]
        th[tag] = ctx.groupby("pub_year").cd_w0.quantile(0.95).to_dict()
        ret, ctl = d[(d.grp == "retracted") & d.primary_set.eq(True)], d[d.grp == "control"]
        replay = compare(ret, ctl, "cd_w0", th[tag], np.random.default_rng(np.random.SeedSequence(20261109).spawn(1)[0]))
        original = json.loads((EXP / "e04_eval/runs" / e4 / "results.json").read_text())["primary"]
        if replay["retracted_compared"] != original["retracted_in_used_strata"] or not np.allclose(
                [replay["diff"], *replay["diff_ci"]], [original["diff"], *original["diff_ci"]], rtol=0, atol=1e-12):
            raise ValueError(f"{tag}: primary means/counts not reproduced")
        for key, old in (("positive", "mh_cd_pos"), ("top5", "mh_top_p95")):
            if not np.allclose([replay[key]["or"], *replay[key]["ci"]],
                               [original[old]["or"], *original[old]["ci"]], rtol=0, atol=1e-12):
                raise ValueError(f"{tag}: {key} not reproduced")
        data[tag] = d
        run.log(f"{tag}_original_reproduced", replay)
    baseline = data["cd5"]
    ret = baseline[(baseline.grp == "retracted") & baseline.primary_set.eq(True)]
    models = clogit(ret, baseline[baseline.grp == "control"], th["cd5"])
    old = json.loads((EXP / "e08_posthoc2/runs/e08_posthoc2_20261123_02/results.json").read_text())["P7_sign_shift"]["clogit"]
    for key, model in models.items():
        if not np.allclose([model["or"], *model["ci"]], [old[key]["or"], *old[key]["ci"]], rtol=0, atol=1e-6):
            raise ValueError(f"P7 {key} not reproduced")
    run.log("P7_original_reproduced", True)
    focal = pd.concat([d[["iid"]] for d in data.values()]).drop_duplicates()
    con = duckdb.connect()
    con.execute("SET memory_limit='24GB'")
    con.register("focal", focal)
    excluded = "[" + ",".join(f"'{x}'" for x in EXCLUDED) + "]"
    flags = con.execute(f"""
        WITH ids AS (SELECT iid, id_type, id FROM read_parquet('{D_WORK / 'idmap.parquet'}')
                     WHERE iid IN (SELECT iid FROM focal)),
        pm AS (SELECT pmid, doi, pub_type_ui FROM read_parquet('{D_WORK / 'pubmed26.parquet'}')),
        links AS (
          SELECT i.iid, p.pub_type_ui FROM ids i JOIN pm p
          ON i.id_type='pmid' AND TRY_CAST(i.id AS BIGINT)=p.pmid
          UNION ALL
          SELECT i.iid, p.pub_type_ui FROM ids i JOIN pm p ON i.id_type='doi' AND i.id=p.doi)
        SELECT iid, count(*) AS matches,
          bool_or(coalesce(len(pub_type_ui), 0)>0) AS known_types,
          bool_or(coalesce(list_contains(pub_type_ui, 'D016428'), false)) AS journal_article,
          bool_or(coalesce(list_has_any(pub_type_ui, ['D016454','D000078182','D017418']), false)) AS review_type,
          bool_or(coalesce(list_has_any(pub_type_ui, {excluded}), false)) AS excluded
        FROM links GROUP BY iid
    """).df()
    flags["article"] = flags.known_types & flags.journal_article & ~flags.excluded
    run.log("type_linkage", {"focal_papers": len(focal), "linked_papers": len(flags),
                             "eligible_article_papers": int(flags.article.sum())})
    seeds = iter(np.random.SeedSequence(20261109).spawn(1020)[1000:])
    results = {"input_hashes": input_hashes, "definition": run.info["config"], "windows": {},
               "type_source_hashes": {name: sha256(D_WORK / name)
                                     for name in ("idmap.parquet", "pubmed26.parquet")}}
    for tag, d in data.items():
        d = d.merge(flags, on="iid", how="left", validate="many_to_one")
        if not d.review.eq(d.review_type.eq(True)).all():
            raise ValueError(f"{tag}: original PubMed review flags not reproduced")
        selected = d[d.article.eq(True)]
        ret = selected[(selected.grp == "retracted") & selected.primary_set.eq(True)]
        ctl = selected[selected.grp == "control"]
        coverage = {}
        for group, subset in (("primary", d[(d.grp == "retracted") & d.primary_set.eq(True)]),
                              ("controls", d[d.grp == "control"])):
            coverage[group] = {"total": len(subset), "unknown_types": int((~subset.known_types.eq(True)).sum()),
                               "journal_article": int(subset.journal_article.eq(True).sum()),
                               "excluded_type": int(subset.excluded.eq(True).sum()),
                               "eligible_articles": int(subset.article.eq(True).sum())}
        result = {"coverage": coverage,
                  "primary": compare(ret, ctl, "cd_w0", th[tag], np.random.default_rng(next(seeds))),
                  "dinok": compare(ret, ctl, "dinok", th[tag], np.random.default_rng(next(seeds)))}
        result["by_class"] = {name: compare(g, ctl, "cd_w0", th[tag], np.random.default_rng(next(seeds)))
                              for name, g in ret.groupby("cls")}
        if tag == "cd5":
            result["clogit"] = clogit(ret, ctl, th[tag])
            logs = matched_logs(labels[tag][labels[tag].iid.isin(selected.iid)], scores[tag])
            for value in logs.values():
                value["ci"] = boot_weighted(value.pop("groups"), np.random.default_rng(next(seeds)))
            result["matched_logs"] = logs
        results["windows"][tag] = result
        run.log(f"{tag}_article_only", result)
    (run.dir / "results.json").write_text(json.dumps(results, indent=2, default=float))
    run.finish()


if __name__ == "__main__":
    main()
