# Supplementary Software 1 - Software resource summary

This package supports the manuscript as a Digital Discovery-oriented software resource. Its purpose is to make the MFP-Score and OPR-ranking workflow transparent, inspectable, and re-runnable from supplied demonstration data.

## Core commands

```bash
python run_all.py
python validate_outputs.py
```

## Outputs linked to the manuscript

- `outputs/mfp_scores.csv` -> candidate MFP-Score ranking and Table 1.
- `outputs/candidate_opr_table.csv` -> OPR summary and Table 2.
- `outputs/feature_importance.csv` -> weight-based feature diagnostic, not SHAP.
- `outputs/uncertainty_report.csv` -> uncertainty classes and disabled-claim boundaries.
- `outputs/ablation_summary.csv` and `outputs/sensitivity_summary.csv` -> sanity-check diagnostics.
- `outputs/outputs_manifest.json` and `outputs/checksums.json` -> output traceability.
- `outputs/output_validation_report.json` -> validation status.

## Boundary

The package is a demonstration-level software resource. It is not a validated production model, not a real DFT/MD workflow, not an autonomous-lab system, and not experimental proof of any synthesis route.
