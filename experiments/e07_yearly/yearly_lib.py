"""Yearly citation counts per focal paper (POSTHOC.md P6, P8), in DuckDB, plus a brute-force reference for tests.

Same rules as e03_cd5/cd_lib.py: self-loops are not citations; a citing paper counts only if it has a publication year.
For focal f published in year t with reference set R(f) (R(f) excludes f), and each citing year y in [t, Y_END]:
  ni      = papers published in y that cite f and no paper in R(f)
  nj      = papers published in y that cite f and >= 1 paper in R(f)
  ni_ntc, nj_ntc = the same, counting only citing records flagged as editorial notices
  nk_ntc  = notice records published in y, other than f, that cite >= 1 paper in R(f) but not f
Summed over y in [t+lo, t+hi], ni and nj equal cd_lib's n_i and n_j for that window (checked by test_yearly.py and e07).
No label is read here: the notice flag is a property of the citing record, applied to every focal paper alike.
"""
Y_END = 2023


def build(con, focal, edges, pubs, notices):
    """focal: table (iid, pub_year); edges: SQL source (citing_iid, cited_iid); pubs: SQL source (iid, pub_year);
    notices: table (iid) of citing records flagged as notices (distinct). Creates tables fr, a, ab, ne, knt."""
    con.execute(f"""CREATE OR REPLACE TABLE fr AS SELECT DISTINCT f.iid AS f, e.cited_iid AS r
                    FROM {focal} f JOIN {edges} e ON e.citing_iid = f.iid WHERE e.cited_iid <> f.iid""")
    # A: citers of f by citing year (self-loops excluded: c <> f)
    con.execute(f"""CREATE OR REPLACE TABLE a AS SELECT DISTINCT f.iid AS f, e.citing_iid AS c, p.pub_year AS y
                    FROM {focal} f JOIN {edges} e ON e.cited_iid = f.iid JOIN {pubs} p ON p.iid = e.citing_iid
                    WHERE e.citing_iid <> f.iid AND p.pub_year BETWEEN f.pub_year AND {Y_END}""")
    # citers of f that also cite >= 1 reference of f (a self-loop c -> c is not a citation)
    con.execute(f"""CREATE OR REPLACE TABLE ab AS SELECT DISTINCT a.f, a.c
                    FROM a JOIN {edges} e ON e.citing_iid = a.c JOIN fr ON fr.f = a.f AND fr.r = e.cited_iid
                    WHERE e.citing_iid <> e.cited_iid""")
    # notices that cite >= 1 reference of f but not f (the notice part of n_k); edges of notices first (small)
    con.execute(f"""CREATE OR REPLACE TABLE ne AS SELECT DISTINCT e.citing_iid AS c, e.cited_iid AS r, p.pub_year AS y
                    FROM {edges} e JOIN {notices} n ON n.iid = e.citing_iid JOIN {pubs} p ON p.iid = e.citing_iid
                    WHERE e.citing_iid <> e.cited_iid AND p.pub_year IS NOT NULL""")
    con.execute(f"""CREATE OR REPLACE TABLE knt AS
                    SELECT DISTINCT fr.f, ne.c, ne.y
                    FROM fr JOIN ne ON ne.r = fr.r JOIN {focal} fo ON fo.iid = fr.f
                    WHERE ne.c <> fr.f AND ne.y BETWEEN fo.pub_year AND {Y_END}
                      AND NOT EXISTS (SELECT 1 FROM a WHERE a.f = fr.f AND a.c = ne.c)""")


def counts(con, notices):
    """Rows (iid, y, ni, nj, ni_ntc, nj_ntc, nk_ntc) for every (focal, year) with a nonzero count, sorted."""
    return con.execute(f"""
      WITH ac AS (
        SELECT a.f, a.y, ab.c IS NOT NULL AS also_ref, n.iid IS NOT NULL AS ntc
        FROM a LEFT JOIN ab ON ab.f = a.f AND ab.c = a.c LEFT JOIN {notices} n ON n.iid = a.c),
      ya AS (
        SELECT f, y, count(*) FILTER (NOT also_ref) AS ni, count(*) FILTER (also_ref) AS nj,
               count(*) FILTER (NOT also_ref AND ntc) AS ni_ntc, count(*) FILTER (also_ref AND ntc) AS nj_ntc
        FROM ac GROUP BY 1, 2),
      yk AS (SELECT f, y, count(*) AS nk_ntc FROM knt GROUP BY 1, 2)
      SELECT coalesce(ya.f, yk.f) AS iid, coalesce(ya.y, yk.y) AS y,
             coalesce(ni, 0) AS ni, coalesce(nj, 0) AS nj, coalesce(ni_ntc, 0) AS ni_ntc,
             coalesce(nj_ntc, 0) AS nj_ntc, coalesce(nk_ntc, 0) AS nk_ntc
      FROM ya FULL OUTER JOIN yk ON ya.f = yk.f AND ya.y = yk.y
      ORDER BY 1, 2""").df()


def brute_force(edges, year, focal, notices, y_end=Y_END):
    """edges: list of (citing, cited); year: dict (nodes without a year are absent); focal: iids; notices: set.
    Returns {(f, y): [ni, nj, ni_ntc, nj_ntc, nk_ntc]} for nonzero rows."""
    refs, citers = {}, {}
    for c, d in set(edges):
        if c == d:
            continue
        refs.setdefault(c, set()).add(d)
        citers.setdefault(d, set()).add(c)
    out = {}
    for f in focal:
        t = year[f]
        ok = lambda p: p in year and t <= year[p] <= y_end and p != f
        A = {c for c in citers.get(f, ()) if ok(c)}
        B = {c for r in refs.get(f, ()) for c in citers.get(r, ()) if ok(c)}
        for c in A:
            row = out.setdefault((f, year[c]), [0, 0, 0, 0, 0])
            k = 1 if c in B else 0
            row[k] += 1
            row[2 + k] += c in notices
        for c in B - A:
            if c in notices:
                out.setdefault((f, year[c]), [0, 0, 0, 0, 0])[4] += 1
    return out
