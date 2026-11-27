import sys
import unittest
from pathlib import Path

from types_lib import ORDER, categories, retained_types

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "e16_topic"))
from topic_lib import article, metadata  # noqa: E402


def record(pmid=1, native=True, types=("D016428",), links=(), targets=()):
    return dict(pmid=pmid, is_pmid=native, pub_type_ui=list(types), mesh_ui=[], mesh_major=[],
                cc_reftype=list(links), cc_pmid=list(targets))


CASES = [
    ([record()], None),
    ([record(types=("D016428", "D016441"))], None),
    ([record(types=("D016428", "D016454"))], "review_types"),
    ([record(types=("D016428", "D016422", "D016454"))], "review_types"),
    ([record(types=("D016428", "D016420"))], "letter_comment_editorial"),
    ([record(types=("D016421",))], "letter_comment_editorial"),
    ([record(types=("D016428", "D016425"))], "erratum_notice_concern"),
    ([record(types=("D000075742",))], "erratum_notice_concern"),
    ([record(types=("D016441",))], "no_journal_article"),
    ([], "unknown_types"),
    ([record(native=False, types=("D016440",))], "unknown_types"),
    ([record(), record(2, False, ("D016440",), links=("RetractionOf",), targets=(1,))], None),
    ([record(native=False), record(2, False, ("D016425",))], None),
    ([record(native=False, types=("D016428", "D016422"))], "letter_comment_editorial"),
]


class TypeTests(unittest.TestCase):
    def test_categories_follow_fixed_order(self):
        for rows, expected in CASES:
            flags, group = categories(retained_types(rows))
            self.assertEqual(group, expected, rows)
            self.assertTrue(group is None or group in ORDER)

    def test_agreement_with_p16_metadata(self):
        for rows, _ in CASES:
            types = retained_types(rows)
            self.assertEqual(article(types), metadata(rows)["article"], rows)
            self.assertEqual(categories(types)[1] is None, metadata(rows)["article"], rows)

    def test_overlapping_flags(self):
        flags, group = categories({"D016428", "D016422", "D016420", "D016441"})
        self.assertTrue(flags["letter"] and flags["comment"] and flags["retracted_publication"])
        self.assertFalse(flags["no_journal_article"] or flags["review"])
        self.assertEqual(group, "letter_comment_editorial")


if __name__ == "__main__":
    unittest.main()
