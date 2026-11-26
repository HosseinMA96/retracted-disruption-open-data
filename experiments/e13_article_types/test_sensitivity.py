import numpy as np
import pandas as pd
from sensitivity_lib import is_article, matched, compare

assert is_article(["D016428", "D016441"])
for excluded in ["D016421", "D016422", "D016420", "D016425", "D016440", "D000075742",
                 "D016454", "D000078182", "D017418"]:
    assert not is_article(["D016428", excluded]), excluded
assert not is_article([]) and not is_article(None) and not is_article(["D016441"])
r = pd.DataFrame({"journal_id": ["a", "a", "b", "c"], "pub_year": [2000]*4,
                  "cd_w0": [0.2, -0.2, 0.3, np.nan]})
c = pd.DataFrame({"journal_id": ["a", "a", "b", "d"], "pub_year": [2000]*4,
                  "cd_w0": [0.1, -0.3, -0.1, 0.4]})
rr, cc, groups = matched(r, c, "cd_w0")
assert len(rr) == len(cc) == 3 and len(groups) == 2
x = compare(r, c, "cd_w0", {2000: 0.15}, np.random.default_rng(4), 100)
y = compare(r, c, "cd_w0", {2000: 0.15}, np.random.default_rng(4), 100)
assert x == y and np.isclose(x["diff"], 0.2) and x["controls_compared"] == 3
print("Article filter, retained retracted-publication type, missing types, matched strata and determinism: OK")
