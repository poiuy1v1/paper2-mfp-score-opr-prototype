#!/usr/bin/env python3
"""Young-Laplace style capillary stress calculator for the Paper 2 v7 prototype.

This is a heuristic drying-risk layer for synthetic monoMOF candidate ranking. It is
not a molecular simulation, DFT calculation, MD workflow, or experimentally
validated mechanical model.
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, Iterable, List


def capillary_pressure_mpa(surface_tension_mN_m: float, contact_angle_deg: float, pore_radius_nm: float) -> float:
    """Return Young-Laplace capillary pressure in MPa: Pc = 2 gamma cos(theta) / r.

    surface_tension_mN_m is converted to N/m; pore_radius_nm is converted to m.
    Negative cos(theta) values are clipped to zero because non-wetting cases are
    outside this simple collapse-risk heuristic.
    """
    gamma = float(surface_tension_mN_m) * 1e-3
    r = max(float(pore_radius_nm) * 1e-9, 1e-12)
    cos_theta = max(0.0, math.cos(math.radians(float(contact_angle_deg))))
    return (2.0 * gamma * cos_theta / r) / 1e6


def risk_class(pc_mpa: float) -> str:
    if pc_mpa >= 8.0:
        return "high"
    if pc_mpa >= 3.0:
        return "medium"
    return "low"


def calculate_rows(rows: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    out = []
    for row in rows:
        pc = capillary_pressure_mpa(row['surface_tension_mN_m'], row['contact_angle_deg'], row['pore_radius_nm'])
        out.append({
            'candidate_id': row.get('candidate_id', row.get('record_id', 'unknown')),
            'pore_radius_nm': row['pore_radius_nm'],
            'surface_tension_mN_m': row['surface_tension_mN_m'],
            'contact_angle_deg': row['contact_angle_deg'],
            'capillary_pressure_mpa': f'{pc:.3f}',
            'drying_risk_class': risk_class(pc),
        })
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description='Calculate heuristic capillary drying risk for monoMOF candidates.')
    parser.add_argument('--input', default='data/candidate_powder_mofs.csv')
    parser.add_argument('--output', default='outputs/capillary_risk.csv')
    args = parser.parse_args()
    with open(args.input, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    out = calculate_rows(rows)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        writer.writeheader(); writer.writerows(out)
    print(f'Wrote {args.output} ({len(out)} rows)')


if __name__ == '__main__':
    main()
