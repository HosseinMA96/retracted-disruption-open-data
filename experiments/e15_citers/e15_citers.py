"""P15: excluded citing records, adjusted DI_nok means, journal bootstrap and journal exclusions."""
import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from common import Run, C_WORK, D_WORK, E_DATA, E_ROOT, sha256
from citer_lib import ST, build_citers, removed_counts, filter_scores, journal_mean, within_model

EXP = Path(__file__).resolve().parents[1]
IDS = {"cd5": ("e02_pop_20261110_01", "e03_cd5_20261110_01", 5),
       "cd3": ("e02_pop_cd3_20261110_01", "e03_cd5_cd3_20261110_01", 3)}
E7 = "e07_yearly_20261123_02"
PLAN_COMMIT = "9c4ba4ca9bca39542f86a014bda2db463c1534ac"
NOTICE_TYPES = ["D016440", "D016425", "D000075742"]
NOTICE_LINKS = ["RetractionOf", "ErratumFor", "ExpressionOfConcernFor"]


def main():
    run = Run(sys.argv[1], __file__, {
        "posthoc": "P15", "plan_commit": PLAN_COMMIT, "seed": 20261109, "seed_offset": 3000,
        "n_boot": 2000, "bootstrap_unit": "journal", "top_journals": 10,
        "posthoc_sha256": sha256(E_ROOT / "POSTHOC.md"), "spec_sha256": sha256(E_ROOT / "SPEC.md"),
        "helper_sha256": sha256(Path(__file__).with_name("citer_lib.py")),
        "common_sha256": sha256(Path(__file__).with_name("common.py"))})
    (run.dir / "run.json").write_text(json.dumps(run.info, indent=2))
    out = E_DATA / "e15" / sys.argv[1]
    out.mkdir(parents=True, exist_ok=False)
    con = duckdb.connect(str(out / "work.duckdb"))
    con.execute(f"SET threads=8; SET memory_limit='48GB'; SET temp_directory='{E_DATA / 'tmp'}'")
    con.execute("SET preserve_insertion_order=false")
    frames, hashes = {}, {}
    old = json.loads((EXP / "e08_posthoc2/runs/e08_posthoc2_20261123_02/results.json").read_text())
    e7file = E_DATA / "e07" / E7 / "yearly.parquet"
    info7 = json.loads((EXP / "e07_yearly/runs" / E7 / "run.json").read_text())
    hashes["yearly"] = sha256(e7file)
    if hashes["yearly"] != info7["results"]["frozen"]["yearly.parquet"]["sha256"]:
        raise ValueError("Frozen E7 yearly counts changed")
    yearly = pd.read_parquet(e7file)
    focal = []
    for window, (e2, e3, horizon) in IDS.items():
        label = E_DATA / "e02" / e2 / "labels.parquet"
        score = E_DATA / "e03" / e3 / "scores.parquet"
        i2 = json.loads((EXP / "e02_population/runs" / e2 / "run.json").read_text())
        i3 = json.loads((EXP / "e03_cd5/runs" / e3 / "run.json").read_text())
        hashes[window] = {"labels": sha256(label), "scores": sha256(score)}
        if hashes[window]["labels"] != i2["results"]["files"]["labels.parquet"]:
            raise ValueError("Frozen labels changed")
        if hashes[window]["scores"] != i3["results"]["frozen"]["scores.parquet"]["sha256"]:
            raise ValueError("Frozen scores changed")
        d = pd.read_parquet(label).merge(pd.read_parquet(score).drop(columns="pub_year"),
                                        on="iid", how="left", validate="many_to_one")
        if d.ni_w0.isna().any():
            raise ValueError("A labelled focal paper lacks frozen counts")
        d = d[(d.grp.eq("retracted") & d.primary_set.eq(True)) | d.grp.eq("control")].copy()
        if d.iid.duplicated().any():
            raise ValueError("Duplicate focal membership in comparison")
        z = yearly.merge(d[["iid", "pub_year"]], on="iid", validate="many_to_one")
        z = z[z.y.between(z.pub_year, z.pub_year + horizon)].groupby("iid")[["ni", "nj"]].sum()
        for field in ["ni", "nj"]:
            if not np.array_equal(d.iid.map(z[field]).fillna(0).to_numpy(), d[field + "_w0"].to_numpy()):
                raise ValueError("E7 window sums do not reproduce frozen scores")
        frames[window] = d
        focal.append(d[["iid", "pub_year"]].assign(end_year=d.pub_year + horizon))
    focal = pd.concat(focal).groupby(["iid", "pub_year"], as_index=False).end_year.max()
    if focal.iid.duplicated().any():
        raise ValueError("Conflicting focal publication years")
    con.register("focal", focal)
    edges = f"read_parquet('{C_WORK / 'edges.parquet'}')"
    pubs = f"read_parquet('{C_WORK / 'pubs_slim.parquet'}')"
    for name, path in [("graph_edges", C_WORK / "edges.parquet"),
                       ("graph_publications", C_WORK / "pubs_slim.parquet")]:
        hashes[name] = sha256(path)
    run.log("focal_papers", len(focal))
    (run.dir / "pre_count_input_hashes.json").write_text(json.dumps(hashes, indent=2))
    build_citers(con, "focal", edges, pubs)
    run.log("citing_events", int(con.execute("SELECT count(*) FROM citing").fetchone()[0]))

    pmfile, idfile = D_WORK / "pubmed26.parquet", D_WORK / "idmap.parquet"
    paperfile = D_WORK / "rw_papers_d02_rw_20261101_01.parquet"
    mapfile = D_WORK / "rw_iid_d05_match_20261101_02.parquet"
    for name, path in [("pubmed", pmfile), ("idmap", idfile), ("rw_papers", paperfile), ("rw_mapping", mapfile)]:
        hashes[name] = sha256(path)
    if hashes["rw_papers"] != "809945a3ead91850c313fee2515da1220231460d9561c427d0c0d4f33114b135":
        raise ValueError("Frozen Retraction Watch paper table changed")
    if hashes["rw_mapping"] != "de031e26c09031b96e482d6c70e0d040cd68d6e0c50f3fdf683c981e68243035":
        raise ValueError("Frozen Retraction Watch node mapping changed")
    lst = lambda xs: "[" + ",".join("'" + x + "'" for x in xs) + "]"
    con.execute(f"""CREATE TABLE pm AS SELECT pmid,doi,
        coalesce(list_has_any(pub_type_ui,{lst(NOTICE_TYPES)}),false)
        OR coalesce(list_has_any(cc_reftype,{lst(NOTICE_LINKS)}),false) AS notice,
        coalesce(list_has_any(pub_type_ui,['D016420','D016422']),false) AS comment_letter,
        coalesce(list_has_any(pub_type_ui,['D016441']),false) AS retracted,
        coalesce(len(pub_type_ui)>0,false) AS types_known FROM read_parquet('{pmfile}')""")
    con.execute(f"""CREATE TABLE idm AS SELECT i.iid,i.id_type,i.id
        FROM read_parquet('{idfile}') i SEMI JOIN (SELECT DISTINCT c FROM citing) a ON i.iid=a.c""")
    con.execute("""CREATE TABLE pm_matches AS
        SELECT i.iid,p.notice,p.comment_letter,p.retracted,p.types_known FROM idm i JOIN pm p
        ON i.id_type='pmid' AND TRY_CAST(i.id AS BIGINT)=p.pmid
        UNION ALL SELECT i.iid,p.notice,p.comment_letter,p.retracted,p.types_known FROM idm i JOIN pm p
        ON i.id_type='doi' AND i.id=p.doi""")
    con.execute(f"""CREATE TABLE rw AS SELECT DISTINCT m.iid
        FROM read_parquet('{mapfile}') m JOIN read_parquet('{paperfile}') p USING (key)
        WHERE NOT p.reinstated""")
    con.execute("""CREATE TABLE flags AS WITH p AS (
        SELECT iid,bool_or(notice) AS notice,bool_or(comment_letter) AS comment_letter,
        bool_or(retracted) AS retracted,bool_or(types_known) AS types_known FROM pm_matches GROUP BY iid)
        SELECT coalesce(p.iid,r.iid) AS iid,coalesce(p.notice,false) AS notice,
        coalesce(p.comment_letter,false) AS comment_letter,
        (coalesce(p.retracted,false) OR r.iid IS NOT NULL) AS retracted,
        p.iid IS NOT NULL AS pubmed_matched,coalesce(p.types_known,false) AS types_known
        FROM p FULL OUTER JOIN rw r USING (iid)""")
    coverage = con.execute("""SELECT count(*) AS citing_events,count(DISTINCT c) AS citing_nodes,
        count(*) FILTER (pubmed_matched) AS pubmed_matched_events,
        count(*) FILTER (types_known) AS known_type_events,
        count(*) FILTER (notice) AS notice_events,count(*) FILTER (comment_letter) AS comment_letter_events,
        count(*) FILTER (retracted) AS retracted_events,
        count(*) FILTER (notice OR comment_letter OR retracted) AS union_excluded_events
        FROM citing a LEFT JOIN flags n ON a.c=n.iid""").df().iloc[0].to_dict()
    run.log("flag_coverage_union_of_windows", coverage)
    removed = removed_counts(con, edges, "flags")
    removed.to_parquet(out / "removed_yearly.parquet", index=False)
    hashes["removed_yearly"] = sha256(out / "removed_yearly.parquet")
    con.register("removed", removed)
    seeds = iter(np.random.SeedSequence(20261109).spawn(3120)[3000:])
    rng = lambda: np.random.default_rng(next(seeds))
    result = {"definition": run.info["config"], "input_hashes": hashes,
              "flag_coverage_union_of_windows": coverage, "windows": {}}
    for window, d in frames.items():
        horizon = IDS[window][2]
        incoming = con.execute("SELECT f AS iid,y,count(*) AS n FROM citing GROUP BY f,y").df()
        z = incoming.merge(d[["iid", "pub_year"]], on="iid", validate="many_to_one")
        z = z[z.y.between(z.pub_year, z.pub_year + horizon)].groupby("iid").n.sum()
        if not np.array_equal(d.iid.map(z).fillna(0).to_numpy(), d.cites_w0.to_numpy()):
            raise ValueError("Independent incoming-citer counts do not reproduce frozen totals")
        actual = removed.merge(d[["iid", "pub_year"]], on="iid", validate="many_to_one")
        actual = actual[actual.y.between(actual.pub_year, actual.pub_year + horizon)]
        expected = yearly.merge(d[["iid", "pub_year"]], on="iid", validate="many_to_one")
        expected = expected[expected.y.between(expected.pub_year, expected.pub_year + horizon)]
        for new, previous in [("ni_notices", "ni_ntc"), ("nj_notices", "nj_ntc")]:
            a = actual.groupby("iid")[new].sum()
            b = expected.groupby("iid")[previous].sum()
            if not np.array_equal(d.iid.map(a).fillna(0).to_numpy(), d.iid.map(b).fillna(0).to_numpy()):
                raise ValueError("P8 notice removal counts not reproduced")
        ranking = d[d.grp.eq("retracted")].groupby("journal_id").size().reset_index(name="n_primary")
        ranking = ranking.sort_values(["n_primary", "journal_id"], ascending=[False, True]).head(10)
        output = {"top_journals": ranking.to_dict("records"), "scenarios": {}}
        for scenario in ["unfiltered", "notices", "notices_comments_letters", "all"]:
            filtered = filter_scores(d, removed, horizon, scenario)
            filtered["lrefs"] = np.log1p(filtered.n_refs)
            filtered["lcites"] = np.log1p(filtered.cites_remaining)
            filtered["lcites_original"] = np.log1p(filtered.cites_w0)
            estimate = journal_mean(filtered, rng())
            if scenario == "unfiltered":
                original = old["P5_dinok"][window]["primary"]
                if estimate["retracted_compared"] != original["retracted_in_used_strata"] or not np.isclose(
                        estimate["diff"], original["diff"], rtol=0, atol=1e-12):
                    raise ValueError("Original P5 DI_nok gap/count not reproduced")
            entry = {"mean": estimate, "removals": {}}
            for group, part in filtered.groupby("grp"):
                entry["removals"][group] = {
                    "papers": len(part), "papers_with_removed_citers": int((part.ni_removed + part.nj_removed > 0).sum()),
                    "removed_citers": int((part.ni_removed + part.nj_removed).sum()),
                    "lost_defined_scores": int(((part.cites_w0 > 0) & part.cites_remaining.eq(0)).sum())}
            if window == "cd5":
                entry["models"] = {name: within_model(filtered, covariates, rng())
                                   for name, covariates in [("unadjusted", []), ("references", ["lrefs"]),
                                                            ("references_citations", ["lrefs", "lcites"])]}
                if not np.isclose(entry["models"]["unadjusted"]["retracted_coefficient"],
                                  estimate["diff"], rtol=0, atol=1e-12):
                    raise ValueError("Weighted unadjusted regression does not reproduce matched mean")
                if scenario == "all":
                    entry["models"]["references_original_citations"] = within_model(
                        filtered, ["lrefs", "lcites_original"], rng())
            output["scenarios"][scenario] = entry
            if scenario == "all":
                output["by_class"] = {}
                for cls in sorted(filtered.loc[filtered.grp.eq("retracted"), "cls"].unique()):
                    selected = filtered[filtered.grp.eq("control") | filtered.cls.eq(cls)]
                    output["by_class"][cls] = journal_mean(selected, rng())
                selected = filtered[~filtered.journal_id.isin(ranking.journal_id)]
                output["without_top_journals"] = {"mean": journal_mean(selected, rng()),
                    "primary_removed": int((filtered.grp.eq("retracted") & filtered.journal_id.isin(ranking.journal_id)).sum())}
                if window == "cd5":
                    output["without_top_journals"]["models"] = {
                        name: within_model(selected, covariates, rng())
                        for name, covariates in [("unadjusted", []), ("references", ["lrefs"]),
                                                 ("references_citations", ["lrefs", "lcites"])]}
        result["windows"][window] = output
        run.log(window + "_results", output)
        run.log(window + "_baseline_and_notice_checks", "passed")
    (run.dir / "results.json").write_text(json.dumps(result, indent=2, default=str))
    (run.dir / "manifest.json").write_text(json.dumps({
        "plan_commit": PLAN_COMMIT, "input_hashes": hashes,
        "private_count_output": "E_DATA/e15/" + sys.argv[1] + "/removed_yearly.parquet",
        "released": ["results.json", "run.json", "manifest.json", "pre_count_input_hashes.json",
                     "stdout.log", "SHA256SUMS"]}, indent=2))
    con.close()
    (out / "work.duckdb").unlink()
    run.finish()


if __name__ == "__main__":
    main()
