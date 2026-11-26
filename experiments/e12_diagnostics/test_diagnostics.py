import numpy as np
import pandas as pd
from diagnostics_lib import event_pairs, matched_logs, boot_mean, boot_weighted


labels = pd.DataFrame([
    [1, "retracted", "A", 2010, True, "2016-01-01"],
    [2, "retracted", "A", 2010, True, "2016-01-01"],
    [3, "control", "A", 2010, None, None],
    [4, "control", "A", 2010, None, None],
    [5, "retracted", "B", 2010, True, "2016-01-01"],
    [6, "control", "B", 2010, None, None],
], columns=["iid", "grp", "journal_id", "pub_year", "primary_set", "first_notice"])
yearly = pd.DataFrame([[1, 2013, 3, 1, 1, 0], [2, 2013, 0, 0, 0, 0],
                       [3, 2013, 1, 1, 0, 0], [4, 2013, 0, 0, 0, 0],
                       [5, 2013, 1, 1, 0, 0], [6, 2013, 0, 2, 0, 0]],
                      columns=["iid", "y", "ni", "nj", "ni_ntc", "nj_ntc"])
balanced, pairs = event_pairs(labels, yearly)
assert len(balanced) == 3 and len(pairs) == 2
np.testing.assert_allclose(pairs.paired_diff, [1/3, 1])
estimate = boot_mean(pairs, "paired_diff", np.random.default_rng(1), 1000)
assert estimate["n"] == 2 and estimate["strata"] == 2 and abs(estimate["mean"] - 2/3) < 1e-12
assert estimate == boot_mean(pairs, "paired_diff", np.random.default_rng(1), 1000)
scores = pd.DataFrame([[1, 2010, 0.1, 1, 2], [2, 2010, 0.2, 99, 3],
                       [3, 2010, 0.1, 9, 1], [4, 2010, 0.2, 9, 1],
                       [5, 2010, 0.1, 3, 4], [6, 2010, 0.1, 1, 2]],
                      columns=["iid", "pub_year", "cd_w0", "n_refs", "cites_w0"])
result = matched_logs(labels, scores)["n_refs"]
expected = (np.log(2) + np.log(100) + np.log(4) - 2*np.log(10) - np.log(2)) / 3
assert abs(result["difference"] - expected) < 1e-12
assert abs(result["difference"] - result["log_of_mean_difference"]) > 0.1
assert result["retracted_compared"] == 3 and result["controls_compared"] == 3
assert boot_weighted(result["groups"], np.random.default_rng(2)) == boot_weighted(result["groups"], np.random.default_rng(2))
try:
    event_pairs(labels, pd.concat([yearly, yearly.iloc[:1]]))
except ValueError:
    pass
else:
    raise AssertionError("Duplicate yearly rows were accepted")
print("paired counts, notice exclusion, uncited handling, mean-of-logs, bootstrap determinism and duplicate guard: OK")
