"""CD index (SPEC.md §5) in DuckDB, plus a brute-force reference implementation for tests.

For focal f published in year t and window W=[t+lo, t+hi]:
  A = papers in W citing f;  B = papers in W, != f, citing >=1 reference of f
  n_i=|A\\B|, n_j=|A∩B|, n_k=|B\\A|, CD=(n_i-n_j)/(n_i+n_j+n_k), NULL if denominator 0.
Both windows [t, t+5] (suffix _w0) and [t+1, t+5] (suffix _w1) are computed in one pass.
"""
HI = 5

def build_inputs(con, focal, edges, pubs):
    """focal: table (iid, pub_year). edges: SQL source (citing_iid, cited_iid). pubs: SQL source (iid, pub_year).
    Creates fr (f, t, r) and inc (x, c, y): citations to every focal paper and to every reference of one,
    with the citing paper's year, restricted to years that can fall in some window."""
    con.execute(f"""CREATE OR REPLACE TABLE fr AS SELECT DISTINCT f.iid AS f, f.pub_year AS t, e.cited_iid AS r
                    FROM {focal} f JOIN {edges} e ON e.citing_iid = f.iid WHERE e.cited_iid <> f.iid""")
    con.execute(f"""CREATE OR REPLACE TABLE tgt AS SELECT iid AS x FROM {focal} UNION SELECT DISTINCT r FROM fr""")
    ymin, ymax = con.execute(f"SELECT min(pub_year), max(pub_year) + {HI} FROM {focal}").fetchone()
    con.execute(f"""CREATE OR REPLACE TABLE inc AS SELECT DISTINCT e.cited_iid AS x, e.citing_iid AS c, p.pub_year AS y
                    FROM {edges} e JOIN tgt ON e.cited_iid = tgt.x JOIN {pubs} p ON p.iid = e.citing_iid
                    WHERE p.pub_year BETWEEN {ymin} AND {ymax} AND e.citing_iid <> e.cited_iid""")  # self-citations of a node are not citations

def score_batch(con, focal_b):
    """focal_b: table (iid, pub_year) subset. Returns a DataFrame of counts and CD for both windows."""
    con.execute(f"""CREATE OR REPLACE TEMP TABLE a AS SELECT DISTINCT f.iid AS f, i.c, i.y, f.pub_year AS t
                    FROM {focal_b} f JOIN inc i ON i.x = f.iid
                    WHERE i.c <> f.iid AND i.y BETWEEN f.pub_year AND f.pub_year + {HI}""")
    con.execute(f"""CREATE OR REPLACE TEMP TABLE b AS SELECT DISTINCT fr.f, i.c, i.y, fr.t
                    FROM (SELECT * FROM fr WHERE f IN (SELECT iid FROM {focal_b})) fr JOIN inc i ON i.x = fr.r
                    WHERE i.c <> fr.f AND i.y BETWEEN fr.t AND fr.t + {HI}""")
    sql = f"""
    WITH u AS (
      SELECT coalesce(a.f, b.f) AS f, coalesce(a.y, b.y) AS y, coalesce(a.t, b.t) AS t,
             a.c IS NOT NULL AS in_a, b.c IS NOT NULL AS in_b
      FROM a FULL OUTER JOIN b ON a.f = b.f AND a.c = b.c),
    k AS (
      SELECT f,
        count(*) FILTER (in_a AND NOT in_b) AS ni_w0, count(*) FILTER (in_a AND in_b) AS nj_w0,
        count(*) FILTER (in_b AND NOT in_a) AS nk_w0,
        count(*) FILTER (in_a AND NOT in_b AND y >= t + 1) AS ni_w1, count(*) FILTER (in_a AND in_b AND y >= t + 1) AS nj_w1,
        count(*) FILTER (in_b AND NOT in_a AND y >= t + 1) AS nk_w1
      FROM u GROUP BY f)
    SELECT fb.iid, fb.pub_year,
      coalesce(nr.n_refs, 0) AS n_refs,
      coalesce(ni_w0,0) ni_w0, coalesce(nj_w0,0) nj_w0, coalesce(nk_w0,0) nk_w0,
      coalesce(ni_w1,0) ni_w1, coalesce(nj_w1,0) nj_w1, coalesce(nk_w1,0) nk_w1
    FROM {focal_b} fb LEFT JOIN k ON k.f = fb.iid
      LEFT JOIN (SELECT f, count(*) AS n_refs FROM fr WHERE f IN (SELECT iid FROM {focal_b}) GROUP BY f) nr ON nr.f = fb.iid
    ORDER BY fb.iid"""
    df = con.execute(sql).df()
    for w in ("w0", "w1"):
        den = df[f"ni_{w}"] + df[f"nj_{w}"] + df[f"nk_{w}"]
        df[f"cd_{w}"] = ((df[f"ni_{w}"] - df[f"nj_{w}"]) / den).where(den > 0)
        df[f"cites_{w}"] = df[f"ni_{w}"] + df[f"nj_{w}"]
        df[f"cd1_{w}"] = (df[f"nj_{w}"] == 0) & (df[f"nk_{w}"] == 0) & (df[f"ni_{w}"] > 0)
    return df

def brute_force(edges, year, focal, lo, hi=HI):
    """edges: list of (citing, cited); year: dict; focal: list of iids. Returns {f: (ni, nj, nk, cd)}."""
    refs, citers = {}, {}
    for c, d in set(edges):
        if c == d: continue
        refs.setdefault(c, set()).add(d); citers.setdefault(d, set()).add(c)
    out = {}
    for f in focal:
        t = year[f]; inw = lambda p: t + lo <= year[p] <= t + hi
        A = {c for c in citers.get(f, ()) if inw(c)}
        B = {c for r in refs.get(f, ()) for c in citers.get(r, ()) if c != f and inw(c)}
        ni, nj, nk = len(A - B), len(A & B), len(B - A)
        out[f] = (ni, nj, nk, (ni - nj) / (ni + nj + nk) if ni + nj + nk else None)
    return out
