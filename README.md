# MFP-Score, OPR, and source-grounded evidence workflow for monolithic MOF formation

This repository contains the MIT-licensed supplementary software and machine-readable evidence package for the manuscript:

> **A Reproducible Software-Resource Workflow for AI-Guided Prioritization of Monolithic Metal-Organic Framework Formation**

Release: **v1.1.0**.

## Authors and correspondence

- Jinnan Wei
- Andrew E. H. Wheatley (corresponding author; aehw2@cam.ac.uk)

Affiliation: Yusuf Hamied Department of Chemistry, University of Cambridge, Lensfield Road, Cambridge CB2 1EW, UK.

## Funding

This work received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

## What is included

1. **Synthetic-curated demonstration workflow**
   - transparent MFP-Score baseline;
   - hypothesis-generating OPR route generator;
   - capillary-risk, uncertainty, ablation, sensitivity, manifest and checksum outputs.

2. **Source-grounded descriptive evidence workflow**
   - 49 human-verified condition-level records from nine primary studies;
   - controlled outcome-status semantics and nullable schemas;
   - descriptive source-coverage and condition-contrast tables;
   - registry-to-model projection adapter with a hard no-scoring gate;
   - neutral evidence workbook and validation reports.

## Quick start

```bash
cd SupplementarySoftware1
python3 run_all.py
python3 source_grounded_evidence/run_evidence_tables.py
python3 source_grounded_evidence/scripts/registry_to_model_projection_adapter.py \
  source_grounded_evidence/data/AUTHORITATIVE_EVIDENCE_REGISTRY.csv \
  source_grounded_evidence/adapter_outputs
```

Expected boundaries:

```text
legacy synthetic-curated validation: PASS
source-grounded table generator: PASS
source-grounded scoring admitted: 0
synthetic imputation used: 0
```

## Scientific claim boundary

The source-grounded registry is not a benchmark, gold set or training dataset. Version v1.1.0 does **not** generate source-grounded MFP scores, OPR rankings, classifier metrics, accuracy/F1/AUPRC/calibration results, or synthetic imputations.

## Archive and citation

The previous synthetic-curated-only release was v1.0.1, archived at Zenodo DOI [10.5281/zenodo.20452017](https://doi.org/10.5281/zenodo.20452017).

The version-specific DOI for v1.1.0 is assigned by Zenodo when this GitHub release is processed. Consult the Zenodo record linked from the GitHub release for the minted DOI; do not substitute the v1.0.1 DOI.

## Release inventory

- `REPOSITORY_MANIFEST_v1.1.0.md`: current public archive contents and scope.
- `REPOSITORY_FILE_INVENTORY_v1.1.0.csv`: machine-readable release inventory.
- `SHA256SUMS_v1.1.0.txt`: SHA-256 checksums for release files.
- `validate_v29A_2_1_final_release_state.py`: final release-state and archive-hygiene validator.

## License

MIT License. See `LICENSE`.
