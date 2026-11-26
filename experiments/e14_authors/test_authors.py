from author_lib import author_exclusions, paper_key, names

assert paper_key("HTTPS://doi.org/10.TEST/A", "") == "10.test/a"
assert paper_key("", "00042") == "pmid:42"
assert paper_key("", "invalid") is None
assert names(" Person A ; PERSON  A; n/a ; ; [unknown]") == {"person a"}


def row(doi, author, nature="Retraction", pmid=""):
    return {"OriginalPaperDOI": doi, "OriginalPaperPubMedID": pmid, "RetractionNature": nature, "Author": author}


rows = [row(f"10.test/{i}", "Person A; Person B") for i in range(10)]
rows += [row("10.test/0", "PERSON   A"), row("10.test/other", "Person C"), row("10.test/missing", ""),
         row("10.test/reinstated", "Person C"), row("10.test/reinstated", "", "Reinstatement")]
keys, known, excluded, stats = author_exclusions(rows)
assert len(excluded) == 10 and stats["names_at_or_above_threshold"] == 2
assert "10.test/other" in known and "10.test/other" not in excluded
assert "10.test/missing" not in known and "10.test/missing" not in excluded
assert "10.test/reinstated" in keys and "10.test/reinstated" not in known
_, _, excluded9, _ = author_exclusions(rows[:-1] + [row("10.test/9", "", "Reinstatement")])
assert not excluded9
_, known_pmids, _, _ = author_exclusions([
    row("", "Person D", pmid="42"), row("10.test/reinstated", "Person E"),
    row("10.test/reinstated", "", "Reinstatement", pmid="42")])
assert not known_pmids
_, _, duplicate_exclusions, _ = author_exclusions([row("10.test/single", "Person A")] * 10)
assert not duplicate_exclusions
import pandas as pd
import numpy as np
from e14_authors import evaluate

ret = pd.DataFrame({"journal_id": [1], "pub_year": [2000], "cd_w0": [0.0]})
ctl = ret.assign(journal_id=2)
empty = evaluate(ret, ctl, "cd_w0", {2000: 0.1}, np.random.default_rng(1))
assert empty["status"].startswith("not estimable:") and "diff" not in empty
print("Author normalization, distinct-paper counts, duplicate notices, missing names, reinstatement and threshold: OK")
