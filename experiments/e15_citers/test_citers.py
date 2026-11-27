import unittest
import duckdb
import numpy as np
import pandas as pd
from citer_lib import build_citers, removed_counts, filter_scores, journal_mean, within_model, matched_frame


class CiterTests(unittest.TestCase):
    def test_overlapping_flags_and_reference_membership(self):
        con = duckdb.connect()
        edges = pd.DataFrame({"citing_iid": [1, 1, 3, 3, 4, 4, 5, 6, 7],
                              "cited_iid": [2, 1, 1, 2, 1, 4, 1, 1, 1]})
        pubs = pd.DataFrame({"iid": [1, 2, 3, 4, 5, 6], "pub_year": [2000, 1998, 2001, 2002, 2003, 2009]})
        focal = pd.DataFrame({"iid": [1], "pub_year": [2000], "end_year": [2005]})
        flags = pd.DataFrame({"iid": [3, 4, 5, 6, 7], "notice": [True, False, False, True, True],
                              "comment_letter": [True, True, False, False, False],
                              "retracted": [True, False, True, False, False]})
        for name, df in [("edges", edges), ("pubs", pubs), ("focal", focal), ("flags", flags)]:
            con.register(name, df)
        build_citers(con, "focal", "edges", "pubs")
        z = removed_counts(con, "edges", "flags")
        self.assertEqual(z[["ni_notices", "nj_notices"]].sum().tolist(), [0, 1])
        self.assertEqual(z[["ni_notices_comments_letters", "nj_notices_comments_letters"]].sum().tolist(), [1, 1])
        self.assertEqual(z[["ni_all", "nj_all"]].sum().tolist(), [2, 1])
        frame = pd.DataFrame({"iid": [1], "pub_year": [2000], "ni_w0": [2], "nj_w0": [1]})
        self.assertTrue(filter_scores(frame, z, 5, "all").dinok.isna().all())
        with self.assertRaisesRegex(ValueError, "exceed"):
            filter_scores(frame.assign(ni_w0=1), z, 5, "all")
        con.close()

    def test_weighted_fixed_effects_and_journal_resampling(self):
        rows = []
        for journal in [1, 2, 3]:
            for year in [2000, 2001]:
                for group, n in [("retracted", 2), ("control", journal + 2)]:
                    for i in range(n):
                        exposed = group == "retracted"
                        x = i + 0.7 * exposed + 0.2 * journal
                        z = (i % 2) + 0.3 * exposed + 0.1 * year
                        rows.append((journal, year, group, x, z, 0.13 * exposed + 0.04 * x - 0.03 * z + year / 10000))
        frame = pd.DataFrame(rows, columns=["journal_id", "pub_year", "grp", "x", "z", "dinok"])
        mean = journal_mean(frame, np.random.default_rng(7), 100)
        unadjusted = within_model(frame, [], np.random.default_rng(7), 100)
        self.assertAlmostEqual(mean["diff"], unadjusted["retracted_coefficient"], places=12)
        self.assertEqual(mean["journals"], 3)
        model = within_model(frame, ["x", "z"], np.random.default_rng(9), 100)
        self.assertAlmostEqual(model["retracted_coefficient"], 0.13, places=11)
        d, _ = matched_frame(frame)
        fixed = pd.get_dummies(d[["journal_id", "pub_year"]].astype(str).agg("|".join, axis=1), dtype=float)
        design = np.column_stack([d[["exposed", "x", "z"]], fixed])
        weights = np.sqrt(d.weight.to_numpy())
        direct = np.linalg.lstsq(design * weights[:, None], d.dinok.to_numpy() * weights, rcond=None)[0]
        self.assertTrue(np.allclose([model["coefficients"][k] for k in ["exposed", "x", "z"]], direct[:3], atol=1e-11))
        with self.assertRaisesRegex(ValueError, "Rank-deficient"):
            within_model(frame.assign(z=frame.x), ["x", "z"], np.random.default_rng(9), 100)


if __name__ == "__main__":
    unittest.main()
