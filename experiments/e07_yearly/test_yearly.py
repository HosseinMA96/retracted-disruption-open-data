"""Unit test (run on the VM): yearly_lib == brute force, and yearly sums == cd_lib (the frozen-score code) on random toy
graphs with duplicates, self-loops, citation cycles, citing nodes without a year and notice records.
usage: python test_yearly.py"""
import random, sys
from pathlib import Path
import duckdb, pandas as pd
import yearly_lib
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "e03_cd5"))
import cd_lib  # noqa: E402


def one(seed, n=300, m=3500):
    rnd = random.Random(seed)
    year = {i: rnd.randint(1995, 2015) for i in range(n)}
    edges = []
    for _ in range(m):
        a, b = rnd.sample(range(n), 2)
        if year[a] >= year[b] - 1:            # mostly older targets; some one-year-newer targets make cycles possible
            edges.append((a, b))
    edges += edges[:60] + [(5, 5), (7, 7)]    # duplicates and self-loops must be ignored
    edges += [(i, i) for i in rnd.sample(range(n), 60)]
    for _ in range(300):                       # mutual citations (c cites f and f cites c) within a year of each other
        a, b = rnd.sample(range(n), 2)
        if abs(year[a] - year[b]) <= 1:
            edges += [(a, b), (b, a)]
    no_year = set(rnd.sample(range(n), 15))   # citing records without a publication year are not counted
    focal = sorted(rnd.sample(sorted(set(range(n)) - no_year), 60))
    notices = set(rnd.sample(range(n), 40))
    yr = {k: v for k, v in year.items() if k not in no_year}
    con = duckdb.connect()
    con.register("e_df", pd.DataFrame(edges, columns=["citing_iid", "cited_iid"]))
    con.register("p_df", pd.DataFrame(list(yr.items()), columns=["iid", "pub_year"]))
    con.execute("CREATE TABLE focal AS SELECT iid, pub_year FROM p_df WHERE iid IN (%s)" % ",".join(map(str, focal)))
    con.execute("CREATE TABLE ntc AS SELECT * FROM (VALUES %s) t(iid)" % ",".join(f"({i})" for i in sorted(notices)))
    yearly_lib.build(con, "focal", "e_df", "p_df", "ntc")
    got = yearly_lib.counts(con, "ntc")
    ref = yearly_lib.brute_force(edges, yr, focal, notices)
    g = {(int(r.iid), int(r.y)): [int(r.ni), int(r.nj), int(r.ni_ntc), int(r.nj_ntc), int(r.nk_ntc)] for r in got.itertuples()}
    if g != ref:
        bad = sorted(k for k in set(g) | set(ref) if g.get(k) != ref.get(k))[:5]
        raise AssertionError(f"seed {seed}: yearly_lib != brute force at {[(k, g.get(k), ref.get(k)) for k in bad]}")
    # window sums equal the frozen-score code (cd_lib, window [t, t+5] and [t+1, t+5])
    con2 = duckdb.connect()
    con2.register("e_df", pd.DataFrame(edges, columns=["citing_iid", "cited_iid"]))
    con2.register("p_df", pd.DataFrame(list(yr.items()), columns=["iid", "pub_year"]))
    con2.execute("CREATE TABLE focal AS SELECT iid, pub_year FROM p_df WHERE iid IN (%s)" % ",".join(map(str, focal)))
    cd_lib.build_inputs(con2, "focal", "e_df", "p_df")
    cd = cd_lib.score_batch(con2, "focal").set_index("iid")
    got = got.merge(pd.DataFrame({"iid": focal, "t": [yr[f] for f in focal]}), on="iid")
    for w, lo in (("w0", 0), ("w1", 1)):
        s = got[(got.y >= got.t + lo) & (got.y <= got.t + cd_lib.HI)].groupby("iid")[["ni", "nj"]].sum()
        s = s.reindex(focal, fill_value=0)
        assert (s.ni.values == cd[f"ni_{w}"].reindex(focal).values).all(), (seed, w, "ni")
        assert (s.nj.values == cd[f"nj_{w}"].reindex(focal).values).all(), (seed, w, "nj")
    n_ntc = int(got[["ni_ntc", "nj_ntc", "nk_ntc"]].to_numpy().sum())
    return len(focal), n_ntc


if __name__ == "__main__":
    res = [one(s) for s in range(20)]
    assert sum(r[1] for r in res) > 0, "the toy graphs never exercised a notice citation"
    print(f"focal papers checked: {sum(r[0] for r in res)} over 20 random graphs; notice citations exercised: "
          f"{sum(r[1] for r in res)}; yearly == brute force and window sums == cd_lib -> OK")
