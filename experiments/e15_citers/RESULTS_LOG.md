# P15 citing-record and journal sensitivity

Plan recorded in POSTHOC.md before execution and published at
9c4ba4ca9bca39542f86a014bda2db463c1534ac. No empirical P15 results were read before that commit.
Main filter removes notices, comments/letters and retracted citing papers, with overlap deduplicated.
Original references, populations, control draws and scores remain unchanged.
Mean differences and weighted within-stratum linear models use whole-journal bootstrap intervals.
The top-ten-journal exclusion is fixed from original primary-set counts before filtering.
Only aggregate outputs are released; counting tables remain on the analysis VM.

## e15_citers_20261127_01: failed counting attempt

Synthetic tests passed; frozen score/label/yearly inputs were checked. The join building incoming citers
exhausted DuckDB's temporary-disk allowance (71.8 GiB) before any P15 estimate was produced.
Elapsed time 12:05.08; peak RSS 50,386,716 KB. Initial run metadata and the failure log were fetched and
checksum-verified, and the VM deallocated. No results.json exists and no scientific estimate is taken from this run.
Exact pre-retry counting source is preserved in versions/e15_01_source.tgz with checksum.
The retry materializes focal incoming edges and their year lookup before joining, leaving the statistical plan
unchanged. It uses a new run ID; no failed-run record is overwritten.

## e15_citers_20261127_02: completed

The bounded joins passed both synthetic tests and all empirical baseline checks: immutable labels/scores/yearly
hashes, original per-paper counts, independent incoming-citer totals, P8 notice removal, original P5 mean/counts,
and equality of the unadjusted weighted model and matched mean. Runtime 2:49.01; peak RSS 1,716,668 KB.
Aggregate records were fetched and SHA-256 verified; the VM was deallocated.

Five-year DI_nok matched gaps (95% whole-journal bootstrap intervals):
unfiltered +0.066768 [0.034454, 0.094954]; notices removed +0.068584 [0.037091, 0.096448];
also Comment/Letter +0.069583 [0.036721, 0.098340]; full filter +0.081598 [0.049014, 0.109965].
The full filter retains 4,504 retracted / 30,389 control papers in 2,190 strata and 972 journals;
13 primary scores become undefined. It increases, rather than attenuates, the gap.
The fully filtered reference/citation-adjusted coefficient is +0.097434 [0.065435, 0.127391];
using original citation counts gives +0.098803 [0.064852, 0.129202].
Removing the top ten journals gives a matched gap of +0.052644 [0.032773, 0.074152]
(3,013 compared primary papers), or +0.070324 [0.049091, 0.091359] with both covariates.

Three-year fully filtered gap: +0.090398 [0.064238, 0.113946] (7,088 compared primary papers);
without the top ten journals: +0.081534 [0.064081, 0.099387] (5,057).
Class-specific results, exclusions, coverage, model coefficients and full-precision values are in results.json.
New journal intervals do not replace the original journal-year intervals. No causal or complete-coverage claim follows.

## e15_flow_20261127_01: population diagram

Generated from checksummed E2, E4, E11 and completed P15 aggregate files; no inferred counts.
The PDF/PNG and per-run metadata/checksums are preserved. Native labels are 11.5 pt and print at 8-9 pt
at manuscript width; text lies within the canvas. Flow appears as Figure 1, preceding the unchanged forest/event
figures (now Figures 2 and 3). Both the CD5 and DI_nok compared control counts are stated explicitly.
