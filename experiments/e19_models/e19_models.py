"""P19: P13's conditional-logit models refitted on the PMID-priority article sample (five-year window)."""
import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from common import Run, E_ROOT, E_DATA, D_WORK, sha256
from models_lib import article_flags, models, sample

EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "e13_article_types"))
from sensitivity_lib import compare  # noqa: E402

E2, E3, P13, P16 = "e02_pop_20261110_01", "e03_cd5_20261110_01", "e13_articles_20261126_01", "e16_topic_20261127_03"
EXPECTED = {"union_link": (3528, 43152), "pmid_priority": (3626, 43167)}


def record(exp, run, name="results.json"):
    return json.loads((EXP / exp / "runs" / run / name).read_text())


def same(new, old, tol):
    return (np.allclose([new["or"], *new["ci"]], [old["or"], *old["ci"]], rtol=0, atol=tol)
            and all(new[k] == old[k] for k in ("retracted_in_model", "strata") if k in old))


def main():
    run_id, plan = sys.argv[1], sys.argv[2]
    run = Run(run_id, __file__, {
        "posthoc": "P19", "plan_commit": plan, "window": [0, 5], "inputs": [E2, E3, P13, P16],
        "duckdb_threads": 1, "duckdb_memory_limit": "6GB", "replay_tolerance_clogit": 1e-6,
        "spec_sha256": sha256(E_ROOT / "SPEC.md"), "posthoc_sha256": sha256(E_ROOT / "POSTHOC.md"),
        "helper_hashes": {str(p.relative_to(EXP)): sha256(p) for p in
                          [Path(__file__).with_name("models_lib.py"), Path(__file__).with_name("common.py"),
                           EXP / "e16_topic/topic_lib.py", EXP / "e13_article_types/sensitivity_lib.py"]}})
    (run.dir / "run.json").write_text(json.dumps(run.info, indent=2))
    (run.dir / "manifest.json").write_text(json.dumps({
        "run_id": run_id, "plan_commit": plan, "inputs": [E2, E3, P13, P16],
        "script_sha256": run.info["script_sha256"], "helper_hashes": run.info["config"]["helper_hashes"],
        "outputs": ["results.json", "run.json", "manifest.json", "stdout.log", "SHA256SUMS"],
        "release": "aggregate model estimates only; publication-level flags remain on the VM"}, indent=2))
    label, score = E_DATA / "e02" / E2 / "labels.parquet", E_DATA / "e03" / E3 / "scores.parquet"
    i2, i3 = record("e02_population", E2, "run.json"), record("e03_cd5", E3, "run.json")
    hashes = {"labels": sha256(label), "scores": sha256(score)}
    if (hashes["labels"] != i2["results"]["files"]["labels.parquet"] or i3["config"]["e2_run"] != E2
            or hashes["scores"] != i3["results"]["frozen"]["scores.parquet"]["sha256"]):
        raise ValueError("Frozen labels or scores changed")
    p13, p16 = record("e13_article_types", P13), record("e16_topic", P16)
    for name in ("idmap.parquet", "pubmed26.parquet"):
        hashes[name] = sha256(D_WORK / name)
        if hashes[name] != p13["type_source_hashes"][name]:
            raise ValueError("P13 metadata input changed")
    run.log("frozen_and_metadata_hashes_verified", hashes)

    d = pd.read_parquet(label).merge(pd.read_parquet(score).drop(columns="pub_year"),
                                     on="iid", how="left", validate="many_to_one")
    if d.ni_w0.isna().any():
        raise ValueError("A labelled paper lacks frozen counts")
    context = d[d.grp.eq("context") & d.cd_w0.notna()]
    thresholds = context.groupby("pub_year").cd_w0.quantile(0.95).to_dict()
    d = d[(d.grp.eq("retracted") & d.primary_set.eq(True)) | d.grp.eq("control")].copy()
    focal = d[["iid"]].drop_duplicates()

    con = duckdb.connect()
    con.execute("SET memory_limit='6GB'")
    con.execute("SET threads=1")
    con.register("focal", focal)
    pubmed = f"read_parquet('{D_WORK / 'pubmed26.parquet'}')"
    con.execute(f"""CREATE TABLE ids AS SELECT iid,id_type,id
        FROM read_parquet('{D_WORK / 'idmap.parquet'}') SEMI JOIN focal USING(iid)""")
    con.execute(f"""CREATE TABLE linked_pmids AS
        SELECT DISTINCT p.pmid FROM {pubmed} p JOIN ids i ON i.id_type='pmid' AND TRY_CAST(i.id AS BIGINT)=p.pmid
        UNION SELECT DISTINCT p.pmid FROM {pubmed} p JOIN ids i ON i.id_type='doi' AND i.id=p.doi""")
    con.execute(f"""CREATE TABLE pm AS SELECT p.pmid,p.doi,p.pub_type_ui,p.cc_reftype,p.cc_pmid,p.mesh_ui,p.mesh_major
        FROM {pubmed} p SEMI JOIN linked_pmids USING(pmid)""")
    links = con.execute("""
        SELECT i.iid, true AS is_pmid, p.* EXCLUDE(doi) FROM ids i JOIN pm p
          ON i.id_type='pmid' AND TRY_CAST(i.id AS BIGINT)=p.pmid
        UNION ALL
        SELECT i.iid, false AS is_pmid, p.* EXCLUDE(doi) FROM ids i JOIN pm p
          ON i.id_type='doi' AND i.id=p.doi""").df()
    con.close()
    run.log("bounded_metadata_links", len(links))
    d = d.merge(article_flags(links, focal.iid), on="iid", how="left", validate="many_to_one")
    for flag, expected in EXPECTED.items():
        ret, ctl = sample(d, flag)
        if (len(ret), len(ctl)) != expected:
            raise ValueError(f"{flag} eligibility not reproduced: {(len(ret), len(ctl))}")

    union = models(d, "union_link", thresholds)
    old = p13["windows"]["cd5"]["clogit"]
    for key, value in union.items():
        if not same(value, old[key], 1e-6):
            raise ValueError(f"P13 union-link model {key} not reproduced")
    ret, ctl = sample(d, "pmid_priority")
    mh = compare(ret, ctl, "cd_w0", thresholds, np.random.default_rng(np.random.SeedSequence(20261109).spawn(1)[0]))
    old16 = p16["windows"]["cd5"]["type_sensitive"]["identifier_aware_cd"]
    if (mh["retracted_compared"] != old16["retracted_compared"] or mh["controls_compared"] != old16["controls_compared"]
            or not np.isclose(mh["diff"], old16["diff"], rtol=0, atol=1e-12)
            or not all(same(mh[k], old16[k], 1e-12) for k in ("positive", "top5"))):
        raise ValueError("P16 PMID-priority comparison not reproduced")
    run.log("replays", "passed: eligibility counts, six P13 union-link models, P16 PMID-priority MH odds ratios")

    fitted = models(d, "pmid_priority", thresholds)
    result = {"definition": run.info["config"], "input_hashes": hashes,
              "samples": {flag: dict(zip(("retracted", "controls"), expected)) for flag, expected in EXPECTED.items()},
              "replayed_union_link_models": union, "pmid_priority_mh": {k: mh[k] for k in ("positive", "top5")},
              "pmid_priority_models": fitted}
    run.log("pmid_priority_models", fitted)
    (run.dir / "results.json").write_text(json.dumps(result, indent=2, default=float))
    run.finish()


if __name__ == "__main__":
    main()
