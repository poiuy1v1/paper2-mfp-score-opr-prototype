#!/usr/bin/env python3
"""Run the full Paper 2 v7 MFP/OPR demonstration pipeline."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print('+ ' + ' '.join(cmd))
    subprocess.run(cmd, check=True)


def uncertainty(score: float, risk: str) -> str:
    if score >= 0.75 and risk == 'low':
        return 'low'
    if score >= 0.55 and risk in {'low','medium'}:
        return 'medium'
    return 'high'


def main() -> None:
    parser = argparse.ArgumentParser(description='Regenerate demo MFP scores, capillary risk, OPR table, and uncertainty report.')
    parser.add_argument('--output-dir', default='outputs')
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(exist_ok=True)
    run([sys.executable, 'scripts/mfp_score_baseline.py', '--output-dir', str(out)])
    run([sys.executable, 'scripts/capillary_stress_calculator.py', '--output', str(out/'capillary_risk.csv')])
    run([sys.executable, 'scripts/opr_optimizer.py', '--scores', str(out/'mfp_scores.csv'), '--output', str(out/'candidate_opr_table.csv')])
    with open(out/'mfp_scores.csv', newline='', encoding='utf-8') as f:
        score_rows = list(csv.DictReader(f))
    rows = []
    for row in score_rows:
        score = float(row['mfp_score_demo'])
        risk = row['drying_risk_class']
        rows.append({
            'candidate_id': row['candidate_id'],
            'mfp_score_demo': row['mfp_score_demo'],
            'drying_risk_class': risk,
            'uncertainty_class': uncertainty(score, risk),
            'reason': 'synthetic feature values; requires curated literature extraction and experimental validation',
            'disabled_claims_until_validated': 'accuracy, SHAP percentages, final OPR, synthesis success',
        })
    with open(out/'uncertainty_report.csv','w',newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    summary = {'pipeline_scope':'synthetic-curated demonstration only', 'outputs': ['mfp_scores.csv','capillary_risk.csv','candidate_opr_table.csv','feature_importance.csv','calibration_summary.json','uncertainty_report.csv'], 'num_candidates': len(rows)}
    (out/'pipeline_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
