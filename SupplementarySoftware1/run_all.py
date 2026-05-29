#!/usr/bin/env python3
"""One-command reproducibility entry point for Paper 2 Supplementary Software 1."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(args):
    print('+ ' + ' '.join(str(a) for a in args))
    subprocess.run([str(a) for a in args], cwd=ROOT, check=True)


def main() -> None:
    outputs = ROOT / 'outputs'
    outputs.mkdir(exist_ok=True)
    run([sys.executable, 'scripts/candidate_ranking.py', '--output-dir', 'outputs'])
    run([sys.executable, 'scripts/sensitivity_ablation.py', '--output-dir', 'outputs'])
    run([sys.executable, 'validate_outputs.py'])
    summary = {
        'entry_point': 'run_all.py',
        'scope': 'regenerates demonstration-level outputs and validates file consistency',
        'primary_outputs': [
            'mfp_scores.csv',
            'candidate_opr_table.csv',
            'feature_importance.csv',
            'uncertainty_report.csv',
            'ablation_summary.csv',
            'sensitivity_summary.csv',
            'outputs_manifest.json',
            'checksums.json',
            'output_validation_report.json',
        ],
    }
    (outputs / 'run_all_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
