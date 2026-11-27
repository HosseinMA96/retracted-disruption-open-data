# P16 lab notebook

- 2026-11-27 UTC, before execution: the author approved up-to-five positive-overlap major-MeSH
  Jaccard matches inside the original journal/year control pool. Type-linkage and interval plan
  published as `018d835f7db497a788320977d54d4b62f3755918`; seven focused synthetic tests passed.
- VM startup completed, but the first SSH connection was refused before any script ran or data
  were queried. Retry only after verifying SSH readiness; no empirical run was overwritten.
- `e16_topic_20261127_01` was blocked after roughly fourteen minutes with no estimates, low CPU,
  about 13 GiB RSS, 49 GiB available RAM and no swap. Terminated its known PID; the wrapper preserves
  run metadata, manifest and stdout. Exact source archive: `versions/e16_01_source.tgz`.
  Retry `_02` bounds metadata extraction before nested fields and uses one DuckDB thread/6 GB limit.
  Statistical rules, seed and output definitions are unchanged.
- `_02` bounded lookup completed in 86.70 seconds (peak RSS 882,228 KB), then failed before estimates:
  four of 110,462 graph nodes had no current PubMed metadata. A guard incorrectly required linkage for
  every focal record. The existing plan permits missing-source metadata as unknown; `_03` explicitly
  counts and represents that state without imputing types or topics. Exact source: `versions/e16_02_source.tgz`.
  Frozen baseline and P13/P14 point/count checks remain mandatory.
- `_03` completed in 1:37.34 (peak RSS 1,098,240 KB); eight synthetic tests, frozen-input checks,
  original P5/P13/P14 means/counts and P13 CD comparisons passed. Aggregate fetch checksums verified;
  VM deallocated. Earlier attempts and their exact sources remain intact.
- DOI-only notices target native PMIDs for 106 primary papers and 13 drawn controls. PMID priority restores
  article eligibility for 98 and 15 papers, respectively; this includes removal of any DOI-only excluded
  type, not just notices. Primary/drawn-control eligibility is 3,626/4,587 and 43,167/52,147.
- Major-MeSH matching retains only 540 papers: gap 0.049776862 (-0.012347972, 0.097392746), versus
  0.082465018 (-0.005868149, 0.136079661) using the exact-retained-paper journal/year baseline.
  The article-type version retains 417: 0.062789308 (-0.002551950, 0.123826087), versus baseline
  0.085793242 (-0.005036865, 0.148465208). Both topic intervals include zero: inconclusive, not confirmation.
  No rule was relaxed after seeing these results.
- Main Table 2 uses PMID-prioritized article estimates; original union-link P13 results stay in the appendix.
  Fixed-window DI_nok means now use whole-journal intervals throughout the manuscript, including Figure 2.
  Overall unfiltered intervals come verbatim from P15; other fixed-window intervals come from `_03`.
  Original CD/event intervals and all immutable earlier outputs are unchanged.

The identifier map is native OpenCitations Meta identifiers joined to graph nodes, not a PubMed-augmented
PMID map (`D_retraction_contamination/experiments/d00_setup/d00_idmap.py`). PMID priority therefore distinguishes
the graph's own PMID links from additional exact-DOI PubMed matches.

The complete plan is in `../../POSTHOC.md`. Per-run JSON, aggregate outputs, logs, manifest and checksums
live in `runs/<run_id>/`. Publication-level metadata/matches and author names stay on the VM.
