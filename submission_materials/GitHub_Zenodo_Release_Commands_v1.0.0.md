# GitHub / Zenodo release commands for v1.0.0

This file is a mechanical release helper. Replace `USERNAME` and repository names before use.

## 1. Prepare local repository

```bash
mkdir paper2-monomof-mfp-opr-workflow
cd paper2-monomof-mfp-opr-workflow
cp -r /path/to/SupplementarySoftware1/* .
cp /path/to/LICENSE .
git init
git add .
git commit -m "Initial MIT-licensed supplementary software release v1.0.0"
git branch -M main
git remote add origin https://github.com/USERNAME/paper2-monomof-mfp-opr-workflow.git
git push -u origin main
```

## 2. Create versioned release

```bash
git tag -a v1.0.0 -m "v1.0.0 MIT-licensed supplementary software release"
git push origin v1.0.0
```

Then create a GitHub release from tag `v1.0.0` and connect/archive it with Zenodo.

## 3. Backfill DOI after Zenodo

Replace `[INSERT VERSIONED ZENODO DOI FOR FINAL RELEASE]` in the manuscript and submission materials with the version-specific Zenodo DOI. Do not invent a DOI before the Zenodo archive exists.
