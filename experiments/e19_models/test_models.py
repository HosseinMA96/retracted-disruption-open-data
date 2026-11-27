import unittest

import numpy as np
import pandas as pd

from models_lib import article_flags, models, sample


def record(iid, pmid, native=True, types=("D016428",), links=(), targets=()):
    return dict(iid=iid, pmid=pmid, is_pmid=native, pub_type_ui=list(types), mesh_ui=[], mesh_major=[],
                cc_reftype=list(links), cc_pmid=list(targets))


class ModelTests(unittest.TestCase):
    def test_flags_follow_union_link_and_pmid_priority(self):
        links = pd.DataFrame([
            record(1, 11), record(1, 12, False, ("D016440",), ("RetractionOf",), (11,)),
            record(2, 21, types=("D016428", "D016454")),
            record(3, 31, False), record(3, 32, False, ("D016425",)),
        ])
        flags = article_flags(links, [1, 2, 3, 4]).set_index("iid")
        self.assertEqual(flags.loc[1].tolist(), [False, True])
        self.assertEqual(flags.loc[2].tolist(), [False, False])
        self.assertEqual(flags.loc[3].tolist(), [False, True])
        self.assertEqual(flags.loc[4].tolist(), [False, False])

    def test_models_use_only_flagged_primary_and_controls(self):
        rng = np.random.default_rng(5)
        rows = []
        for journal in range(1, 41):
            for year in (2001, 2002):
                for group, n in (("retracted", 3), ("control", 9)):
                    for _ in range(n):
                        exposed = group == "retracted"
                        refs = rng.poisson(30 + 8 * exposed)
                        cites = rng.poisson(12 + 4 * exposed)
                        logit = -1.2 + 0.7 * exposed - 0.02 * (refs - 30)
                        positive = rng.random() < 1 / (1 + np.exp(-logit))
                        score = (0.01 if positive else -0.01) + rng.normal(0, 0.001)
                        rows.append(dict(journal_id=journal, pub_year=year, grp=group,
                                         primary_set=True if exposed else None, n_refs=refs, cites_w0=cites,
                                         cd_w0=score, keep=bool(rng.random() < 0.85)))
        frame = pd.DataFrame(rows)
        frame.loc[0, "primary_set"] = False
        thresholds = {2001: 0.012, 2002: 0.012}
        ret, ctl = sample(frame, "keep")
        self.assertTrue(ret.primary_set.eq(True).all() and ret.keep.all() and ctl.keep.all())
        fit = models(frame, "keep", thresholds)
        self.assertEqual(set(fit), {f"{o}_{m}" for o in ("pos", "top5") for m in ("unadjusted", "refs", "refs_cites")})
        self.assertGreater(fit["pos_refs"]["or"], fit["pos_unadjusted"]["or"] * 0.9)
        self.assertTrue(1.2 < fit["pos_refs"]["or"] < 4.0, fit["pos_refs"])
        self.assertLessEqual(fit["pos_unadjusted"]["retracted_in_model"], len(ret))


if __name__ == "__main__":
    unittest.main()
