# ZIP readme for reviewers (v1.0.0)

This ZIP is not empty. It contains the manuscript, the reviewer-runnable Supplementary Software 1 package, repository/DOI/license materials, and TOC/graphical abstract files.

## Start here

1. Read the manuscript PDF in `manuscript/`.
2. Review `PACKAGE_CONTENTS.md` and `MANIFEST_FOR_REVIEWERS.md`.
3. To rerun the software:
   ```bash
   cd SupplementarySoftware1
   python3 run_all.py
   python3 validate_outputs.py
   ```
4. Check `SupplementarySoftware1/outputs/output_validation_report.md`.
5. Review repository/license/DOI materials in `submission_materials/`.

## Current external placeholders

- Repository DOI: `[INSERT VERSIONED ZENODO DOI FOR FINAL RELEASE]`
- License: MIT License selected and confirmed for public software deposition.

## Scientific boundary

The software outputs are demonstration-level and hypothesis-generating. They are not experimentally validated predictions, a production ML model, a completed DFT/MD workflow, or an autonomous-lab implementation.
