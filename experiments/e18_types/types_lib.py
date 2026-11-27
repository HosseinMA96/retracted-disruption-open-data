"""P18 categories of PMID-prioritized publication types (descriptive)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "e16_topic"))
from topic_lib import EXCLUDED, notice, values  # noqa: E402

JOURNAL_ARTICLE, RETRACTED_PUBLICATION = "D016428", "D016441"
CATEGORY_TYPES = {
    "review": {"D016454", "D000078182", "D017418"},
    "editorial": {"D016421"}, "letter": {"D016422"}, "comment": {"D016420"},
    "published_erratum": {"D016425"}, "retraction_notice": {"D016440"}, "expression_of_concern": {"D000075742"},
}
ORDER = ["review_types", "letter_comment_editorial", "erratum_notice_concern", "no_journal_article", "unknown_types"]
assert set().union(*CATEGORY_TYPES.values()) == EXCLUDED


def retained_types(rows):
    """Same record choice as topic_lib.metadata: native PMID records first, else DOI records without notices."""
    pmids = {int(r["pmid"]) for r in rows if r["is_pmid"]}
    chosen = [r for r in rows if r["is_pmid"]] if pmids else [r for r in rows if not notice(r)]
    return {t for r in chosen for t in values(r, "pub_type_ui")}


def categories(types):
    flags = {name: bool(types & uis) for name, uis in CATEGORY_TYPES.items()}
    flags["no_journal_article"] = JOURNAL_ARTICLE not in types
    flags["retracted_publication"] = RETRACTED_PUBLICATION in types
    flags["unknown_types"] = not types
    if not types:
        group = "unknown_types"
    elif flags["review"]:
        group = "review_types"
    elif flags["letter"] or flags["comment"] or flags["editorial"]:
        group = "letter_comment_editorial"
    elif flags["published_erratum"] or flags["retraction_notice"] or flags["expression_of_concern"]:
        group = "erratum_notice_concern"
    elif flags["no_journal_article"]:
        group = "no_journal_article"
    else:
        group = None
    return flags, group
