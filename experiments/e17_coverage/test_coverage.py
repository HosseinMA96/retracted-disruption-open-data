import math
import sys
import unittest
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from coverage_lib import attach, coverage_events, journal_mh, pooled_coverage, restricted_dinok

EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "e15_citers"))
from citer_lib import build_citers, journal_mean  # noqa: E402
sys.path.insert(0, str(EXP / "e13_article_types"))
from sensitivity_lib import mh_or  # noqa: E402
sys.path.insert(0, str(EXP / "e03_cd5"))
import cd_lib  # noqa: E402

CUTS = (3, 6)


class FixedDraws:
    def __init__(self, rows):
        self.rows = np.asarray(rows)

    def integers(self, low, high, size):
        assert size == self.rows.shape and self.rows.max() < high
        return self.rows


def random_graph(seed):
    rng = np.random.default_rng(seed)
    nodes = np.arange(1, 181)
    years = {int(i): int(rng.integers(1996, 2013)) for i in nodes if rng.random() > 0.05}
    edges = []
    for c in nodes:
        for r in rng.choice(nodes, size=int(rng.integers(0, 13)), replace=True):
            edges.append((int(c), int(r)))
    edges += [(7, 7), (11, 11), (12, 12)]
    focal = [int(i) for i in nodes if years.get(int(i), 0) in range(2000, 2005)][:30]
    return (pd.DataFrame(edges, columns=["citing_iid", "cited_iid"]),
            pd.DataFrame(sorted(years.items()), columns=["iid", "pub_year"]),
            pd.DataFrame({"iid": focal, "pub_year": [years[f] for f in focal]}))


def brute_force(edges, pubs, focal):
    e = {(c, r) for c, r in edges.itertuples(index=False) if c != r}
    year = dict(pubs.itertuples(index=False))
    rows = []
    for f, t in focal.itertuples(index=False):
        refs = {r for c, r in e if c == f}
        row = {"iid": f, "events": 0, "ni_all": 0, "nj_all": 0, "sum_log_refs": 0.0}
        for k in CUTS:
            row.update({f"ni_{k}": 0, f"nj_{k}": 0, f"below_{k}": 0})
        for c in sorted({c for c, r in e if r == f}):
            if c not in year or not t <= year[c] <= t + 5:
                continue
            degree = len({r for cc, r in e if cc == c})
            also = any((c, r) in e for r in refs)
            row["events"] += 1
            row["nj_all" if also else "ni_all"] += 1
            row["sum_log_refs"] += math.log1p(degree)
            for k in CUTS:
                if degree >= k:
                    row[f"nj_{k}" if also else f"ni_{k}"] += 1
                else:
                    row[f"below_{k}"] += 1
        rows.append(row)
    return pd.DataFrame(rows)


def sql_counts(edges, pubs, focal):
    con = duckdb.connect()
    for name, df in [("edges", edges), ("pubs", pubs), ("focal", focal.assign(end_year=focal.pub_year + 5))]:
        con.register(name, df)
    build_citers(con, "focal", "edges", "pubs")
    counts = coverage_events(con, "edges", CUTS)
    groups = pd.DataFrame({"iid": focal.iid, "grp": np.where(focal.index % 2, "control", "retracted")})
    pooled = pooled_coverage(con, groups, CUTS)
    con.close()
    return counts, pooled


