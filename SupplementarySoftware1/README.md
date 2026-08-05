# Supplementary Software 1 v1.1.0

This package supports the manuscript **A Reproducible Software-Resource Workflow for AI-Guided Prioritization of Monolithic Metal-Organic Framework Formation**.

Version v1.1.0 contains two explicitly separated workflows:

1. the synthetic-curated MFP-Score/OPR demonstration; and
2. a source-grounded descriptive evidence workflow that generates manuscript tables and projection-readiness outputs without invoking the scorer.

## Scope boundary

This is a software/resource and evidence package, not a production prediction model. It does not claim validated MFP-Score accuracy, F1/AUPRC/calibration performance, final SHAP attribution, experimental synthesis success, completed DFT/MD/TST/NEB calculations, autonomous-lab operation or industrial deployment.

The 49-record evidence registry is not a benchmark, gold set or training dataset. Source-grounded scoring is not admitted in this release.

## Run the synthetic-curated demonstration

```bash
python3 run_all.py
```

Expected result: `Validation status: PASS`.

## Run the source-grounded descriptive workflow

```bash
python3 source_grounded_evidence/run_evidence_tables.py
python3 source_grounded_evidence/scripts/registry_to_model_projection_adapter.py \
  source_grounded_evidence/data/AUTHORITATIVE_EVIDENCE_REGISTRY.csv \
  source_grounded_evidence/adapter_outputs
```

Expected hard-stop values:

```text
mfp_scores_generated = 0
opr_rankings_generated = 0
classifier_training_performed = false
synthetic_imputation_used = false
scoring_admitted_count = 0
```

## Main package components

- `data/`, `scripts/`, `outputs/`: synthetic-curated demonstration workflow.
- `source_grounded_evidence/data/`: authoritative evidence registry, descriptive summaries and neutral workbook.
- `source_grounded_evidence/schema/`: nullable registry and model-projection schemas.
- `source_grounded_evidence/scripts/`: descriptive table generator and no-scoring projection adapter.
- `source_grounded_evidence/outputs/`: generated descriptive tables and validation report.
- `source_grounded_evidence/adapter_outputs/`: projection candidates, blockers and adapter validation.
- `REVIEWER_QUICKSTART.md`: compact reproduction guide.
- `REPRODUCIBILITY.md`: detailed scope and validation notes.
- `RELEASE_STATUS.md`: stable v1.1.0 release boundaries.
- `LICENSE`: MIT License.

## Version and DOI information

- Previous archived version: v1.0.1, DOI `10.5281/zenodo.20452017`.
- Current version: v1.1.0.
- The v1.1.0 version DOI is assigned by Zenodo from the GitHub release. Consult the release-linked Zenodo record for the minted DOI.

Do not substitute the v1.0.1 DOI for the v1.1.0 DOI.

## Authors and funding

Authors: Jinnan Wei and Andrew E. H. Wheatley. Corresponding author: Andrew E. H. Wheatley (aehw2@cam.ac.uk). The work received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.
