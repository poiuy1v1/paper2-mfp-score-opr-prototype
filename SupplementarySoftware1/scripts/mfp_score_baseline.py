#!/usr/bin/env python3
"""Baseline MFP-Score prototype for Paper 2 v7.

The MFP-Score here is a transparent expert-weighted logistic scoring function
implemented on synthetic-curated demonstration data. It is intended to make the
manuscript interface reproducible, not to claim a validated production ML model.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Tuple

try:
    from capillary_stress_calculator import capillary_pressure_mpa, risk_class
except ImportError:
    from scripts.capillary_stress_calculator import capillary_pressure_mpa, risk_class

WEIGHTS = {
    'modulator_window': 1.00,
    'precursor_window': 1.10,
    'temperature_window': 0.75,
    'drying_route_score': 1.35,
    'capillary_safety': 1.15,
    'pore_radius_score': 0.60,
    'framework_stability_z': 1.20,
}
INTERCEPT = -3.00
DRYING_ROUTE_SCORE = {
    'supercritical_CO2': 1.00,
    'ethanol_exchange_slow_dry': 0.86,
    'solvent_exchange_slow_dry': 0.82,
    'ambient_slow_dry': 0.66,
    'freeze_dry': 0.58,
    'ambient_fast_dry': 0.30,
    'oven_dry': 0.22,
    'unknown': 0.35,
}


def logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def gaussian_window(value: float, center: float, width: float) -> float:
    return math.exp(-0.5 * ((value - center) / width) ** 2)


def features(row: Dict[str, str]) -> Dict[str, float]:
    modconc = float(row['modulator_concentration_m'])
    precursor = float(row['precursor_concentration_m'])
    temp = float(row['temperature_c'])
    pore_radius = float(row['pore_radius_nm'])
    stability = float(row['framework_stability_z'])
    pc = capillary_pressure_mpa(row['surface_tension_mN_m'], row['contact_angle_deg'], row['pore_radius_nm'])
    return {
        'modulator_window': gaussian_window(modconc, 2.0, 1.1),
        'precursor_window': gaussian_window(precursor, 0.10, 0.055),
        'temperature_window': gaussian_window(temp, 100.0, 45.0),
        'drying_route_score': DRYING_ROUTE_SCORE.get(row.get('drying_route', 'unknown'), 0.35),
        'capillary_safety': max(0.0, min(1.0, 1.0 - pc / 12.0)),
        'pore_radius_score': max(0.0, min(1.0, pore_radius / 30.0)),
        'framework_stability_z': max(0.0, min(1.0, stability)),
    }


def score_row(row: Dict[str, str]) -> Tuple[float, Dict[str, float]]:
    feat = features(row)
    logit = INTERCEPT + sum(WEIGHTS[k] * feat[k] for k in WEIGHTS)
    return logistic(logit), feat


def load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def evaluate_seed(seed_rows: List[Dict[str, str]], threshold: float = 0.50) -> Dict[str, float]:
    y_true = [int(r['label_monolith']) for r in seed_rows]
    y_prob = [score_row(r)[0] for r in seed_rows]
    y_pred = [1 if p >= threshold else 0 for p in y_prob]
    tp = sum(1 for y,p in zip(y_true,y_pred) if y == 1 and p == 1)
    tn = sum(1 for y,p in zip(y_true,y_pred) if y == 0 and p == 0)
    fp = sum(1 for y,p in zip(y_true,y_pred) if y == 0 and p == 1)
    fn = sum(1 for y,p in zip(y_true,y_pred) if y == 1 and p == 0)
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(1e-12, precision + recall)
    balanced_accuracy = 0.5 * (tp / max(1, tp + fn) + tn / max(1, tn + fp))
    brier = mean((p - y) ** 2 for p,y in zip(y_prob,y_true))
    return {
        'scope': 'synthetic-curated demonstration only; not a validated production model',
        'threshold': threshold,
        'n_seed_records': len(seed_rows),
        'positive_records': sum(y_true),
        'negative_records': len(y_true) - sum(y_true),
        'precision_demo': round(precision, 3),
        'recall_demo': round(recall, 3),
        'f1_demo': round(f1, 3),
        'balanced_accuracy_demo': round(balanced_accuracy, 3),
        'brier_demo': round(brier, 3),
        'warning': 'These metrics are diagnostics on a synthetic-curated toy set and must not be reported as validated model performance.',
    }


def write_dict_csv(rows: List[Dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description='Compute demonstration MFP-Scores for synthetic-curated monoMOF candidates.')
    parser.add_argument('--seed', default='data/seed_monomof_dataset.csv')
    parser.add_argument('--candidates', default='data/candidate_powder_mofs.csv')
    parser.add_argument('--output-dir', default='outputs')
    args = parser.parse_args()
    seed = load_csv(args.seed)
    cand = load_csv(args.candidates)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in cand:
        score, feat = score_row(r)
        pc = capillary_pressure_mpa(r['surface_tension_mN_m'], r['contact_angle_deg'], r['pore_radius_nm'])
        rows.append({
            'candidate_id': r['candidate_id'],
            'metal_node': r['metal_node'],
            'linker_family': r['linker_family'],
            'topology': r['topology'],
            'mfp_score_demo': f'{score:.3f}',
            'priority_class': 'high' if score >= 0.70 else 'medium' if score >= 0.45 else 'low',
            'capillary_pressure_mpa': f'{pc:.3f}',
            'drying_risk_class': risk_class(pc),
            'drying_route': r['drying_route'],
            'framework_stability_z': r['framework_stability_z'],
            **{f'feature_{k}': f'{v:.3f}' for k,v in feat.items()},
        })
    rows.sort(key=lambda x: float(x['mfp_score_demo']), reverse=True)
    write_dict_csv(rows, output_dir/'mfp_scores.csv')
    fi = []
    total = sum(abs(v) for v in WEIGHTS.values())
    for k,v in sorted(WEIGHTS.items(), key=lambda kv: abs(kv[1]), reverse=True):
        fi.append({'feature': k, 'absolute_weight': v, 'relative_importance_demo': round(abs(v)/total, 3), 'interpretation': 'expert-weighted prototype diagnostic, not SHAP'})
    write_dict_csv(fi, output_dir/'feature_importance.csv')
    summary = evaluate_seed(seed)
    (output_dir/'calibration_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
