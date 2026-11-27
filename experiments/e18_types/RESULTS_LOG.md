# P18 lab notebook

- 2026-11-27 UTC, before execution: P18 plan published as `ac8d639a1157c70f57a1ebd6d0ec3da984d21dd9`
  (anonymous commit page and raw POSTHOC.md bytes verified). Three synthetic tests pass locally (fixed category
  order; agreement with P16's `topic_lib.metadata` article flag, including DOI-only notices and unknown types).
  A throwaway synthetic end-to-end run exercised the bounded lookup, unlinked nodes and every guard.
  No real data were read before the VM run.
- `e18_types_20261127_01` (VM, started 23:50:33 UTC by the VM clock): 1:03.96 wall time, peak RSS 492,988 KB,
  exit 0. Tests passed on the VM; label and metadata-source hashes matched; P16 identifier-aware (3,626; 43,167)
  and P13 union-link (3,528; 43,152) eligible counts reproduced. Fetch checksums verified; VM deallocated.
- Primary: 961 of 4,587 fail (21.0%): review types 395; letter/comment/editorial 67; only notice types 499
  (overlapping: Retraction of Publication 458, Expression of Concern 47, Published Erratum 16); 682 failing papers
  carry Retracted Publication. Controls: 8,980 of 52,147 fail (17.2%): 6,032 / 2,518 / 265 / 165 (no Journal
  Article). Setting notice-type failures aside: 10.1% of primary papers vs 16.7% of controls. Interpretation in
  the paper is hedged: notice types on retracted originals are consistent with linked notice records.
