# P14 author-name exclusion

Planned in POSTHOC.md before execution. Threshold: at least 10 distinct non-reinstated retracted paper keys
per normalized author name in the full frozen RW snapshot. Exclude linked primary nodes; keep original controls,
scores and year thresholds. Blank/placeholder author fields are retained and counted as missing.
This is a name-based sensitivity, not author disambiguation or an author-cluster bootstrap. Release aggregates only.

## e14_authors_20261126_01 (2026-11-26)

Author-rule tests passed before the run. Raw CSV and D2 hashes and paper-key/reinstatement counts reproduced.
D5 mapping hash recorded and unchanged during the join. Frozen label/score hashes verified; original CD5/CD3
primary points, 95% bootstrap intervals, positive/top-5% odds ratios and comparison counts reproduced.
Original P5 DI_nok mean points and comparison counts reproduced before filtering.

1,649 normalized names reach the threshold across 62,734 non-reinstated paper keys. No missing author names
among either primary population. CD5 removes 2,280 / 4,587: 2,307 scored, 2,306 compared with 23,999 controls.
CD gap +0.00027 (-0.00113 to 0.00195); positive OR 1.26 (1.12-1.41); top5 OR 0.97 (0.75-1.25).
DI_nok +0.060765 (0.037890-0.083505), 2,260 compared; misconduct +0.078988 (0.047707-0.109717).

CD3 removes 3,722 / 7,350: 3,628 eligible, 3,627 scored, 3,626 compared with 37,294 controls.
CD gap +0.00063 (-0.00047 to 0.00184); positive OR 1.32 (1.21-1.44); top5 OR 1.03 (0.85-1.25).
DI_nok +0.068510 (0.048250-0.089267), 3,485 compared.

Wall time 19.12 seconds; max RSS 644,792 KB; no swap. Aggregate results/log/manifest fetched and
SHA256SUMS verified. VM deallocated after retrieval. No author names, identifiers or per-paper associations released.
Interpretation: the DI_nok contrast persists after this exclusion; the shorter-window top-tier excess weakens.
