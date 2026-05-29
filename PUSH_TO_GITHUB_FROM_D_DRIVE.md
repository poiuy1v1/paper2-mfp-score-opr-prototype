# Push this folder from D drive to GitHub

Assume you unzip this package to:

```text
D:\paper2-github
```

Open PowerShell or Git Bash and run:

```bash
cd /d/paper2-github
```

For PowerShell, use:

```powershell
cd D:\paper2-github
```

Run the software check first:

```bash
cd SupplementarySoftware1
python3 run_all.py
python3 validate_outputs.py
cd ..
```

Then initialise Git and push:

```bash
git init
git branch -M main
git add .
git commit -m "Initial MIT-licensed supplementary software release"
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/paper2-mfp-score-opr-prototype.git
git push -u origin main
```

Create a GitHub release:

```text
Tag: v1.0.0
Title: v1.0.0 - MIT-licensed supplementary software release
```

Then connect GitHub to Zenodo and archive the release. Use the **versioned DOI**, not only the concept DOI, for the manuscript.
