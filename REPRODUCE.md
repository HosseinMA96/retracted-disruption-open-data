# Reproducing Paper E

Every number in the paper comes from a run listed below; `FINDINGS.md` maps each claim to its run. Each run folder
(`experiments/<exp>/runs/<run_id>/`) holds `run.json` (parameters, SHA-256 of the script, of `SPEC.md` and, for post
hoc runs, of `POSTHOC.md`, input hashes, counts, runtime), `stdout.log`, small group-level outputs and `SHA256SUMS`.
Scripts refuse to write into an existing run folder, so a rerun always gets a new run ID.

## 1. Machine and environment
- Steps that read the citation graph need about 64 GB RAM and 150 GB of disk; they ran on one Azure
  `Standard_E8s_v6` VM (8 vCPU, 64 GB). Step timings below exclude VM provisioning overhead;
  the failed P15 attempt is recorded separately.
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
| Test of P15 (synthetic filtered counts and independent weighted least squares) | `e15_citers/test_citers.py` | seconds |
| P15 citing-record filters, adjusted DI_nok means and journal sensitivities | `e15_citers/e15_citers.py e15_citers_20261127_02` | 2:49 |
| Test of P16 (synthetic metadata, nullable arrays, priority, matching and weights) | `e16_topic/test_topic.py` | seconds |
| P16 type audit, topic matching and fixed-window journal intervals | `e16_topic/e16_topic.py e16_topic_20261127_03` (fixed parent runs in script) | 1:37 |
| Test of P17 (synthetic graphs vs brute force and the frozen counter; journal Mantel–Haenszel resampling) | `e17_coverage/test_coverage.py` | seconds |
| P17 citer coverage, coverage-restricted DI_nok/sign and journal-clustered primary intervals | `e17_coverage/e17_coverage.py e17_coverage_20261127_01 4169ea7cbd6a600f420c6871c566bdaa37b5b214` (via `vm/run_p17.sh`) | 2:54 |
| Test of P18 (category order; agreement with P16 metadata) | `e18_types/test_types.py` | seconds |
| P18 composition of article-type filter failures | `e18_types/e18_types.py e18_types_20261127_01 ac8d639a1157c70f57a1ebd6d0ec3da984d21dd9` (via `vm/run_p18.sh`) | 1:04 |
| Test of P19 (flag selection; conditional-logit wrapper) | `e19_models/test_models.py` | seconds |
| P19 PMID-priority conditional-logit models | `e19_models/e19_models.py e19_models_20261127_01 d14be2e63862fd8a2c755b9ac2b2de3e9a59afb6` (via `vm/run_p19.sh`) | 4:55 |
| Figures (laptop) | `e06_figures/e06_figs_v2.py e06_fig_20261127_10 e04_eval_20261110_01 e04_eval_cd3_20261110_01 e08_posthoc2_20261123_02 e09_pretrend_20261123_01 e12_diag_20261126_01 e16_topic_20261127_03` | seconds |
| Population flow (laptop) | `e15_citers/flow_diagram.py e15_flow_20261127_02 e15_citers_20261127_02` | seconds |
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
- The forest and event figure run plots paired annual points with P12 intervals. The forest is two by two; normal-size labels
  and legends print at about 8.62 pt. Earlier figure runs remain immutable, and plotted values are unchanged,
  with TrueType fonts retaining en dashes.
  Run _08 moves the event legend below both axes, clear of the notice lines; the forest is byte-identical to _07.
  Run _09 makes all four forest null lines visible above the grid without changing plot marks; the event remains
  byte-identical to _08. Run _10 replaces only fixed-window DI_nok intervals with P16 whole-journal intervals;
  CD mean/OR points and intervals and the event PDF are unchanged.
  The caption distinguishes the CD journal-year and DI_nok whole-journal resampling units.
  The population flow is now Figure 1, the forest Figure 2 and the event plot Figure 3.
  Flow run _02 corrects subscript notation and puts exclusions before the final eligible count; all inputs and
  numbers match _01. The old flow source is preserved in commit c1d69e904178a0d4550720d9365c827c319f181a.
- Pre-specification provenance: `experiments/spec_provenance.json`, the unchanged `SPEC.md`, and the score and
  evaluation run records. The original private Git commit is dated before scoring; this is not an independent public
  preregistration timestamp. The original commit history remains private and cannot be inspected in this release.
  P15 VM run timestamps and laptop figure timestamps come from different host clocks; Git author/committer
  dates are client-generated. `clock_sources` documents the non-monotonic records without claiming a measured
  one-hour offset or rewriting immutable timestamps. Cross-host timestamp strings alone cannot prove chronology.
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
- P15 was publicly planned at `9c4ba4ca9bca39542f86a014bda2db463c1534ac` before execution. It checks frozen
  labels/scores/yearly files, replays per-paper counts, independently counts incoming citers, reproduces P8
  notice removals and original P5 means/counts, and verifies the unadjusted weighted model equals the matched mean.
  Nested exclusions remove notices, then Comment/Letter, then retracted citing papers, without changing focal
  references. Retraction flags use the full snapshot, not status when citing. New intervals use 2,000
  whole-journal resamples (seed 20261109, child offset 3000); original strata intervals remain unchanged.
  Models use weights 1 for retracted papers and n_retracted/n_control for controls within each used stratum.
  Top-ten journals are ranked on original primary counts, with journal-ID tie breaks; no controls are redrawn.
  Only aggregate results are public; `E_DATA/e15/<run>/removed_yearly.parquet` stays on the VM.
  `vm/run_p15.sh` runs the tests and analysis; the controller must fetch records and deallocate the VM afterward.
