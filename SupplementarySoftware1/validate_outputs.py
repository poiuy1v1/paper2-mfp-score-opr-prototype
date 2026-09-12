#!/usr/bin/env python3
"""Validate Supplementary Software for the accompanying manuscript outputs.

The checks here support Digital Discovery / JCIM-style reproducibility: files must
exist, required columns must be present, row counts must match, scores must be
bounded, and exact bytes must match the frozen local maintenance-candidate identity.
Current-run diagnostics are descriptive; they never supply expected hashes.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / 'outputs'
EXPECTED = ROOT / 'expected' / 'release_output_identity_v1.1.1.json'

REQUIRED_OUTPUTS = {
    'mfp_scores.csv': ['candidate_id', 'mfp_score_demo', 'priority_class', 'drying_risk_class'],
    'capillary_risk.csv': ['candidate_id', 'capillary_pressure_mpa', 'drying_risk_class'],
    'candidate_opr_table.csv': ['candidate_id', 'mfp_score_demo', 'recommended_modulator_screen', 'recommended_drying_route'],
    'feature_importance.csv': ['feature', 'relative_importance_demo', 'interpretation'],
    'uncertainty_report.csv': ['candidate_id', 'uncertainty_class', 'disabled_claims_until_validated'],
    'ablation_summary.csv': ['scenario', 'top_candidate', 'mean_absolute_rank_shift_vs_baseline'],
    'sensitivity_summary.csv': ['scenario', 'top_candidate', 'high_priority_count'],
    'calibration_summary.json': [],
    'pipeline_summary.json': [],
    'software_resource_diagnostics.json': [],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(65536), b''):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def check_columns(rows: List[Dict[str, str]], required: List[str], filename: str) -> List[str]:
    errors = []
    if not rows:
        errors.append(f'{filename}: no rows')
        return errors
    cols = set(rows[0].keys())
    for col in required:
        if col not in cols:
            errors.append(f'{filename}: missing required column {col}')
    return errors


def unique_json_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f'duplicate JSON key: {key}')
        obj[key] = value
    return obj


def load_expected():
    """Read the versioned authority. No bootstrap or write path is permitted here."""
    raw = EXPECTED.read_bytes()
    if b'\r' in raw or raw.startswith(b'\xef\xbb\xbf'):
        raise ValueError('expected identity must be UTF-8 without BOM and LF only')
    obj = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_json_object)
    if not isinstance(obj, dict):
        raise ValueError('expected identity must be an object')
    if (obj.get('release') != 'v1.1.1'
            or obj.get('algorithm_change_from_v1.1.0') is not False
            or obj.get('canonical_encoding') != 'utf-8'
            or obj.get('canonical_eol') != 'LF'):
        raise ValueError('invalid expected release or serialization contract')
    outputs = obj.get('outputs')
    if not isinstance(outputs, dict) or set(outputs) != set(REQUIRED_OUTPUTS):
        raise ValueError('expected identity must contain exactly the ten required outputs')
    for filename, entry in outputs.items():
        if (not isinstance(entry, dict) or set(entry) != {'bytes', 'sha256'}
                or type(entry['bytes']) is not int or entry['bytes'] < 0
                or not isinstance(entry['sha256'], str)
                or re.fullmatch(r'[0-9a-f]{64}', entry['sha256']) is None):
            raise ValueError(f'invalid expected identity entry: {filename}')
    return outputs, hashlib.sha256(raw).hexdigest()


def main() -> int:
    errors: List[str] = []
    warnings: List[str] = []
    manifest = []
    csv_tables = {}
    expected = {}
    expected_sha256 = None
    try:
        expected, expected_sha256 = load_expected()
    except (OSError, ValueError, TypeError) as exc:
        errors.append(f'immutable expected identity unavailable or invalid: {exc}')

    for filename, required_cols in REQUIRED_OUTPUTS.items():
        path = OUTPUTS / filename
        if not path.exists():
            errors.append(f'missing output file: {filename}')
            continue
        entry = {'file': filename, 'bytes': path.stat().st_size, 'sha256': sha256(path)}
        if filename in expected:
            if entry['bytes'] != expected[filename]['bytes']:
                errors.append(f"{filename}: expected byte count {expected[filename]['bytes']}, got {entry['bytes']}")
            if entry['sha256'] != expected[filename]['sha256']:
                errors.append(f"{filename}: SHA-256 mismatch against immutable expected identity")
        if filename.endswith('.csv'):
            try:
                rows = read_csv(path)
                entry['rows'] = len(rows)
                csv_tables[filename] = rows
                errors.extend(check_columns(rows, required_cols, filename))
            except (OSError, UnicodeError, csv.Error) as exc:
                errors.append(f'{filename}: invalid CSV: {exc}')
        elif filename.endswith('.json'):
            try:
                obj = json.loads(path.read_text(encoding='utf-8'))
                entry['json_keys'] = sorted(obj.keys()) if isinstance(obj, dict) else []
            except Exception as exc:
                errors.append(f'{filename}: invalid JSON: {exc}')
        manifest.append(entry)

    if 'mfp_scores.csv' in csv_tables:
        for row in csv_tables['mfp_scores.csv']:
            try:
                score = float(row['mfp_score_demo'])
                if not (0.0 <= score <= 1.0):
                    errors.append(f"mfp_scores.csv: score out of range for {row.get('candidate_id')}: {score}")
            except Exception as exc:
                errors.append(f"mfp_scores.csv: invalid score for {row.get('candidate_id')}: {exc}")

    # Candidate set consistency checks across central outputs.
    central = ['mfp_scores.csv', 'candidate_opr_table.csv', 'uncertainty_report.csv', 'capillary_risk.csv']
    sets = {}
    for filename in central:
        if filename in csv_tables:
            sets[filename] = {r.get('candidate_id') for r in csv_tables[filename]}
    if sets:
        reference_name = 'mfp_scores.csv'
        reference = sets.get(reference_name, set())
        for filename, ids in sets.items():
            if ids != reference:
                errors.append(f'candidate set mismatch between {reference_name} and {filename}')

    # Ensure feature importance is not accidentally represented as SHAP.
    if 'feature_importance.csv' in csv_tables:
        text = ' '.join(' '.join(str(v) for v in row.values()) for row in csv_tables['feature_importance.csv']).lower()
        if 'shap' in text and 'not shap' not in text:
            warnings.append('feature_importance.csv mentions SHAP; confirm it remains a non-SHAP diagnostic')

    report = {
        'validation_scope': 'software/resource reproducibility checks only; not production model validation',
        'expected_identity': 'expected/release_output_identity_v1.1.1.json',
        'expected_identity_sha256': expected_sha256,
        'diagnostic_hash_authority': 'generated-current; not immutable expected authority',
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'warnings': warnings,
        'manifest': manifest,
        'disabled_claims': ['validated accuracy', 'final SHAP attribution', 'experimental synthesis success', 'completed DFT/MD workflow'],
    }
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    current_manifest = {'authority': 'generated-current', 'not_expected_authority': True, 'outputs': manifest}
    (OUTPUTS / 'outputs_manifest.json').write_bytes(json.dumps(current_manifest, indent=2).encode('utf-8'))
    checksums = {item['file']: item['sha256'] for item in manifest}
    current_checksums = {'authority': 'generated-current', 'not_expected_authority': True, 'outputs': checksums}
    (OUTPUTS / 'checksums.json').write_bytes(json.dumps(current_checksums, indent=2).encode('utf-8'))
    (OUTPUTS / 'output_validation_report.json').write_bytes(json.dumps(report, indent=2).encode('utf-8'))
    md = [
        '# Output validation report',
        '',
        f"Status: **{report['status']}**",
        '',
        'Scope: software/resource reproducibility checks only; this is not production model validation.',
        '',
        '## Errors',
    ]
    md.extend([f'- {e}' for e in errors] if errors else ['- None'])
    md.extend(['', '## Warnings'])
    md.extend([f'- {w}' for w in warnings] if warnings else ['- None'])
    md.extend(['', '## Files validated'])
    md.extend([f"- `{item['file']}` ({item.get('rows', 'JSON')} entries; sha256 `{item['sha256'][:12]}...`)" for item in manifest])
    (OUTPUTS / 'output_validation_report.md').write_bytes('\n'.join(md).encode('utf-8'))
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
