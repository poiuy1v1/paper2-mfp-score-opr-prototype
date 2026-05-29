# Supplementary Software 1 v1.0.0 - Paper 2 MFP/OPR reproducibility workflow

This package supports the manuscript `paper2_v12_SoftwareReproducibilityAudit_QC`.
Release version: v1.0.0, initial MIT-licensed supplementary software release.
It provides a minimal, transparent, and reviewer-runnable workflow for a synthetic-curated demonstration of MFP-Score ranking and OPR route generation for monolithic MOF formation.

## Scope

This package is a **software/resource demonstration**, not a production model. It does not claim:

- validated MFP-Score accuracy;
- validated F1/AUPRC/SHAP performance;
- experimental synthesis success;
- completed DFT/MD/TST/NEB calculations;
- autonomous-lab deployment;
- industrial continuous-flow implementation.

## Reviewer quick-start

For the shortest referee-facing instructions, see `REVIEWER_QUICKSTART.md`.

## One-command reproduction

From this directory, run:

```bash
python3 run_all.py
```

This regenerates the core outputs and validates file consistency.

## Main inputs

- `data/seed_monomof_dataset.csv` - synthetic-curated seed records used for sanity-check diagnostics.
- `data/candidate_powder_mofs.csv` - synthetic-curated candidate powder MOFs used for demonstration ranking.
- `data/feature_dictionary.csv` - feature definitions and manuscript interpretation.
- `schemas/synthesis_extraction_schema.json` - schema for future literature extraction.

## Main scripts

- `scripts/mfp_score_baseline.py` - transparent expert-weighted logistic MFP-Score baseline.
- `scripts/capillary_stress_calculator.py` - Young-Laplace-style capillary pressure and drying-risk heuristic.
- `scripts/opr_optimizer.py` - hypothesis-generating OPR route generator.
- `scripts/candidate_ranking.py` - pipeline entry point for MFP scores, capillary risk, OPR table, and uncertainty report.
- `scripts/sensitivity_ablation.py` - lightweight ablation and sensitivity diagnostics.
- `validate_outputs.py` - output consistency, column, score-range, candidate-set, manifest, and checksum validator.
- `run_all.py` - one-command entry point.
- `REVIEWER_QUICKSTART.md` - minimal referee-facing rerun guide.
- `REPRODUCIBILITY_CHECKLIST.md` - checklist for final journal/package readiness.
- `LICENSE_NOTE.md` and `CITATION.cff` - final archive preparation files.

## Regenerated outputs

- `outputs/mfp_scores.csv`
- `outputs/candidate_opr_table.csv`
- `outputs/feature_importance.csv`
- `outputs/uncertainty_report.csv`
- `outputs/capillary_risk.csv`
- `outputs/calibration_summary.json`
- `outputs/ablation_summary.csv`
- `outputs/sensitivity_summary.csv`
- `outputs/software_resource_diagnostics.json`
- `outputs/outputs_manifest.json`
- `outputs/checksums.json`
- `outputs/output_validation_report.json`
- `outputs/output_validation_report.md`
- `outputs/run_all_summary.json`

## Recommended final-archive step

Before journal submission, archive the manuscript-aligned software release in a persistent repository that can mint a DOI, and update the Data and code availability statement with the permanent record.