- P16 was publicly planned at `018d835f7db497a788320977d54d4b62f3755918` before execution.
  Native OpenCitations PMID links are prioritized; without them, exact-DOI records are used after notice exclusion.
  Missing source nodes remain explicitly unknown. It reproduces original P13 type flags/CD estimates and P5/P13/P14
  DI_nok points/counts before adding identifier-prioritized estimates and whole-journal intervals.
  Topic matching uses unfiltered five-year DI_nok, major-MeSH sets, up to five highest positive Jaccard controls
  from the original journal/year pool, reuse and SHA-256 ties `20261109|retracted_iid|control_iid`.
  Exact-retained-paper baselines use all descriptor-eligible stratum controls. Article restriction repeats the
  same rule. Matches stay fixed during 2,000 whole-journal draws (seed 20261109, child offset 4000).
  Metadata lookup is bounded and materialized before nested fields, with one DuckDB thread/6 GB limit.
  `vm/run_p16.sh` runs tests/analysis; publication-level types, topics and matches stay on the VM.
- P17 was publicly planned at `4169ea7cbd6a600f420c6871c566bdaa37b5b214` before execution. It verifies frozen
  label/score hashes and the P15 graph hashes, rebuilds window citers with P15's `build_citers`, and independently
  reproduces every paper's frozen n_i/n_j, the P15 unfiltered DI_nok gap and E4's mean gap and odds ratios.
  Citer coverage is the out-degree in the same graph (self-loops excluded). Restricted counts keep citers with
  at least 10 or 25 references; references, controls and strata are fixed. Whole-journal intervals use 2,000
  draws (seed 20261109, child offset 5000); Mantel–Haenszel components are summed within journals.
  `vm/run_p17.sh` runs tests/analysis; citer degrees and per-paper values stay on the VM.
- P18 was publicly planned at `ac8d639a1157c70f57a1ebd6d0ec3da984d21dd9` before execution. It rebuilds P16's
  PMID-prioritized types with the same bounded lookup and `topic_lib`, reproduces P16/P13 eligible counts, and
  counts excluded types among failing papers (overlapping and in a fixed order). Descriptive; no estimates.
- P19 was publicly planned at `d14be2e63862fd8a2c755b9ac2b2de3e9a59afb6` before execution. It rebuilds both article
  flags, reproduces P13's six union-link conditional-logit models (tolerance 1e-6) and P16's PMID-priority
  Mantel–Haenszel odds ratios, then fits the same six models on the PMID-priority sample.
  The frozen parser records major flags on DescriptorName, not QualifierName. A read-only synthetic audit
  confirms qualifier-only flags are omitted; P16 therefore tests descriptor-major matching, not all major headings.
  See `experiments/e16_topic/RESULTS_LOG.md`. Recovering qualifier-only flags requires a new extraction and planned rerun.

## Submission document build
`paper/journals/joi/build_submission.sh` also invokes `build_declaration.py` to create the editable
`competing_interests.docx` from the manuscript title and declaration text. This needs `python-docx==1.2.0`;
`DOCX_PYTHON` selects its interpreter. A local DOCX is not an output of Elsevier's declarations tool:
the author must still complete that tool and upload its generated `.doc`/`.docx`.
JOI's single-anonymized review process requires the identified source package. The build no longer generates
an anonymized variant; author and GitHub-link presence are checked. See `paper/journals/joi/UPLOAD.md` for exact
files and the required Editorial Manager pdfLaTeX-generated PDF check.
The build also compiles the separate cover letter; both `cover_letter.tex` and `cover_letter.pdf` are released.
It names the companion arXiv preprint and shared linked dataset. The cover letter is not part of the manuscript ZIP.
The build also creates `highlights.docx` from `highlights.txt` and checks paragraph text and the 85-character limit.
The author confirmed mandatory separate highlights (3--5 bullets, at most 85 characters) and a 200-word
abstract limit. Direct access to the current publisher guide remains blocked; see `UPLOAD.md` for the source distinction.
The v0.17 build has a 197-word abstract, five highlights with a maximum of 76 characters and review line numbers.
The explanatory Figure 1 caption discloses AI code assistance; Methods names the plotting tools for Figures 2-3.
`build_submission.sh` also compiles `supplement.pdf` (P13/P16 detail moved unchanged from the appendix).
All three figure PDFs and earlier empirical results are unchanged.

## 5. Runs not cited
- `e16_topic_20261127_01`: stalled before estimates (14:10.82, peak RSS 13,613,512 KB), terminated by known PID.
  Available RAM was about 49 GiB with no swap; memory exhaustion was not demonstrated.
  `_02`: bounded metadata lookup completed, then an overly strict all-linked guard failed on four unknown nodes
  before estimates (1:26.70, peak RSS 882,228 KB).
  Both records and exact source archives are preserved. `_03` implements the already-planned unknown-source
  handling, not a changed statistical rule; eight tests and reproduction checks pass.
- `e15_citers_20261127_01`: failed incoming-citer join before any estimate (12:05.08, peak RSS 50,386,716 KB).
  Failure metadata/logs/checksums and the exact source snapshot are preserved. Retry _02 explicitly
  materializes bounded incoming-edge/year joins; the statistical design is unchanged.
- `e07_yearly_20261123_01`, `e08_posthoc2_20261123_01`: notice rule matched PubMed publication types by name; the 2026
  baseline names D016440 "Retraction Notice", so the rule was changed to type identifiers before any P8 result was read
  (POSTHOC.md P8 amendment). Kept with `SUPERSEDED.txt`.
- `e06_fig_20261110_01`, `_02`, `e06_fig_20261123_01`: layout fixes (see `e06_figures/RESULTS_LOG.md`).
