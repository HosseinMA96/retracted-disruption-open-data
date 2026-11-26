"""E2: populations of SPEC.md §3–4 (retracted, matched controls, context sample). No disruption score is computed here.
Writes to E_DATA/e02/RUN_ID/ (VM only):
  focal_iids.parquet  (iid, pub_year)               label-free input for the score script
  labels.parquet      (iid, grp, journal_id, pub_year, primary_set, cls, review, first_notice)
The run folder gets counts and the SHA-256 of both files.
usage: python e02_population.py RUN_ID [LAST_YEAR WINDOW]   defaults 2017 5 (SPEC v1); other values = post hoc (POSTHOC.md)
"""
import sys, duckdb
from common import Run, C_WORK, D_WORK, E_DATA, E_ROOT, sha256

M, RWRUN, SEED, K, Y0 = "d05_match_20261101_02", "d02_rw_20261101_01", 20261109, 5, 2000
Y1 = int(sys.argv[2]) if len(sys.argv) > 2 else 2017
WIN = int(sys.argv[3]) if len(sys.argv) > 3 else 5
REVIEW = ["D016454", "D000078182", "D017418"]
MILL = ["Paper Mill"]
MISC = ["Falsification/Fabrication of Data", "Falsification/Fabrication of Image", "Falsification/Fabrication of Results",
        "Manipulation of Images", "Manipulation of Results", "Manipulation of Data", "Misconduct by Author",
        "Misconduct - Official Investigation(s) and/or Finding(s)", "Euphemisms for Misconduct", "Plagiarism of/in Article",
        "Plagiarism of Text", "Plagiarism of Image", "Plagiarism of Data", "Euphemisms for Plagiarism", "Duplication of/in Image",
        "Compromised Peer Review", "Rogue Editor", "False/Forged Authorship", "False/Forged Affiliation",
        "Computer-Aided Content or Computer-Generated Content", "Hoax Paper", "Sabotage of Materials/Methods"]
ERR = ["Results Not Reproducible", "Contamination of Cell Lines/Tissues", "Contamination of Materials", "Doing the Right Thing"]

run = Run(sys.argv[1], __file__, {"match_run": M, "rw_run": RWRUN, "seed": SEED, "K": K, "years": [Y0, Y1], "window_years": WIN,
                                   "spec_sha256": sha256(E_ROOT / "SPEC.md")})
out = E_DATA / "e02" / sys.argv[1]; out.mkdir(parents=True, exist_ok=False)
con = duckdb.connect(); con.execute(f"SET threads=8; SET memory_limit='48GB'; SET temp_directory='{E_DATA / 'tmp'}'")
q = lambda s: con.execute(s).fetchall(); one = lambda s: q(s)[0][0]
E = f"read_parquet('{C_WORK / 'edges.parquet'}')"
lst = lambda xs: "[" + ",".join("'" + x.replace("'", "''") + "'" for x in xs) + "]"

# --- biomedical nodes and DOI duplicates (D rule) ---------------------------------------------------------
con.execute(f"CREATE TABLE idm AS SELECT iid, id_type, id FROM read_parquet('{D_WORK / 'idmap.parquet'}') WHERE iid IS NOT NULL")
con.execute(f"CREATE TABLE pm AS SELECT pmid, doi, pub_type_ui FROM read_parquet('{D_WORK / 'pubmed26.parquet'}')")
con.execute("""CREATE TABLE pmlink AS
   SELECT i.iid, p.pub_type_ui FROM idm i JOIN pm p ON i.id_type='pmid' AND TRY_CAST(i.id AS BIGINT) = p.pmid
   UNION ALL SELECT i.iid, p.pub_type_ui FROM idm i JOIN pm p ON i.id_type='doi' AND i.id = p.doi""")
con.execute(f"""CREATE TABLE pmflag AS SELECT iid, bool_or(list_has_any(pub_type_ui, {lst(REVIEW)})) AS review,
                bool_or(list_contains(pub_type_ui, 'D016441')) AS pm_retracted FROM pmlink GROUP BY iid""")
