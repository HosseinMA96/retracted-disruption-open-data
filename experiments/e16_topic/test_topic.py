import unittest
import numpy as np
import pandas as pd
from topic_lib import metadata, select_controls, topic_pairs, paired_journal_mean


def record(pmid=1, native=True, types=("D016428",), mesh=("D1",), major=(True,), links=(), targets=()):
    return dict(pmid=pmid, is_pmid=native, pub_type_ui=list(types), mesh_ui=list(mesh),
                mesh_major=list(major), cc_reftype=list(links), cc_pmid=list(targets))


class TopicTests(unittest.TestCase):
    def test_unlinked_metadata_stays_unknown(self):
        x = metadata([])
        self.assertFalse(x["known_types"])
        self.assertFalse(x["legacy_article"])
        self.assertFalse(x["article"])
        self.assertEqual(x["major_mesh"], ())

    def test_foreign_notice_cannot_exclude_native_article(self):
        x = metadata([record(), record(2, False, ("D016440",), ("D2",),
                                       links=("RetractionOf",), targets=(1,))])
        self.assertFalse(x["legacy_article"])
        self.assertTrue(x["article"])
        self.assertTrue(x["notice_targets_native_pmid"])
        self.assertEqual(x["major_mesh"], ("D1",))

    def test_doi_fallback_and_native_notice(self):
        self.assertTrue(metadata([record(native=False), record(2, False, ("D016425",))])["article"])
        self.assertFalse(metadata([record(types=("D016428", "D016425")),
                                   record(2, False)])["article"])
        x = metadata([record(native=False, types=("D016440",))])
        self.assertFalse(x["known_types"])
        self.assertEqual(x["major_mesh"], ())

    def test_major_flags_and_invalid_alignment(self):
        self.assertEqual(metadata([record(mesh=("D1", "D2"), major=(True, False))])["major_mesh"], ("D1",))
        with self.assertRaises(ValueError):
            metadata([record(mesh=("D1", "D2"))])

    def test_nullable_correction_targets(self):
        r = record(2, False, ("D016440",), links=("RetractionOf",), targets=(None,))
        r["cc_pmid"] = np.ma.array([1], mask=[True])
        self.assertFalse(metadata([record(), r])["notice_targets_native_pmid"])

    def test_positive_overlap_and_order_independent_ties(self):
        rows = [dict(iid=i, major_mesh=("D1",), dinok=float(i)) for i in range(10)]
        rows.append(dict(iid=99, major_mesh=("D2",), dinok=999))
        a = select_controls(123, {"D1"}, rows)
        b = select_controls(123, {"D1"}, list(reversed(rows)))
        self.assertEqual([r["iid"] for _, r in a], [r["iid"] for _, r in b])
        self.assertEqual(len(a), 5)
        self.assertNotIn(99, [r["iid"] for _, r in a])

    def test_fixed_retained_baseline_and_strata(self):
        ret = pd.DataFrame([dict(iid=i, journal_id=1, pub_year=2000, dinok=0,
                                 major_mesh=mesh) for i, mesh in [(1, ("D1",)), (2, ("D3",))]])
        ctl = pd.DataFrame([dict(iid=i, journal_id=1, pub_year=year, dinok=value, major_mesh=mesh)
                            for i, year, value, mesh in [(3, 2000, 1, ("D1",)),
                                                        (4, 2000, -1, ("D2",)),
                                                        (5, 2001, 100, ("D1",))]])
        pairs, result = topic_pairs(ret, ctl)
        self.assertEqual(result["retracted_compared"], 1)
        self.assertEqual(result["unmatched_major_mesh_primary"], 1)
        self.assertEqual(pairs.baseline_gap.tolist(), [0])
        self.assertEqual(pairs.topic_gap.tolist(), [-1])

    def test_journal_resampling_keeps_years_together(self):
        pairs = pd.DataFrame(dict(journal_id=[1, 1, 2], baseline_gap=[1, 3, -1],
                                  topic_gap=[2, 4, -2]))
        x = paired_journal_mean(pairs, np.random.default_rng(3), nboot=1000)
        self.assertAlmostEqual(x["baseline"]["diff"], 1)
        self.assertAlmostEqual(x["topic"]["diff"], 4 / 3)
        self.assertEqual(x["baseline"]["ci"], [-1, 2])
        self.assertEqual(x["topic"]["ci"], [-2, 3])


if __name__ == "__main__":
    unittest.main()
