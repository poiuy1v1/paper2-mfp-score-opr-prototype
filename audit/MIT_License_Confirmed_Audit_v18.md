# MIT License Confirmed Audit - v18

## Scope
This pass updates v17 after MIT License approval was confirmed. It does not modify the scientific model, software outputs, TOC artwork, or reference structure.

## Changes
- Converted license wording from draft/pending approval to confirmed MIT License.
- Preserved root `LICENSE` and `SupplementarySoftware1/LICENSE` files.
- Updated Data/code availability wording.
- Updated `CITATION.cff` and Zenodo metadata draft version to `v18-mit-license-confirmed-release-ready`.
- Added GitHub/Zenodo release command helper.
- Added DOI backfill checklist for the next step.

## Remaining external action
The only remaining external item is the real GitHub/Zenodo release DOI. The DOI placeholder must not be replaced until Zenodo generates the versioned DOI.

## Validation

- `pdflatex` compile: PASS.
- `python3 run_all.py`: PASS.
- `python3 validate_outputs.py`: PASS; errors: []; warnings: [].
- PDF pages: 32.
- PDF word-count delta relative to v17: -7 words.
