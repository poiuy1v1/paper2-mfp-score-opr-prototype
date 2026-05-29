# Paper 2 Supplementary Software 1 v1.0.0: MFP-Score and OPR Workflow for monoMOF Discovery

This repository is the GitHub-ready v1.0.0 release folder for the Paper 2 supplementary software package.

It contains a reviewer-runnable Python workflow for a synthetic-curated demonstration of:

- MFP-Score candidate ranking;
- OPR route generation;
- capillary-risk heuristics;
- feature-diagnostic outputs;
- uncertainty reporting;
- checksum and validation reporting.

## Scope and boundaries

This software is a **minimal reproducible prototype**. It does **not** claim:

- validated MFP-Score accuracy;
- validated F1/AUPRC/SHAP model performance;
- experimental synthesis success;
- completed DFT/MD/TST/NEB calculations;
- autonomous-lab deployment;
- industrial continuous-flow implementation.

## Quick start

From the repository root:

```bash
cd SupplementarySoftware1
python3 run_all.py
python3 validate_outputs.py
```

Expected validation summary:

```text
Validation status: PASS
Errors: []
Warnings: []
```

## Repository structure

```text
paper2-github/
├── README.md
├── LICENSE
├── CITATION.cff
├── .zenodo.json
├── SupplementarySoftware1/
├── manuscript/
└── submission_materials/
```

## Main software folder

See [`SupplementarySoftware1/README.md`](SupplementarySoftware1/README.md) and [`SupplementarySoftware1/REVIEWER_QUICKSTART.md`](SupplementarySoftware1/REVIEWER_QUICKSTART.md).

## License

MIT License. See [`LICENSE`](LICENSE).

## Citation

Repository URL and DOI are placeholders until the GitHub/Zenodo release is created. After Zenodo generates the versioned DOI, update:

- `CITATION.cff`
- `.zenodo.json`
- `SupplementarySoftware1/CITATION.cff`
- `SupplementarySoftware1/zenodo_metadata_draft.json`
- manuscript Data/code availability statement

## Release workflow

1. Create a GitHub repository.
2. Upload this folder.
3. Create a GitHub release, recommended tag: `v1.0.0`.
4. Archive the release on Zenodo.
5. Use the **versioned DOI** in the manuscript.