con.execute("""CREATE TABLE bio AS SELECT DISTINCT iid FROM idm WHERE id_type = 'pmid'
   UNION SELECT DISTINCT i.iid FROM idm i JOIN (SELECT DISTINCT doi FROM pm WHERE doi IS NOT NULL) d ON i.id_type='doi' AND i.id = d.doi""")
con.execute("""CREATE TABLE dup AS SELECT DISTINCT iid FROM idm WHERE id_type='doi' AND id IN
               (SELECT id FROM idm WHERE id_type='doi' GROUP BY id HAVING count(DISTINCT iid) > 1)""")
con.execute(f"""CREATE TABLE node AS SELECT b.iid, p.pub_year, j.journal_id FROM bio b
   JOIN read_parquet('{C_WORK / 'pubs_slim.parquet'}') p USING (iid) LEFT JOIN read_parquet('{C_WORK / 'pubs_j.parquet'}') j USING (iid)
   WHERE p.pub_year BETWEEN {Y0} AND {Y1}""")
run.log("biomedical_nodes_2000_2017", one("SELECT count(*) FROM node"))
con.execute(f"""CREATE TABLE outd AS SELECT citing_iid AS iid, count(DISTINCT cited_iid) AS n_refs FROM {E}
   WHERE citing_iid IN (SELECT iid FROM node) AND cited_iid <> citing_iid GROUP BY 1""")
con.execute("""CREATE TABLE elig0 AS SELECT n.*, coalesce(o.n_refs, 0) AS n_refs FROM node n LEFT JOIN outd o USING (iid)
   WHERE n.journal_id IS NOT NULL AND n.iid NOT IN (SELECT iid FROM dup)""")
run.log("with_journal_not_dup", one("SELECT count(*) FROM elig0"))
run.log("with_journal_not_dup_zero_refs", one("SELECT count(*) FROM elig0 WHERE n_refs = 0"))
con.execute("CREATE TABLE elig AS SELECT * FROM elig0 WHERE n_refs > 0")
run.log("eligible", one("SELECT count(*) FROM elig"))

# --- retraction status and reason class ---------------------------------------------------------------------
con.execute(f"""CREATE TABLE st AS SELECT ri.iid, min(r.notice_date) AS first_notice, bool_or(r.reinstated) AS reinstated,
     flatten(list(p.reasons)) AS reasons
   FROM read_parquet('{D_WORK / f'rw_iid_{M}.parquet'}') ri JOIN read_parquet('{D_WORK / f'rw2_{M}.parquet'}') r USING (key)
   JOIN read_parquet('{D_WORK / f'rw_papers_{RWRUN}.parquet'}') p USING (key) GROUP BY 1""")
con.execute(f"""CREATE TABLE st2 AS SELECT *, CASE
     WHEN list_has_any(reasons, {lst(MILL)}) THEN 'paper_mill'
     WHEN list_has_any(reasons, {lst(MISC)}) THEN 'misconduct'
     WHEN len(list_filter(reasons, x -> x LIKE 'Error in%' OR x LIKE 'Error by%')) > 0 OR list_has_any(reasons, {lst(ERR)}) THEN 'honest_error'
     ELSE 'other' END AS cls FROM st""")
run.log("rw_matched_iids", one("SELECT count(*) FROM st2"))
run.log("rw_matched_iids_in_window_zero_refs", one("SELECT count(*) FROM elig0 WHERE n_refs = 0 AND iid IN (SELECT iid FROM st2)"))
con.execute(f"""CREATE TABLE ret AS SELECT e.iid, e.pub_year, e.journal_id, s.first_notice, s.cls,
     s.first_notice > make_date(e.pub_year + {WIN}, 12, 31) AS primary_set
   FROM elig e JOIN st2 s USING (iid) WHERE NOT coalesce(s.reinstated, false)""")
