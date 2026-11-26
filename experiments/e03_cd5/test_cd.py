"""Unit test: DuckDB CD (cd_lib) == brute force on random toy graphs, both windows. Run on the VM: python test_cd.py"""
import random, duckdb, pandas as pd, math
import cd_lib

def one(seed, n=300, m=3000):
    rnd = random.Random(seed)
    year = {i: rnd.randint(1995, 2015) for i in range(n)}
    edges = []
    for _ in range(m):
        a, b = rnd.sample(range(n), 2)
        if year[a] >= year[b]: edges.append((a, b))          # cite only older or same-year papers
    edges += edges[:50] + [(5, 5)]                            # duplicates and a self-loop must be ignored
    focal = sorted(rnd.sample(range(n), 60))
    con = duckdb.connect()
    con.register("e_df", pd.DataFrame(edges, columns=["citing_iid", "cited_iid"]))
    con.register("p_df", pd.DataFrame(list(year.items()), columns=["iid", "pub_year"]))
    con.execute("CREATE TABLE focal AS SELECT iid, pub_year FROM p_df WHERE iid IN (%s)" % ",".join(map(str, focal)))
    cd_lib.build_inputs(con, "focal", "e_df", "p_df")
    df = cd_lib.score_batch(con, "focal").set_index("iid")
    for w, lo in (("w0", 0), ("w1", 1)):
        ref = cd_lib.brute_force(edges, year, focal, lo)
        for f, (ni, nj, nk, cd) in ref.items():
            r = df.loc[f]
            assert (r[f"ni_{w}"], r[f"nj_{w}"], r[f"nk_{w}"]) == (ni, nj, nk), (seed, w, f, tuple(r), (ni, nj, nk))
            assert (cd is None and math.isnan(r[f"cd_{w}"])) or abs(r[f"cd_{w}"] - cd) < 1e-12
    # reference count excludes self-loops and duplicates
    nref = {f: len({d for c, d in set(edges) if c == f and d != f}) for f in focal}
    assert all(df.loc[f, "n_refs"] == nref[f] for f in focal)
    return len(focal)

if __name__ == "__main__":
    print("focal papers checked:", sum(one(s) for s in range(20)), "over 20 random graphs; all equal -> OK")
