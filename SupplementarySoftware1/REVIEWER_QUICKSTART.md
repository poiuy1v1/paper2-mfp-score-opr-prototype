# Reviewer quick-start guide

This guide is intended for a referee or editor who wants to check that the manuscript-facing outputs can be regenerated from the Supplementary Software 1 package.

## Minimal reproduction command

From the `SupplementarySoftware1/` directory, run:

```bash
python3 run_all.py
```

This command regenerates the MFP-score table, OPR table, capillary-risk table, uncertainty report, ablation and sensitivity summaries, manifest, checksums, and validation report.

## Expected result

The expected validator status is:

```text
PASS
```

The validator writes:

- `outputs/output_validation_report.json`
- `outputs/output_validation_report.md`
- `outputs/outputs_manifest.json`
- `outputs/checksums.json`
- `outputs/run_all_summary.json`

## What this proves

The quick-start run checks file existence, required columns, score ranges, candidate-set consistency, JSON validity, output hashes, and manuscript-output traceability.

## What this does not prove

This run does not validate a production ML predictor, final SHAP feature attribution, experimental synthesis success, completed DFT/MD/TST/NEB calculations, or autonomous-laboratory operation.

## Suggested reviewer check

After running `python3 run_all.py`, open `outputs/output_validation_report.md`. If the status is `PASS` and no errors are reported, the package has reproduced the demonstration-level manuscript-facing outputs.
