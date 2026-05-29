# Reproducibility notes

## Minimal tested command

See also `REVIEWER_QUICKSTART.md` for a compact referee-facing version of these instructions.

```bash
python3 run_all.py
```

The command executes:

1. `scripts/candidate_ranking.py`
2. `scripts/sensitivity_ablation.py`
3. `validate_outputs.py`

The validator writes `outputs/output_validation_report.json`, `outputs/outputs_manifest.json`, and `outputs/checksums.json`.

## Environment

The core scripts use only the Python standard library. Optional notebook inspection or plotting can use the dependencies listed in `requirements.txt` or `environment.yml`.

## Expected validation status

The expected validation status is:

```text
PASS
```

A failed validation means at least one of the following occurred:

- an output file is missing;
- an expected column is absent;
- MFP scores are outside the [0, 1] range;
- candidate sets differ across central output files;
- JSON output is invalid.

## What is reproducible here

The package reproduces the manuscript-facing demonstration workflow:

```text
synthetic-curated input tables -> MFP scores -> capillary risk -> OPR table -> uncertainty report -> ablation/sensitivity diagnostics -> validation manifests
```

## What is not claimed

This package does not reproduce a validated production predictor, experimental synthesis results, DFT/MD outputs, or autonomous laboratory control logs. It is a transparent software/resource baseline for reviewer inspection and future curated-data expansion.


## Final archive preparation

Before formal journal submission, archive the exact software release in a persistent repository, add the final repository DOI to the manuscript Data and code availability statement, and keep the confirmed MIT License files in the archived release.
