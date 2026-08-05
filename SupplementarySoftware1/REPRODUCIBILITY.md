# Reproducibility notes for v1.1.0

## Commands

From `SupplementarySoftware1/`:

```bash
python3 run_all.py
python3 source_grounded_evidence/run_evidence_tables.py
python3 source_grounded_evidence/scripts/registry_to_model_projection_adapter.py \
  source_grounded_evidence/data/AUTHORITATIVE_EVIDENCE_REGISTRY.csv \
  source_grounded_evidence/adapter_outputs
```

## Reproduced outputs

The first command reproduces the synthetic-curated demonstration outputs and validation reports. The second reproduces descriptive source-coverage and condition-contrast tables. The third validates the authoritative registry and writes projection-readiness blockers without calling the scorer.

## Required hard stops

- `scoring_admitted_count = 0`
- `synthetic_imputation_count = 0`
- no source-grounded `mfp_scores.csv`
- no source-grounded `candidate_opr_table.csv`
- no classifier metrics

## Archive information

The previous v1.0.1 release is archived at DOI `10.5281/zenodo.20452017`. Version v1.1.0 adds the source-grounded evidence extension. Its version-specific DOI is assigned by Zenodo from the GitHub release and is available from the release-linked Zenodo record.