run.log("retracted_secondary_all", one("SELECT count(*) FROM ret"))
run.log("retracted_primary_after_window", one("SELECT count(*) FROM ret WHERE primary_set"))
run.log("retracted_by_class", q("SELECT cls, count(*), count(*) FILTER (primary_set) FROM ret GROUP BY 1 ORDER BY 1"))
run.log("retracted_by_year", q("SELECT pub_year, count(*), count(*) FILTER (primary_set) FROM ret GROUP BY 1 ORDER BY 1"))

# --- controls: same journal x year, never retracted (RW or PubMed), lowest hash(iid, SEED), K per retracted ------
con.execute(f"""CREATE TABLE pool AS SELECT e.iid, e.pub_year, e.journal_id, hash(e.iid, {SEED}) AS u FROM elig e
   WHERE e.iid NOT IN (SELECT iid FROM st2) AND e.iid NOT IN (SELECT iid FROM pmflag WHERE pm_retracted)""")
con.execute("CREATE TABLE need AS SELECT journal_id, pub_year, count(*) AS n_ret FROM ret GROUP BY 1, 2")
con.execute(f"""CREATE TABLE ctl AS SELECT iid, pub_year, journal_id FROM (
     SELECT p.*, row_number() OVER (PARTITION BY p.journal_id, p.pub_year ORDER BY p.u, p.iid) AS k, n.n_ret
     FROM pool p JOIN need n USING (journal_id, pub_year)) WHERE k <= {K} * n_ret""")
run.log("strata", one("SELECT count(*) FROM need"))
run.log("strata_without_controls", one("SELECT count(*) FROM need WHERE (journal_id, pub_year) NOT IN (SELECT journal_id, pub_year FROM ctl)"))
run.log("retracted_in_strata_without_controls", one("""SELECT count(*) FROM ret WHERE (journal_id, pub_year) NOT IN
                                                       (SELECT journal_id, pub_year FROM ctl)"""))
run.log("strata_with_fewer_than_K_per_retracted", one(f"""SELECT count(*) FROM need n LEFT JOIN
   (SELECT journal_id, pub_year, count(*) c FROM ctl GROUP BY 1, 2) c USING (journal_id, pub_year) WHERE coalesce(c.c, 0) < {K} * n.n_ret"""))
run.log("controls", one("SELECT count(*) FROM ctl"))

# --- context sample --------------------------------------------------------------------------------------------
con.execute(f"CREATE TABLE ctx AS SELECT iid, pub_year, journal_id FROM elig WHERE hash(iid, {SEED}) % 1000 < 2")
run.log("context_sample", one("SELECT count(*) FROM ctx"))
run.log("context_sample_retracted", one("SELECT count(*) FROM ctx WHERE iid IN (SELECT iid FROM st2)"))

# --- outputs ---------------------------------------------------------------------------------------------------
con.execute("""CREATE TABLE lab AS
     SELECT iid, 'retracted' AS grp, journal_id, pub_year, primary_set, cls, first_notice FROM ret
     UNION ALL SELECT iid, 'control', journal_id, pub_year, NULL, NULL, NULL FROM ctl
     UNION ALL SELECT iid, 'context', journal_id, pub_year, NULL, NULL, NULL FROM ctx""")
con.execute("CREATE TABLE lab2 AS SELECT l.*, coalesce(f.review, false) AS review FROM lab l LEFT JOIN pmflag f USING (iid)")
run.log("label_rows_by_group", q("SELECT grp, count(*), count(*) FILTER (review) FROM lab2 GROUP BY 1 ORDER BY 1"))
con.execute(f"COPY (SELECT * FROM lab2 ORDER BY grp, iid) TO '{out / 'labels.parquet'}' (FORMAT parquet)")
con.execute(f"COPY (SELECT DISTINCT iid, pub_year FROM lab2 ORDER BY iid) TO '{out / 'focal_iids.parquet'}' (FORMAT parquet)")
run.log("focal_iids", one(f"SELECT count(*) FROM read_parquet('{out / 'focal_iids.parquet'}')"))
run.log("files", {f: sha256(out / f) for f in ("labels.parquet", "focal_iids.parquet")})
run.finish()
