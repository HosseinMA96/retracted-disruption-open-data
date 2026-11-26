# E02 populations: lab notebook

## e02_pop_20261110_01 (VM vm-project-e, 134 s, via `vm/run_all.sh 20261110 01`)
SPEC v1. Inputs: D runs d05_match_20261101_02, d02_rw_20261101_01; C graph tables c6_full_20261031_02.
- Biomedical nodes published 2000–2017: 13,823,473; with journal and not a DOI duplicate: 12,522,210 (341,432 with zero references in the graph) → **eligible 12,180,778**.
- Retraction Watch matched iids: 53,170; of these, 328 fall in the window with zero references (excluded with all zero-reference papers).
- **Retracted (secondary, all): 10,450; primary (first notice after 31 Dec of pub_year + 5): 4,587.**
- By class (all / primary): honest error 1,488 / 294; misconduct 5,321 / 2,743; other 3,151 / 1,274; paper mill 490 / 276.
- Strata (journal × year): 5,458; 4 strata (4 retracted papers) have no control. Controls: 52,147 (K = 5).
- Context sample: 24,491 (20 retracted). Reviews: context 2,738, controls 6,032, retracted 920.
- Focal iids (union): 86,950. Files on the VM only: `~/e/data/work/e02/e02_pop_20261110_01/` (labels.parquet sha256 e8f7465a…, focal_iids.parquet sha256 8773bcb0…).
- Note: paper-mill papers in the primary set are few (276) because most paper-mill retractions concern papers published after 2017 (outside the complete 5-year window).
