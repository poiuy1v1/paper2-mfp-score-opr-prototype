#!/usr/bin/env python3
"""Generate lightweight ablation and sensitivity diagnostics for the Paper 2 prototype.

These diagnostics are intended for software/resource validation. They are not SHAP,
not a validated production model, and not evidence of experimental synthesis success.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

import mfp_score_baseline as mfp  # noqa: E402
from capillary_stress_calculator import capillary_pressure_mpa, risk_class  # noqa: E402


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write_csv(rows: List[Dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)


def score_with_weights(row: Dict[str, str], weights: Dict[str, float], intercept: float = mfp.INTERCEPT) -> Tuple[float, Dict[str, float]]:
    feat = mfp.features(row)
    logit = intercept + sum(weights[k] * feat[k] for k in weights)
    return mfp.logistic(logit), feat


def ranking_for(candidates: List[Dict[str, str]], weights: Dict[str, float], intercept: float = mfp.INTERCEPT) -> List[Dict[str, object]]:
    rows = []
    for r in candidates:
        score, _ = score_with_weights(r, weights, intercept=intercept)
        pc = capillary_pressure_mpa(r['surface_tension_mN_m'], r['contact_angle_deg'], r['pore_radius_nm'])
        rows.append({
            'candidate_id': r['candidate_id'],
            'mfp_score_demo': score,
            'drying_risk_class': risk_class(pc),
        })
    rows.sort(key=lambda x: float(x['mfp_score_demo']), reverse=True)
    for i, row in enumerate(rows, 1):
        row['rank'] = i
    return rows


def rank_shift(base: List[Dict[str, object]], alt: List[Dict[str, object]]) -> float:
    b = {r['candidate_id']: int(r['rank']) for r in base}
    a = {r['candidate_id']: int(r['rank']) for r in alt}
    return sum(abs(b[k] - a[k]) for k in b) / max(1, len(b))


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate ablation and sensitivity diagnostics for the MFP prototype.')
    parser.add_argument('--candidates', default='data/candidate_powder_mofs.csv')
    parser.add_argument('--output-dir', default='outputs')
    args = parser.parse_args()

    out = Path(args.output_dir)
    candidates = load_csv(Path(args.candidates))
    base_weights = dict(mfp.WEIGHTS)
    base_rank = ranking_for(candidates, base_weights)

    ablation_scenarios = {
        'baseline_all_features': base_weights,
        'remove_drying_route_score': {**base_weights, 'drying_route_score': 0.0},
        'remove_capillary_safety': {**base_weights, 'capillary_safety': 0.0},
        'remove_framework_stability_z': {**base_weights, 'framework_stability_z': 0.0},
        'remove_process_window_features': {**base_weights, 'modulator_window': 0.0, 'precursor_window': 0.0, 'temperature_window': 0.0},
    }
    ablation_rows = []
    for name, weights in ablation_scenarios.items():
        ranked = ranking_for(candidates, weights)
        ablation_rows.append({
            'scenario': name,
            'top_candidate': ranked[0]['candidate_id'],
            'top_score_demo': f"{float(ranked[0]['mfp_score_demo']):.3f}",
            'mean_absolute_rank_shift_vs_baseline': f"{rank_shift(base_rank, ranked):.3f}",
            'interpretation': 'lightweight ablation for software sanity checking; not a validated mechanistic attribution',
        })
    write_csv(ablation_rows, out / 'ablation_summary.csv')

    sensitivity_scenarios = [
        ('baseline_intercept', 0.0),
        ('more_conservative_intercept_minus_0p5', -0.5),
        ('more_permissive_intercept_plus_0p5', 0.5),
    ]
    sensitivity_rows = []
    for name, delta in sensitivity_scenarios:
        ranked = ranking_for(candidates, base_weights, intercept=mfp.INTERCEPT + delta)
        high_count = sum(1 for r in ranked if float(r['mfp_score_demo']) >= 0.70)
        medium_count = sum(1 for r in ranked if 0.45 <= float(r['mfp_score_demo']) < 0.70)
        low_count = len(ranked) - high_count - medium_count
        sensitivity_rows.append({
            'scenario': name,
            'top_candidate': ranked[0]['candidate_id'],
            'top_score_demo': f"{float(ranked[0]['mfp_score_demo']):.3f}",
            'high_priority_count': high_count,
            'medium_priority_count': medium_count,
            'low_priority_count': low_count,
            'interpretation': 'threshold and intercept sensitivity for prototype sanity checking only',
        })
    write_csv(sensitivity_rows, out / 'sensitivity_summary.csv')

    summary = {
        'scope': 'software/resource validation diagnostics only',
        'ablation_scenarios': list(ablation_scenarios.keys()),
        'sensitivity_scenarios': [x[0] for x in sensitivity_scenarios],
        'disabled_claims': ['validated feature attribution', 'SHAP percentages', 'experimental success', 'production predictor accuracy'],
    }
    (out / 'software_resource_diagnostics.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
