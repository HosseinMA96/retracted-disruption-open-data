"""P18: composition of PMID-prioritized article-type filter failures (descriptive, five-year population)."""
import json
import sys
from pathlib import Path

import duckdb
import pandas as pd

from common import Run, E_ROOT, E_DATA, D_WORK, sha256
from types_lib import CATEGORY_TYPES, ORDER, categories, retained_types

EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "e16_topic"))
from topic_lib import metadata  # noqa: E402

E2, P13, P16 = "e02_pop_20261110_01", "e13_articles_20261126_01", "e16_topic_20261127_03"
EXPECTED = {"primary": {"total": 4587, "identifier_aware": 3626, "union_link": 3528},
            "controls": {"total": 52147, "identifier_aware": 43167, "union_link": 43152}}


def record(exp, run, name="results.json"):
    return json.loads((EXP / exp / "runs" / run / name).read_text())


def main():
    run_id, plan = sys.argv[1], sys.argv[2]
    run = Run(run_id, __file__, {
        "posthoc": "P18", "plan_commit": plan, "population": "five-year primary retracted papers and drawn controls",
        "inputs": [E2, P13, P16], "duckdb_threads": 1, "duckdb_memory_limit": "6GB", "category_order": ORDER,
        "spec_sha256": sha256(E_ROOT / "SPEC.md"), "posthoc_sha256": sha256(E_ROOT / "POSTHOC.md"),
        "helper_hashes": {str(p.relative_to(EXP)): sha256(p) for p in
                          [Path(__file__).with_name("types_lib.py"), Path(__file__).with_name("common.py"),
                           EXP / "e16_topic/topic_lib.py"]}})
    (run.dir / "run.json").write_text(json.dumps(run.info, indent=2))
    (run.dir / "manifest.json").write_text(json.dumps({
        "run_id": run_id, "plan_commit": plan, "inputs": [E2, P13, P16],
        "script_sha256": run.info["script_sha256"], "helper_hashes": run.info["config"]["helper_hashes"],
        "outputs": ["results.json", "run.json", "manifest.json", "stdout.log", "SHA256SUMS"],
        "release": "aggregate counts only; publication-level types remain on the VM"}, indent=2))
    label = E_DATA / "e02" / E2 / "labels.parquet"
    hashes = {"labels": sha256(label)}
    if hashes["labels"] != record("e02_population", E2, "run.json")["results"]["files"]["labels.parquet"]:
        raise ValueError("Frozen labels changed")
    p13 = record("e13_article_types", P13)
    for name in ("idmap.parquet", "pubmed26.parquet"):
        hashes[name] = sha256(D_WORK / name)
        if hashes[name] != p13["type_source_hashes"][name]:
            raise ValueError("P13 metadata input changed")
    run.log("frozen_label_and_metadata_hashes_verified", hashes)
    labels = pd.read_parquet(label)
    groups = {"primary": labels[labels.grp.eq("retracted") & labels.primary_set.eq(True)][["iid"]],
              "controls": labels[labels.grp.eq("control")][["iid"]]}
    focal = pd.concat(groups.values()).drop_duplicates()
    if len(focal) != sum(len(g) for g in groups.values()):
        raise ValueError("Overlapping or duplicated group membership")

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

    rows = []
    for iid, part in links.groupby("iid", sort=False):
        records = part.to_dict("records")
        meta = metadata(records)
        flags, group = categories(retained_types(records))
        if (group is None) != meta["article"]:
            raise ValueError("Category assignment disagrees with P16 article flag")
        rows.append(dict(iid=int(iid), article=meta["article"], legacy_article=meta["legacy_article"],
                         group=group, **flags))
    linked = {r["iid"] for r in rows}
    for iid in focal.iid[~focal.iid.isin(linked)]:
        flags, group = categories(set())
        rows.append(dict(iid=int(iid), article=False, legacy_article=False, group=group, **flags))
    per = pd.DataFrame(rows)
    if per.iid.duplicated().any() or len(per) != len(focal):
        raise ValueError("Per-node metadata does not cover the focal set exactly once")

    result = {"definition": run.info["config"], "input_hashes": hashes, "groups": {}}
    overlap = list(CATEGORY_TYPES) + ["no_journal_article", "unknown_types"]
    for name, members in groups.items():
        d = per[per.iid.isin(members.iid)]
        counts = {"total": len(d), "identifier_aware": int(d.article.sum()), "union_link": int(d.legacy_article.sum())}
        if counts != EXPECTED[name]:
            raise ValueError(f"P13/P16 eligibility not reproduced for {name}: {counts}")
        failing = d[~d.article]
        exclusive = failing["group"].value_counts().reindex(ORDER, fill_value=0)
        if failing["group"].isna().any() or int(exclusive.sum()) != len(failing):
            raise ValueError("A failing paper lacks exactly one category")
        if d.loc[d.article, overlap].any().any():
            raise ValueError("A passing paper carries an excluded or missing type")
        result["groups"][name] = {
            **counts, "failing": len(failing), "failing_share": len(failing) / len(d),
            "exclusive": {k: int(v) for k, v in exclusive.items()},
            "overlapping": {k: int(failing[k].sum()) for k in overlap},
            "failing_with_retracted_publication": int(failing.retracted_publication.sum()),
            "passing_with_retracted_publication": int(d.loc[d.article, "retracted_publication"].sum())}
    run.log("composition", result["groups"])
    (run.dir / "results.json").write_text(json.dumps(result, indent=2))
    run.finish()


if __name__ == "__main__":
    main()
