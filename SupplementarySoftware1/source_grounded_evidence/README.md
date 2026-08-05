# Source-grounded evidence table workflow

This directory contains the condition-level evidence registry and a descriptive table generator used for the manuscript evidence section.

## Run

```bash
python run_evidence_tables.py
```

## Boundaries

The generator performs descriptive aggregation only. It does not generate MFP scores, OPR rankings, classifier predictions, accuracy/F1/AUPRC/calibration metrics, or synthetic imputations. The registry is not a benchmark, gold set, or training dataset.

## Inputs

- `data/AUTHORITATIVE_EVIDENCE_REGISTRY.csv`
- `data/DESCRIPTIVE_SOURCE_SUMMARY.csv`
- additional descriptive CSV files under `data/`

## Outputs

- `outputs/source_coverage_table.tex`
- `outputs/condition_contrasts_table.tex`
- `outputs/manuscript_registry_summary.csv`
- `outputs/selected_condition_contrasts.csv`
- `outputs/table_generator_validation.json`
