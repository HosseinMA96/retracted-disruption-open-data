"""E7 (post hoc P6/P8, POSTHOC.md round 2): label-free yearly citation counts for the focal papers of E2 runs.
Reads only the focal lists (iid, pub_year), the graph tables, and the PubMed publication types and comments/corrections
links of CITING records (to flag editorial notices; applied to every focal paper alike). Checks that its window sums
equal the frozen counts of the given E3 runs, then freezes yearly.parquet (SHA-256 in run.json) before e08 joins labels.
Output (VM only): E_DATA/e07/RUN_ID/yearly.parquet (iid, y, ni, nj, ni_ntc, nj_ntc, nk_ntc).
usage: python e07_yearly.py RUN_ID E2_RUN[,E2_RUN...] E3_RUN[,E3_RUN...]
"""
import sys, json, duckdb
from pathlib import Path
from common import Run, C_WORK, D_WORK, E_DATA, E_ROOT, sha256
import yearly_lib

E2S, E3S = sys.argv[2].split(","), sys.argv[3].split(",")
EXP = Path(__file__).resolve().parents[1]
# PubMed publication-type UIs (names in the 2026 baseline: Retraction Notice, Published Erratum, Expression of Concern);
# matched by UI because NLM renamed D016440 ("Retraction of Publication" -> "Retraction Notice"; POSTHOC.md P8 amendment)
NOTICE_TYPES = ["D016440", "D016425", "D000075742"]
NOTICE_LINKS = ["RetractionOf", "ErratumFor", "ExpressionOfConcernFor"]
focal_files = [E_DATA / "e02" / r / "focal_iids.parquet" for r in E2S]
e3info = {r: json.loads((EXP / "e03_cd5" / "runs" / r / "run.json").read_text()) for r in E3S}
run = Run(sys.argv[1], __file__, {"e2_runs": E2S, "e3_check_runs": E3S, "y_end": yearly_lib.Y_END,
                                   "focal_sha256": {r: sha256(f) for r, f in zip(E2S, focal_files)},
                                   "yearly_lib_sha256": sha256(yearly_lib.__file__),
                                   "spec_sha256": sha256(E_ROOT / "SPEC.md"), "posthoc_sha256": sha256(E_ROOT / "POSTHOC.md"),
                                   "notice_pub_type_uis": NOTICE_TYPES, "notice_links": NOTICE_LINKS})
out = E_DATA / "e07" / sys.argv[1]; out.mkdir(parents=True, exist_ok=False)
con = duckdb.connect(str(out / "work.duckdb"))
con.execute(f"SET threads=8; SET memory_limit='48GB'; SET temp_directory='{E_DATA / 'tmp'}'; SET preserve_insertion_order=false")
q = lambda s: con.execute(s).fetchall(); one = lambda s: q(s)[0][0]
lst = lambda xs: "[" + ",".join("'" + x + "'" for x in xs) + "]"

files = ",".join(f"'{f}'" for f in focal_files)
con.execute(f"CREATE TABLE focal AS SELECT DISTINCT iid, pub_year FROM read_parquet([{files}])")
assert one("SELECT count(*) - count(DISTINCT iid) FROM focal") == 0, "an iid has two publication years"
run.log("focal", one("SELECT count(*) FROM focal"))

# --- editorial notices: attributes of citing records in PubMed, mapped to graph nodes by PMID or DOI (as in E2) ---
PM = f"read_parquet('{D_WORK / 'pubmed26.parquet'}')"
run.log("pubmed_pub_types_seen", q(f"""SELECT u, n, count(*) FROM (SELECT unnest(pub_type_ui) AS u, unnest(pub_type) AS n FROM {PM})
        WHERE n ILIKE '%retract%' OR n ILIKE '%errat%' OR n ILIKE '%concern%' GROUP BY ALL ORDER BY ALL"""))
run.log("pubmed_cc_reftypes_seen", q(f"SELECT r, count(*) FROM (SELECT unnest(cc_reftype) AS r FROM {PM}) GROUP BY 1 ORDER BY 1"))
con.execute(f"""CREATE TABLE pmn AS SELECT pmid, doi, list_has_any(pub_type_ui, {lst(NOTICE_TYPES)}) AS by_type,
                list_has_any(cc_reftype, {lst(NOTICE_LINKS)}) AS by_link FROM {PM}
                WHERE list_has_any(pub_type_ui, {lst(NOTICE_TYPES)}) OR list_has_any(cc_reftype, {lst(NOTICE_LINKS)})""")
