# v1.1.0 - Source-grounded evidence integration release

## Summary

This backward-compatible minor release extends Supplementary Software 1 with a source-grounded, condition-level evidence layer while preserving the existing synthetic-curated demonstration workflow.

## Added

- 49-record human-verified condition-level evidence registry from nine primary studies;
- controlled outcome-status ontology and nullable evidence schema;
- descriptive source, framework, drying-route and condition-contrast summaries;
- registry-to-manuscript LaTeX table generator;
- registry-to-model projection-readiness adapter;
- descriptor compatibility and no-imputation policy;
- neutral source-grounded evidence workbook;
- validation reports, manifests and checksums;
- reviewer quick-start instructions for both workflows.

## Unchanged

- synthetic-curated MFP-Score and OPR demonstration logic;
- MIT License;
- no claim of validated production ML performance or experimental synthesis success.

## Explicit exclusions

This release does not generate source-grounded MFP scores, source-grounded OPR rankings, classifier training, accuracy/F1/AUPRC/calibration metrics or synthetic imputations. The 49-record registry is not a benchmark, gold set or training dataset.

## Previous version

v1.0.1 was archived at Zenodo DOI `10.5281/zenodo.20452017`.

## Authorship and funding lock

- Authors: Jinnan Wei and Andrew E. H. Wheatley.
- Corresponding author: Andrew E. H. Wheatley (aehw2@cam.ac.uk).
- Funding: no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

## DOI status

The v1.1.0 DOI is intentionally pending until the GitHub release is processed by Zenodo.

## Public archive hygiene

The v1.1.0 tagged source snapshot excludes obsolete v1.0.0/v18 release-assembly files, draft DOI placeholders, internal QC logs and stale package indexes. Current inventory, manifest and checksums are generated from the final tracked tree.
