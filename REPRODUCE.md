# Reproducing Paper E

Every number in the paper comes from a run listed below; `FINDINGS.md` maps each claim to its run. Each run folder
(`experiments/<exp>/runs/<run_id>/`) holds `run.json` (parameters, SHA-256 of the script, of `SPEC.md` and, for post
hoc runs, of `POSTHOC.md`, input hashes, counts, runtime), `stdout.log`, small group-level outputs and `SHA256SUMS`.
Scripts refuse to write into an existing run folder, so a rerun always gets a new run ID.

## 1. Machine and environment
- Steps that read the citation graph need about 64 GB RAM and 150 GB of disk; they ran on one Azure
  `Standard_E8s_v6` VM (8 vCPU, 64 GB). Total compute for all E runs: under one VM-hour.
- Python environment: `vm/environment_e.lock.yml` (conda-forge; Python 3.11, DuckDB 1.5.6, pandas 3.1.0, NumPy 2.4.6,
  SciPy 1.17.1, statsmodels 0.15.0, pyarrow 25). Create it with `micromamba create -n d -f vm/environment_e.lock.yml`.
- Figures run on a laptop with Matplotlib 3.10.8 (any Python ≥ 3.10).
- VM control: `vm/vmctl.sh` (`start`, `stop` = deallocate, `ssh`, `push` copies the code to `~/e`, `fetch RUN` copies a
  run back and checks its checksums). The pipelines `vm/run_all.sh`, `vm/run_posthoc*.sh` run the steps in order and
  deallocate the VM at the end.
