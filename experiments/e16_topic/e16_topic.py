"""P16: focal type-linkage audit, major-MeSH matches and fixed-window journal intervals."""
import json
import sys
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
from topic_lib import metadata, topic_pairs, paired_journal_mean

EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "e15_citers"))
from common import Run, E_ROOT, E_DATA, D_WORK, sha256
from citer_lib import journal_mean
sys.path.insert(0, str(EXP / "e13_article_types"))
from sensitivity_lib import compare
sys.path.insert(0, str(EXP / "e14_authors"))
from author_lib import author_exclusions

IDS = {"cd5": ("e02_pop_20261110_01", "e03_cd5_20261110_01", "e04_eval_20261110_01"),
       "cd3": ("e02_pop_cd3_20261110_01", "e03_cd5_cd3_20261110_01", "e04_eval_cd3_20261110_01")}


def read_result(exp, run):
    return json.loads((EXP / exp / "runs" / run / "results.json").read_text())


def check_point(value, old):
    n = old.get("retracted_compared", old.get("retracted_in_used_strata"))
    if not np.isclose(value["diff"], old["diff"], rtol=0, atol=1e-12) or value["retracted_compared"] != n:
        raise ValueError("Original mean/count not reproduced")


def main():
    run = Run(sys.argv[1], __file__, {
        "posthoc": "P16", "plan_commit": sys.argv[2], "seed": 20261109, "seed_offset": 4000, "n_boot": 2000,
        "duckdb_threads": 1, "duckdb_memory_limit": "6GB",
        "spec_sha256": sha256(E_ROOT / "SPEC.md"), "posthoc_sha256": sha256(E_ROOT / "POSTHOC.md"),
        "helper_hashes": {str(p.relative_to(EXP)): sha256(p) for p in
                          [Path(__file__).with_name("topic_lib.py"), EXP / "e15_citers/citer_lib.py",
                           EXP / "e15_citers/common.py", EXP / "e13_article_types/sensitivity_lib.py",
                           EXP / "e14_authors/author_lib.py"]}, "inputs": IDS})
    (run.dir / "run.json").write_text(json.dumps(run.info, indent=2))
    (run.dir / "manifest.json").write_text(json.dumps({
        "run_id": sys.argv[1], "plan_commit": sys.argv[2], "inputs": IDS,
        "script_sha256": run.info["script_sha256"],
        "source_and_helper_hashes": run.info["config"]["helper_hashes"],
        "outputs": ["results.json", "run.json", "manifest.json", "stdout.log", "SHA256SUMS"],
        "release": "aggregate records only; metadata and matches remain on the VM"}, indent=2))
    seeds = iter(np.random.SeedSequence(20261109).spawn(4100)[4000:])
    rng = lambda: np.random.default_rng(next(seeds))
    old_di = read_result("e08_posthoc2", "e08_posthoc2_20261123_02")
    old_types = read_result("e13_article_types", "e13_articles_20261126_01")
    old_authors = read_result("e14_authors", "e14_authors_20261126_01")
    p15 = read_result("e15_citers", "e15_citers_20261127_02")
    data, hashes = {}, {}
    for tag, (e2, e3, _) in IDS.items():
        sf, lf = E_DATA / "e03" / e3 / "scores.parquet", E_DATA / "e02" / e2 / "labels.parquet"
        i2 = json.loads((EXP / "e02_population/runs" / e2 / "run.json").read_text())
        i3 = json.loads((EXP / "e03_cd5/runs" / e3 / "run.json").read_text())
        hashes[tag] = {"scores": sha256(sf), "labels": sha256(lf)}
        if (hashes[tag]["scores"] != i3["results"]["frozen"]["scores.parquet"]["sha256"]
                or hashes[tag]["labels"] != i2["results"]["files"]["labels.parquet"]
                or i3["config"]["e2_run"] != e2):
            raise ValueError("Frozen population/score mismatch")
        d = pd.read_parquet(lf).merge(pd.read_parquet(sf).drop(columns="pub_year"),
                                     on="iid", how="left", validate="many_to_one")
        if d.ni_w0.isna().any() or not d.cites_w0.eq(d.ni_w0 + d.nj_w0).all():
            raise ValueError("Missing or inconsistent frozen scores")
        d["dinok"] = ((d.ni_w0 - d.nj_w0) / d.cites_w0).where(d.cites_w0 > 0)
        data[tag] = d
    for name in ("idmap.parquet", "pubmed26.parquet"):
        hashes[name] = sha256(D_WORK / name)
        if hashes[name] != old_types["type_source_hashes"][name]:
            raise ValueError("P13 metadata input changed")
    run.log("frozen_scores_labels_metadata_hashes_verified", True)
    focal = pd.concat([d[["iid"]] for d in data.values()]).drop_duplicates()
    con = duckdb.connect()
    con.execute("SET memory_limit='6GB'")
    con.execute("SET threads=1")
    con.register("focal", focal)
    con.execute(f"""CREATE TABLE ids AS SELECT iid,id_type,id
        FROM read_parquet('{D_WORK / 'idmap.parquet'}') SEMI JOIN focal USING(iid)""")
    run.log("bounded_identifiers", con.execute("SELECT count(*) FROM ids").fetchone()[0])
    con.execute(f"""CREATE TABLE linked_pmids AS
        SELECT DISTINCT p.pmid FROM read_parquet('{D_WORK / 'pubmed26.parquet'}') p
        JOIN ids i ON i.id_type='pmid' AND TRY_CAST(i.id AS BIGINT)=p.pmid
        UNION
        SELECT DISTINCT p.pmid FROM read_parquet('{D_WORK / 'pubmed26.parquet'}') p
        JOIN ids i ON i.id_type='doi' AND i.id=p.doi""")
    run.log("bounded_pubmed_keys", con.execute("SELECT count(*) FROM linked_pmids").fetchone()[0])
    con.execute(f"""CREATE TABLE pm AS
        SELECT p.pmid,p.doi,p.pub_type_ui,p.cc_reftype,p.cc_pmid,p.mesh_ui,p.mesh_major
        FROM read_parquet('{D_WORK / 'pubmed26.parquet'}') p SEMI JOIN linked_pmids USING(pmid)""")
    run.log("bounded_pubmed_records", con.execute("SELECT count(*) FROM pm").fetchone()[0])
    links = con.execute("""
        SELECT i.iid, true AS is_pmid,p.* EXCLUDE(doi) FROM ids i JOIN pm p
          ON i.id_type='pmid' AND TRY_CAST(i.id AS BIGINT)=p.pmid
        UNION ALL
        SELECT i.iid, false AS is_pmid,p.* EXCLUDE(doi) FROM ids i JOIN pm p
          ON i.id_type='doi' AND i.id=p.doi
    """).df()
    run.log("bounded_metadata_links", len(links))
    flags = pd.DataFrame([dict(iid=iid, **metadata(g.to_dict("records")))
                          for iid, g in links.groupby("iid", sort=False)])
    run.log("metadata_audit_completed", {"nodes": len(focal), "linked": len(flags),
                                       "pmid_sources": int(flags.pmid_source.sum())})
    missing = focal[~focal.iid.isin(flags.iid)]
    run.log("focal_nodes_without_pubmed_metadata", len(missing))
    if not missing.empty:
        unknown = pd.DataFrame([dict(iid=int(iid), **metadata([])) for iid in missing.iid])
        flags = pd.concat([flags, unknown], ignore_index=True)
    raw_file = D_WORK.parent / "raw/retraction-watch-data/retraction_watch.csv"
    mapping_file = D_WORK / "rw_iid_d05_match_20261101_02.parquet"
    hashes["rw_csv"], hashes["d5_mapping"] = sha256(raw_file), sha256(mapping_file)
    if any(hashes[k] != old_authors["input_hashes"][k] for k in ("rw_csv", "d5_mapping")):
        raise ValueError("P14 author input changed")
    raw = pd.read_csv(raw_file, dtype=str, keep_default_na=False,
                      usecols=["OriginalPaperDOI", "OriginalPaperPubMedID", "RetractionNature", "Author"])
    _, _, excluded, _ = author_exclusions(raw.to_dict("records"))
    mapping = pd.read_parquet(mapping_file, columns=["key", "iid"])
    excluded_ids = set(mapping.loc[mapping.key.isin(excluded), "iid"])
    result = {"definition": run.info["config"], "input_hashes": hashes, "windows": {}}
    for tag, d in data.items():
        d = d.merge(flags, on="iid", how="left", validate="many_to_one")
        if d.legacy_article.isna().any():
            raise ValueError("Focal metadata coverage is not accounted for")
        ret = d[d.grp.eq("retracted") & d.primary_set.eq(True)]
        ctl = d[d.grp.eq("control")]
        base = pd.concat([ret, ctl])
        mean = journal_mean(base, rng())
        check_point(mean, old_di["P5_dinok"][tag]["primary"])
        canonical = p15["windows"][tag]["scenarios"]["unfiltered"]["mean"]
        check_point(mean, canonical)
        output = {"unfiltered": {"primary": canonical, "by_class": {}}, "coverage": {}, "type_sensitive": {}}
        for cls, group in ret.groupby("cls"):
            value = journal_mean(pd.concat([group, ctl]), rng())
            check_point(value, old_di["P5_dinok"][tag]["by_class"][cls])
            output["unfiltered"]["by_class"][cls] = value
        for name, subset in (("primary", ret), ("controls", ctl)):
            output["coverage"][name] = {
                "total": len(subset), "legacy_articles": int(subset.legacy_article.sum()),
                "identifier_aware_articles": int(subset.article.sum()),
                "unknown_identifier_aware_types": int((~subset.known_types).sum()),
                "pmid_sources": int(subset.pmid_source.sum()),
                "doi_only_excluded_type": int(subset.doi_only_excluded_type.sum()),
                "foreign_notice": int(subset.foreign_notice.sum()),
                "notice_targets_native_pmid": int(subset.notice_targets_native_pmid.sum()),
                "newly_eligible": int((subset.article & ~subset.legacy_article).sum()),
                "newly_excluded": int((~subset.article & subset.legacy_article).sum())}
            if output["coverage"][name]["legacy_articles"] != old_types["windows"][tag]["coverage"][name]["eligible_articles"]:
                raise ValueError("P13 article eligibility not reproduced")
        legacy = journal_mean(base[base.legacy_article], rng())
        check_point(legacy, old_types["windows"][tag]["dinok"])
        output["type_sensitive"]["legacy_dinok"] = legacy
        typed = base[base.article]
        output["type_sensitive"]["identifier_aware_dinok"] = journal_mean(typed, rng())
        ctx = d[d.grp.eq("context") & d.cd_w0.notna()]
        thresholds = ctx.groupby("pub_year").cd_w0.quantile(.95).to_dict()
        legacy_cd = compare(ret[ret.legacy_article], ctl[ctl.legacy_article], "cd_w0", thresholds, rng())
        check_point(legacy_cd, old_types["windows"][tag]["primary"])
        for key in ("positive", "top5"):
            if not np.allclose([legacy_cd[key]["or"], *legacy_cd[key]["ci"]],
                               [old_types["windows"][tag]["primary"][key]["or"],
                                *old_types["windows"][tag]["primary"][key]["ci"]], atol=1e-12, rtol=0):
                raise ValueError("P13 CD odds ratio not reproduced")
        output["type_sensitive"]["identifier_aware_cd"] = compare(
            typed[typed.grp.eq("retracted")], typed[typed.grp.eq("control")], "cd_w0", thresholds, rng())
        retained = ret[~ret.iid.isin(excluded_ids)]
        output["authors"] = {"primary": journal_mean(pd.concat([retained, ctl]), rng()), "by_class": {}}
        check_point(output["authors"]["primary"], old_authors["windows"][tag]["dinok"])
        for cls, group in retained.groupby("cls"):
            value = journal_mean(pd.concat([group, ctl]), rng())
            check_point(value, old_authors["windows"][tag]["by_class"][cls]["dinok"])
            output["authors"]["by_class"][cls] = value
        if tag == "cd5":
            reviews = ctl[ctl.review.eq(True)].assign(grp="retracted")
            value = journal_mean(pd.concat([reviews, ctl[~ctl.review.eq(True)]]), rng())
            check_point(value, old_di["P4_reviews"]["dinok"])
            output["reviews"] = value
            output["topic_matching"] = {}
            for name, r, c in (("all_types", ret, ctl),
                               ("identifier_aware_articles", ret[ret.article], ctl[ctl.article])):
                pairs, coverage = topic_pairs(r, c)
                estimates = paired_journal_mean(pairs, rng())
                if not np.isclose(estimates["topic"]["diff"], pairs.topic_gap.mean(), atol=1e-12, rtol=0):
                    raise ValueError("Independent topic mean does not agree")
                output["topic_matching"][name] = {"coverage": coverage, "estimates": estimates}
        result["windows"][tag] = output
        run.log(f"{tag}_aggregate_results", output)
    (run.dir / "results.json").write_text(json.dumps(result, indent=2, default=float))
    run.finish()


if __name__ == "__main__":
    main()
