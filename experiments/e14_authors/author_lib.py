"""Exact author-name strings are a sensitivity device, not disambiguated identities."""
import re
from collections import Counter, defaultdict

MISSING = {"unknown", "[unknown]", "n/a", "not available"}


def paper_key(doi, pmid):
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi.strip().lower())
    if doi.startswith("10."):
        return doi
    pmid = pmid.strip()
    if pmid.isdigit() and int(pmid) > 0:
        return f"pmid:{int(pmid)}"
    return None


def names(text):
    values = {" ".join(value.split()).casefold() for value in text.split(";")}
    return values - MISSING - {""}


def author_exclusions(rows, threshold=10):
    per_paper = defaultdict(set)
    all_keys, reinstated = set(), set()
    for row in rows:
        key = paper_key(row["OriginalPaperDOI"], row["OriginalPaperPubMedID"])
        if row["RetractionNature"].strip() == "Reinstatement":
            doi_key = paper_key(row["OriginalPaperDOI"], "")
            pmid_key = paper_key("", row["OriginalPaperPubMedID"])
            reinstated.update(k for k in (doi_key, pmid_key) if k is not None)
        if row["RetractionNature"].strip() == "Retraction" and key is not None:
            all_keys.add(key)
            per_paper[key].update(names(row["Author"]))
    active = {key: values for key, values in per_paper.items() if key not in reinstated}
    counts = Counter(name for values in active.values() for name in values)
    frequent = {name for name, count in counts.items() if count >= threshold}
    excluded = {key for key, values in active.items() if values & frequent}
    known = {key for key, values in active.items() if values}
    return all_keys, known, excluded, {
        "retracted_paper_keys": len(all_keys), "non_reinstated_paper_keys": len(active),
        "papers_with_names": len(known), "normalized_names": len(counts),
        "names_at_or_above_threshold": len(frequent), "excluded_paper_keys": len(excluded),
    }