- `experiments/<exp>/common.py` is the same file in every folder (identical SHA-256). Paths: `C_WORK` (graph tables),
  `D_WORK` (Project D tables), `E_DATA` (this project's work tables).

## 2. Inputs
| Input | Source | Check |
|---|---|---|
| Citation graph, January 2024 | Illinois Data Bank, doi:10.13012/B2IDB-5216575_V1 | sizes and SHA-256 in https://github.com/HosseinMA96/citation-stacking-open-data (`c01_journal_graph/RESULTS_LOG.md`) |
| Graph tables `edges.parquet`, `pubs_slim.parquet`, `pubs_j.parquet` | built by `c6_full_run.py` (run `c6_full_20261031_02`) in https://github.com/HosseinMA96/citation-stacking-open-data | its `run.json` |
| OpenCitations Meta CSV dump | figshare doi:10.6084/m9.figshare.21747461.v7 | SHA-256 `924ac7acc838024bdc78982970c7b1a4bcd4da5f8ad62c47a94d9580df10ca44` |
| Retraction Watch | `gitlab.com/crossref/retraction-watch-data`, commit `a98cc7e2dd37b8affab780096048b261833ecc11` (2026-10-30) | as in Project D |
| PubMed 2026 baseline, ID map, Retraction Watch match | Project D runs `d04_pubmed_20261101_01`, `d00_idmap_20261101_01`, `d02_rw_20261101_01`, `d05_match_20261101_02` in https://github.com/HosseinMA96/retracted-neighbours-open-data | their `run.json`; linked table on Zenodo, doi:10.5281/zenodo.23874477 |

## 3. Runs, in order (the runs cited in the paper)
Run each from its experiment folder: `python <script> <args>`.

| Step | Command | Time on the VM |
|---|---|---|
| Literature DOIs (laptop) | `e01_lit/e01_doi_check.py runs/e01_doi_20261109_01` | seconds |
| Unit test, CD | `e03_cd5/test_cd.py` | seconds |
| Populations (SPEC v1) | `e02_population/e02_population.py e02_pop_20261110_01` | 2 min |
| Frozen CD5 scores | `e03_cd5/e03_cd5.py e03_cd5_20261110_01 e02_pop_20261110_01 16` | 2.5 min |
| Evaluation (SPEC v1) | `e04_eval/e04_eval.py e04_eval_20261110_01 e02_pop_20261110_01 e03_cd5_20261110_01` | 20 s |
| P1 | `e05_posthoc/e05_refs.py e05_refs_20261110_01 e02_pop_20261110_01 e03_cd5_20261110_01` | 1 s |
| P2 populations / scores / evaluation | `e02_population.py e02_pop_cd3_20261110_01 2019 3`; `e03_cd5.py e03_cd5_cd3_20261110_01 e02_pop_cd3_20261110_01 16 3`; `e04_eval.py e04_eval_cd3_20261110_01 e02_pop_cd3_20261110_01 e03_cd5_cd3_20261110_01` | 5.5 min |
| Unit test, yearly counts | `e07_yearly/test_yearly.py` (vs brute force and vs `cd_lib`) | seconds |
| Yearly counts (frozen) | `e07_yearly/e07_yearly.py e07_yearly_20261123_02 e02_pop_cd3_20261110_01,e02_pop_20261110_01 e03_cd5_cd3_20261110_01,e03_cd5_20261110_01` | 3 min |
| P3–P8 | `e08_posthoc2/e08_eval.py e08_posthoc2_20261123_02 e02_pop_20261110_01 e03_cd5_20261110_01 e04_eval_20261110_01 e02_pop_cd3_20261110_01 e03_cd5_cd3_20261110_01 e04_eval_cd3_20261110_01 e07_yearly_20261123_02` | 3.5 min |
| P9 | `e09_pretrend/e09_pretrend.py e09_pretrend_20261123_01 e02_pop_cd3_20261110_01 e03_cd5_cd3_20261110_01 e07_yearly_20261123_02 e08_posthoc2_20261123_02` | seconds |
| P10 | `e10_describe/e10_nk.py e10_nk_20261123_01 e02_pop_20261110_01 e03_cd5_20261110_01` | seconds |
| Test of P11 (synthetic data) | `e11_controls/test_e11.py` | seconds |
| P11 | `e11_controls/e11_controls.py e11_controls_20261126_01 e02_pop_20261110_01 e03_cd5_20261110_01 e04_eval_20261110_01 e02_pop_cd3_20261110_01 e03_cd5_cd3_20261110_01 e04_eval_cd3_20261110_01` | seconds |
| Test of P12 (synthetic data) | `e12_diagnostics/test_diagnostics.py` | seconds |
| P12 matched-log and paired annual diagnostics | `e12_diagnostics/e12_diagnostics.py e12_diag_20261126_01` (fixed frozen input runs in the script) | 1 s |
| Test of P13 (synthetic classification and matching) | `e13_article_types/test_sensitivity.py` | seconds |
| P13 article-type restriction | `e13_article_types/e13_article_types.py e13_articles_20261126_01` (frozen score/label tables plus PubMed metadata, no graph rerun) | 4.6 min |
| Test of P14 (synthetic names, duplicate/reinstated records, threshold, empty comparison) | `e14_authors/test_authors.py` | seconds |
| P14 author-name exclusion | `e14_authors/e14_authors.py e14_authors_20261126_01` (frozen tables and raw RW CSV, no graph rerun) | 19 s |
| Figures (laptop) | `e06_figures/e06_figs_v2.py e06_fig_20261126_06 e04_eval_20261110_01 e04_eval_cd3_20261110_01 e08_posthoc2_20261123_02 e09_pretrend_20261123_01 e12_diag_20261126_01` | seconds |
| Paper | `cd paper/journals/joi && tectonic -X compile main.tex`; upload packages: `./build_submission.sh` | – |

## 4. Determinism and checks
- Controls are chosen by `hash(iid, 20261109)` in DuckDB; bootstrap draws use NumPy `SeedSequence(20261109)` after
  sorting strata; no other randomness.
- The evaluation scripts verify the SHA-256 of the frozen score and count files before reading any label.
- `e07` checks that its yearly counts summed over each scoring window equal the frozen counts of both score runs
  (0 mismatches over 110,462 and 86,950 papers). `e08` replays `e04` in the same order with the same seeds and stops
  unless all 22 v1 comparisons are reproduced exactly; `e09` reproduces the P6 estimate of `e08` first; `e11` reproduces
  every `e04` value it uses (and `e02`'s counts of strata and controls) first.
- P12 reproduces all seven original P9 paired points/counts, P11's 4,586 / 31,662 compared population and both P1
  log-of-mean points before computing new confidence intervals and matched mean-of-log diagnostics.
- The current figure run plots paired annual points with P12 intervals. Figure 1 is two by two; normal-size labels
  and legends print at about 8.62 pt. Earlier figure runs remain immutable, and plotted values are unchanged,
  with TrueType fonts retaining en dashes.
- Pre-specification provenance: `experiments/spec_provenance.json`, the unchanged `SPEC.md`, and the score and
  evaluation run records. The original private Git commit is dated before scoring; this is not an independent public
  preregistration timestamp. The original commit history remains private and cannot be inspected in this release.
- P13 replays both original primary comparisons and all six P7 models before filtering. It verifies frozen score
  and label hashes, reproduces the original review flags, and records type-source, script, helper and pre-run plan
  hashes. It retains Journal Article, excludes review/editorial/notice types on any linked record, and deliberately
  retains Retracted Publication. Both groups are filtered; original controls and year thresholds are not redrawn
  or recalibrated. PubMed Journal Article is an operational proxy, not a guarantee of original research.
- P14 checks raw RW CSV and D2 hashes, reproduces D2 paper keys/reinstatement exclusions, and records/checks the
  stability of the D5 mapping hash. It verifies frozen label/score hashes and reproduces original CD mean intervals,
  positive/top-5% odds ratios and retracted comparison counts, plus P5 DI_nok points/counts, before exclusion.
  Names are semicolon-delimited, whitespace-collapsed and casefolded, without fuzzy matching. At least ten distinct
  non-reinstated paper keys in the full snapshot qualify a name; any qualifying linked key excludes a primary node.
  Controls, scores and thresholds stay fixed. Missing names are retained; 2,000 journal-year bootstrap draws use
  seed 20261109 with child-generator offset 2000. Only aggregates are released; names are not disambiguated identities.

## Submission document build
`paper/journals/joi/build_submission.sh` also invokes `build_declaration.py` to create the editable
`competing_interests.docx` from the manuscript title and declaration text. This needs `python-docx==1.2.0`;
`DOCX_PYTHON` selects its interpreter. A local DOCX is not an output of Elsevier's declarations tool:
the author must still complete that tool and upload its generated `.doc`/`.docx`.

## 5. Runs not cited
- `e07_yearly_20261123_01`, `e08_posthoc2_20261123_01`: notice rule matched PubMed publication types by name; the 2026
  baseline names D016440 "Retraction Notice", so the rule was changed to type identifiers before any P8 result was read
  (POSTHOC.md P8 amendment). Kept with `SUPERSEDED.txt`.
- `e06_fig_20261110_01`, `_02`, `e06_fig_20261123_01`: layout fixes (see `e06_figures/RESULTS_LOG.md`).
