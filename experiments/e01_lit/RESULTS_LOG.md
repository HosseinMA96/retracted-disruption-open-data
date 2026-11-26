# E01 literature gate: lab notebook

## e01_doi_20261109_01 (2026-11-10 03:45 UTC, laptop, network only)
- Command: `python3 -I e01_doi_check.py runs/e01_doi_20261109_01`
- Result: 26/26 DOIs resolved (Crossref 17, DataCite 9). Crossref bibliographic queries found 10.1016/j.joi.2025.101685 (OpenCitations vs WoS disruption, JOI 2025) and 10.1007/s11192-023-04873-5 (Leibel & Bornmann, Scientometrics 2023).
- Outputs: `dois.json`, `queries.json`, `run.json`, `SHA256SUMS` (< 30 KB in total; kept in git).
- Also used (not scripted): web searches 2026-11-09; full read of the Table 1 inventory in arXiv:2602.05140v1 (HTML). Summary in `../../lit/LIT.md`.
- Gate: original framing covered; integrity link open → decision E-R1 for the user.