run.log("pubmed_notice_records_by_type_link", q("SELECT by_type, by_link, count(*) FROM pmn GROUP BY ALL ORDER BY ALL"))
con.execute(f"CREATE TABLE idm AS SELECT iid, id_type, id FROM read_parquet('{D_WORK / 'idmap.parquet'}') WHERE iid IS NOT NULL")
con.execute("""CREATE TABLE ntc AS SELECT DISTINCT iid FROM (
     SELECT i.iid FROM idm i JOIN pmn p ON i.id_type = 'pmid' AND TRY_CAST(i.id AS BIGINT) = p.pmid
     UNION ALL SELECT i.iid FROM idm i JOIN pmn p ON i.id_type = 'doi' AND i.id = p.doi)""")
run.log("notice_nodes", one("SELECT count(*) FROM ntc"))
run.log("notice_nodes_that_are_focal", one("SELECT count(*) FROM ntc SEMI JOIN focal USING (iid)"))

# --- yearly counts --------------------------------------------------------------------------------------------
E = f"read_parquet('{C_WORK / 'edges.parquet'}')"; PUBS = f"read_parquet('{C_WORK / 'pubs_slim.parquet'}')"
yearly_lib.build(con, "focal", E, PUBS, "ntc")
for t in ("fr", "a", "ab", "ne", "knt"):
    run.log(f"rows_{t}", one(f"SELECT count(*) FROM {t}"))
df = yearly_lib.counts(con, "ntc")
assert not df.duplicated(["iid", "y"]).any()

# --- check: window sums == frozen E3 counts (both windows, every paper of every check run) ---------------------
con.register("yr", df)
for r in E3S:
    sf = E_DATA / "e03" / r / "scores.parquet"
    assert sha256(sf) == e3info[r]["results"]["frozen"]["scores.parquet"]["sha256"], f"{sf} changed after freezing"
    (lo0, hi0), (lo1, hi1) = e3info[r]["config"]["windows"]["w0"], e3info[r]["config"]["windows"]["w1"]
    res = q(f"""WITH s AS (SELECT iid, pub_year, ni_w0, nj_w0, ni_w1, nj_w1 FROM read_parquet('{sf}')),
       y AS (SELECT s.iid,
               coalesce(sum(yr.ni) FILTER (yr.y BETWEEN s.pub_year + {lo0} AND s.pub_year + {hi0}), 0) AS ni0,
               coalesce(sum(yr.nj) FILTER (yr.y BETWEEN s.pub_year + {lo0} AND s.pub_year + {hi0}), 0) AS nj0,
               coalesce(sum(yr.ni) FILTER (yr.y BETWEEN s.pub_year + {lo1} AND s.pub_year + {hi1}), 0) AS ni1,
               coalesce(sum(yr.nj) FILTER (yr.y BETWEEN s.pub_year + {lo1} AND s.pub_year + {hi1}), 0) AS nj1
             FROM s LEFT JOIN yr ON yr.iid = s.iid GROUP BY s.iid)
       SELECT count(*), count(*) FILTER (s.iid NOT IN (SELECT iid FROM focal)),
              count(*) FILTER (ni_w0 <> ni0 OR nj_w0 <> nj0 OR ni_w1 <> ni1 OR nj_w1 <> nj1)
       FROM s JOIN y USING (iid)""")[0]
    run.log(f"check_vs_{r}", {"papers": res[0], "not_in_focal": res[1], "mismatches": res[2], "windows": [[lo0, hi0], [lo1, hi1]]})
    assert res[1] == 0 and res[2] == 0, f"yearly counts disagree with the frozen counts of {r}"

df.to_parquet(out / "yearly.parquet", index=False)
con.close(); (out / "work.duckdb").unlink()
# label-free aggregate summaries only
run.log("yearly_rows", len(df))
run.log("citations_total", {c: int(df[c].sum()) for c in ("ni", "nj", "ni_ntc", "nj_ntc", "nk_ntc")})
run.log("focal_with_any_notice_citation", int(df[(df.ni_ntc + df.nj_ntc) > 0].iid.nunique()))
run.log("frozen", {"yearly.parquet": {"sha256": sha256(out / "yearly.parquet"), "rows": len(df)}})
run.finish()
