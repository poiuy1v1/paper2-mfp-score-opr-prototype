# GitHub -> Zenodo release checklist (v1.0.0)

1. Create a clean GitHub repository, for example `paper2-monomof-mfp-opr-workflow`.
2. Copy the release-ready files from `SupplementarySoftware1/` plus manuscript-facing package-visibility files.
3. Confirm the software license with the author, supervisor, and any institutional policy. The v1.0.0 package is the initial MIT-licensed supplementary software release.
4. Confirm `README.md`, `REVIEWER_QUICKSTART.md`, `REPRODUCIBILITY.md`, `REPRODUCIBILITY_CHECKLIST.md`, `environment.yml`, `requirements.txt`, `CITATION.cff`, and `zenodo_metadata_draft.json` are present.
5. Rerun:
   ```bash
   cd SupplementarySoftware1
   python3 run_all.py
   python3 validate_outputs.py
   ```
6. Commit and tag the release, e.g. `v1.0.0`.
7. Connect GitHub to Zenodo and archive the release.
8. Copy the versioned Zenodo DOI into:
   - manuscript Data/code availability section;
   - `CITATION.cff`;
   - `README.md`;
   - cover letter;
   - submission portal metadata.
9. Rebuild the manuscript PDF after DOI insertion.
10. Upload the final manuscript, software archive, cover letter, and TOC/graphical abstract files to the RSC submission portal.