class CoverageTests(unittest.TestCase):
    def test_restricted_counts_match_brute_force_and_frozen_counter(self):
        for seed in (1, 2, 3):
            edges, pubs, focal = random_graph(seed)
            counts, pooled = sql_counts(edges, pubs, focal)
            expected = brute_force(edges, pubs, focal)
            got = attach(focal[["iid"]], counts, CUTS)
            for column in expected.columns.drop("sum_log_refs"):
                self.assertTrue(np.array_equal(got[column].to_numpy(), expected[column].to_numpy()), (seed, column))
            self.assertTrue(np.allclose(got.sum_log_refs, expected.sum_log_refs, atol=1e-12, rtol=0))
            self.assertGreater(int((got.ni_all + got.nj_all > got[f"ni_{CUTS[1]}"] + got[f"nj_{CUTS[1]}"]).sum()), 0)
            con = duckdb.connect()
            con.register("edges", edges)
            con.register("pubs", pubs)
            con.register("focal", focal)
            cd_lib.HI = 5
            cd_lib.build_inputs(con, "focal", "edges", "pubs")
            frozen = cd_lib.score_batch(con, "focal").set_index("iid")
            con.close()
            self.assertTrue(np.array_equal(got.ni_all.to_numpy(), frozen.loc[got.iid, "ni_w0"].to_numpy()))
            self.assertTrue(np.array_equal(got.nj_all.to_numpy(), frozen.loc[got.iid, "nj_w0"].to_numpy()))
            self.assertEqual(sum(v["events"] for v in pooled.values()), int(got.events.sum()))

    def test_shares_and_restricted_scores(self):
        counts = pd.DataFrame({"iid": [1, 2], "events": [4, 2], "ni_all": [3, 0], "nj_all": [1, 2],
                               "sum_log_refs": [4.0, 2.0], "ni_3": [1, 0], "nj_3": [1, 0],
                               "below_3": [2, 2], "ni_6": [0, 0], "nj_6": [1, 0], "below_6": [3, 2]})
        d = attach(pd.DataFrame({"iid": [1, 2, 3]}), counts, CUTS)
        self.assertEqual(d.mean_log_refs.tolist()[:2], [1.0, 1.0])
        self.assertTrue(np.isnan(d.mean_log_refs.iloc[2]) and np.isnan(d.share_below_3.iloc[2]))
        self.assertEqual(d.share_below_3.tolist()[:2], [0.5, 1.0])
        self.assertEqual(restricted_dinok(d, 3).iloc[0], 0.0)
        self.assertTrue(restricted_dinok(d, 3).iloc[1:].isna().all())
        self.assertEqual(restricted_dinok(d, 6).iloc[0], -1.0)

    def test_journal_mantel_haenszel_resamples_whole_journals(self):
        rng = np.random.default_rng(4)
        rows = []
        for journal in range(1, 5):
            for year in (2000, 2001, 2002):
                for group, n in (("retracted", 3), ("control", 7)):
                    for _ in range(n):
                        rows.append((journal, year, group, bool(rng.random() < (0.45 if group == "retracted" else 0.3))))
        frame = pd.DataFrame(rows, columns=["journal_id", "pub_year", "grp", "y"])
        key = frame[["journal_id", "pub_year"]].astype(str).agg("|".join, axis=1)
        point = mh_or(key, frame.grp.eq("retracted"), frame.y)["or"]
        identity = journal_mh(frame, "y", FixedDraws([[0, 1, 2, 3]] * 3), nboot=3)
        self.assertAlmostEqual(identity["or"], point, places=12)
        self.assertTrue(np.allclose(identity["ci"], [point, point], atol=1e-12, rtol=0))
        repeated = journal_mh(frame, "y", FixedDraws([[0, 0, 1, 3]] * 2), nboot=2)
        copy = frame[frame.journal_id.eq(1)].assign(journal_id=99)
        manual = pd.concat([frame[frame.journal_id.isin([1, 2, 4])], copy])
        manual_key = manual[["journal_id", "pub_year"]].astype(str).agg("|".join, axis=1)
        expected = mh_or(manual_key, manual.grp.eq("retracted"), manual.y)["or"]
        self.assertTrue(np.allclose(repeated["ci"], [expected, expected], atol=1e-12, rtol=0))
        self.assertEqual((identity["strata"], identity["journals"]), (12, 4))

    def test_generic_matched_mean_uses_retracted_weights(self):
        frame = pd.DataFrame({"journal_id": [1, 1, 1, 2, 2, 2, 2], "pub_year": [2000] * 7,
                              "grp": ["retracted", "control", "control", "retracted", "retracted", "control", "control"],
                              "x": [1.0, 0.0, 1.0, 3.0, 5.0, 1.0, np.nan]})
        value = journal_mean(frame.assign(dinok=frame.x), np.random.default_rng(1), 20)
        self.assertAlmostEqual(value["diff"], (1 * (1 - 0.5) + 2 * (4 - 1)) / 3, places=12)
        self.assertEqual((value["retracted_compared"], value["controls_compared"]), (3, 3))


if __name__ == "__main__":
    unittest.main()
