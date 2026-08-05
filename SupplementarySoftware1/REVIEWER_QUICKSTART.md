# Reviewer quick-start

Run from `SupplementarySoftware1/`.

## 1. Synthetic-curated demonstration

```bash
python3 run_all.py
```

Expected: `Validation status: PASS`, `Errors: []`, `Warnings: []`.

## 2. Source-grounded descriptive tables

```bash
python3 source_grounded_evidence/run_evidence_tables.py
```

Expected validation file:

```text
source_grounded_evidence/outputs/table_generator_validation.json
```

It must report 49 registry rows, nine primary sources, zero MFP scores, zero OPR rankings, no classifier training and no synthetic imputation.

## 3. Projection-readiness adapter

```bash
python3 source_grounded_evidence/scripts/registry_to_model_projection_adapter.py \
  source_grounded_evidence/data/AUTHORITATIVE_EVIDENCE_REGISTRY.csv \
  source_grounded_evidence/adapter_outputs
```

Expected:

```text
status: PASS
scoring_admitted_count: 0
synthetic_imputation_count: 0
derived_field_request_count: 0
```

These checks establish package reproducibility and the no-scoring boundary. They do not validate experimental synthesis, production ML performance, completed DFT/MD or autonomous-laboratory operation.
