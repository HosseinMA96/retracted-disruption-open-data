# P13 article-type sensitivity

Plan recorded in POSTHOC.md before running. Original score/label hashes and CD5/CD3 primary/P7 estimates must
reproduce before filtering. The operational Journal Article proxy excludes reviews and editorial/notice types,
but retains Retracted Publication. Only aggregate results are released; the VM is deallocated after fetching.

## e13_articles_20261126_01 (2026-11-26T19:34:33Z)

Executed script/helper/plan hashes match the local release sources. Frozen score and label hashes verified;
CD5/CD3 primary points, intervals, odds ratios and compared counts reproduced; all six P7 models reproduced.
The original PubMed review flags also reproduced before applying the restriction.
Runtime 271.0 s (4:38.32 wall), maximum RSS 10,977,488 KB, no swaps. Aggregate fetch checksums passed;
the VM was then deallocated and its deallocated state independently checked.

- CD5: 3,528 eligible/scored primary articles, 3,521 compared with 23,839 controls in 1,841 strata.
  Mean gap 0.000761013 (-0.000218134 to 0.001886385); positive OR 1.244691 (1.131045-1.369756);
  top-5% OR 1.072056 (0.861843-1.333544).
- CD5 top-5% conditional logit: 1.073582 (0.862298-1.336636) unadjusted;
  1.639967 (1.279035-2.102752) with log references; 1.394909 (1.078519-1.804114) with references and citations.
- Matched mean log reference gap +0.064059 (0.045366-0.083135); log-of-stratum-mean gap +0.005866.
  Matched mean log citation gap +0.265192 (0.233241-0.299106).
- CD3: 5,600 eligible, 5,599 scored and 5,592 compared primary articles; 37,334 compared controls in 2,735 strata.
  Mean gap 0.000871718 (0.000183705-0.001694908); positive OR 1.322477 (1.229414-1.422585);
  top-5% OR 1.213136 (1.035646-1.421045).
- All class-specific estimates and DI_nok gaps are in results.json. The main mean/top-tier findings are not
  substituted for the pre-specified results. Article-type restriction changes both populations and retains the
  original year thresholds; it is not guaranteed to identify only original research or to isolate a causal mechanism.
