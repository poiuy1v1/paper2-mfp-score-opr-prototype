#!/usr/bin/env python3
"""Generate hypothesis-generating Optimal Processing Routes (OPRs).

The OPRs are rule-based demonstration outputs. They are not experimentally
validated synthesis procedures.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List


def read_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def modulator_recommendation(row: Dict[str, str]) -> str:
    metal = row['metal_node'].lower()
    if 'zr' in metal:
        return 'formic acid or acetic acid screen, 1.5-3.0 M'
    if 'fe' in metal or 'cr' in metal:
        return 'acid-modulated aqueous screen, avoid over-fast crystallization'
    if 'cu' in metal:
        return 'low-acid or no-acid ethanol/water gel-aging screen'
    if 'zn' in metal:
        return 'composite/scaffold route recommended before pristine monolith claim'
    return 'modulator screen required'


def drying_recommendation(row: Dict[str, str], risk: str) -> str:
    if risk == 'high':
        return 'solvent exchange followed by supercritical CO2 or very slow low-surface-tension drying'
    if row['drying_route'] == 'supercritical_CO2':
        return 'retain supercritical CO2 drying as low-collapse-risk reference route'
    if row['drying_route'] in {'ethanol_exchange_slow_dry','solvent_exchange_slow_dry'}:
        return 'retain solvent exchange and slow drying; test drying-rate sensitivity'
    return 'replace fast/oven drying with ethanol exchange and slow drying'


def temperature_window(row: Dict[str, str]) -> str:
    t = float(row['temperature_c'])
    lo = max(25, round(t - 20))
    hi = round(t + 20)
    return f'{lo}-{hi} C screening window'


def make_opr_rows(candidates: List[Dict[str, str]], scores: List[Dict[str, str]]) -> List[Dict[str, str]]:
    by_id = {r['candidate_id']: r for r in scores}
    out = []
    for cand in candidates:
        s = by_id[cand['candidate_id']]
        risk = s['drying_risk_class']
        out.append({
            'candidate_id': cand['candidate_id'],
            'mfp_score_demo': s['mfp_score_demo'],
            'priority_class': s['priority_class'],
            'recommended_modulator_screen': modulator_recommendation(cand),
            'recommended_temperature_window': temperature_window(cand),
            'recommended_drying_route': drying_recommendation(cand, risk),
            'capillary_risk_flag': risk,
            'validation_first_step': 'small-vial gelation screen + solvent-exchange/drying control',
            'status': 'hypothesis-generating; not experimentally validated',
        })
    out.sort(key=lambda x: float(x['mfp_score_demo']), reverse=True)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate hypothesis-generating OPR table from demo MFP scores.')
    parser.add_argument('--candidates', default='data/candidate_powder_mofs.csv')
    parser.add_argument('--scores', default='outputs/mfp_scores.csv')
    parser.add_argument('--output', default='outputs/candidate_opr_table.csv')
    args = parser.parse_args()
    rows = make_opr_rows(read_csv(args.candidates), read_csv(args.scores))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    print(f'Wrote {args.output} ({len(rows)} rows)')


if __name__ == '__main__':
    main()
