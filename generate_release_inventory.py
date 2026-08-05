#!/usr/bin/env python3
"""Generate the v1.1.0 public repository inventory, manifest and checksums."""
from __future__ import annotations
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INVENTORY = ROOT / 'REPOSITORY_FILE_INVENTORY_v1.1.0.csv'
MANIFEST = ROOT / 'REPOSITORY_MANIFEST_v1.1.0.md'
CHECKSUMS = ROOT / 'SHA256SUMS_v1.1.0.txt'
EXCLUDE_DIRS = {'.git', '__pycache__', '_release_input', '_release_work'}
EXCLUDE_FILES = {INVENTORY.name, MANIFEST.name, CHECKSUMS.name}
EXCLUDE_SUFFIXES = {'.pyc', '.pyo', '.tmp', '.zip'}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def public_files(include_indexes: bool = False):
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.suffix.lower() in EXCLUDE_SUFFIXES:
            continue
        if not include_indexes and rel.as_posix() in EXCLUDE_FILES:
            continue
        if rel.as_posix() == CHECKSUMS.name:
            continue
        yield path, rel


def category(rel: Path) -> str:
    p = rel.as_posix()
    if p.startswith('SupplementarySoftware1/source_grounded_evidence/'):
        return 'source-grounded evidence'
    if p.startswith('SupplementarySoftware1/outputs/'):
        return 'legacy generated outputs'
    if p.startswith('SupplementarySoftware1/data/'):
        return 'legacy demonstration data'
    if p.startswith('SupplementarySoftware1/scripts/') or p.endswith('.py'):
        return 'software and validation'
    if p.startswith('SupplementarySoftware1/'):
        return 'supplementary software documentation/configuration'
    if p in {'.zenodo.json', 'CITATION.cff', 'LICENSE', 'README.md', 'RELEASE_NOTES_v1.1.0.md'}:
        return 'root release metadata/documentation'
    return 'repository documentation'


rows=[]
for path, rel in public_files(False):
    rows.append({
        'path': rel.as_posix(),
        'category': category(rel),
        'bytes': path.stat().st_size,
        'sha256': sha256(path),
    })
with INVENTORY.open('w', newline='', encoding='utf-8') as fh:
    writer=csv.DictWriter(fh, fieldnames=['path','category','bytes','sha256'])
    writer.writeheader(); writer.writerows(rows)

counts={}
for row in rows:
    counts[row['category']] = counts.get(row['category'],0)+1
manifest=[
    '# Repository manifest for v1.1.0',
    '',
    'This manifest describes the public tagged source tree for the source-grounded evidence integration release.',
    '',
    '## Scientific boundaries',
    '',
    '- The legacy MFP-Score/OPR workflow is a synthetic-curated deterministic demonstration.',
    '- The 49-record source-grounded evidence registry is descriptive, human-verified and not a benchmark or training set.',
    '- Source-grounded MFP scoring, OPR ranking, classifier training and synthetic imputation remain disabled.',
    '',
    '## Archive hygiene',
    '',
    '- Obsolete v1.0.0/v18 assembly material, internal QC logs, stale package indexes and DOI placeholders are excluded.',
    '- Current inventory is stored in `REPOSITORY_FILE_INVENTORY_v1.1.0.csv`.',
    '- Current checksums are stored in `SHA256SUMS_v1.1.0.txt`.',
    '',
    '## File counts by category',
    '',
]
for key in sorted(counts):
    manifest.append(f'- {key}: {counts[key]}')
manifest += ['', f'Total indexed release files: {len(rows)}', '']
MANIFEST.write_text('\n'.join(manifest), encoding='utf-8')

checksum_lines=[]
for path, rel in public_files(True):
    checksum_lines.append(f'{sha256(path)}  {rel.as_posix()}')
CHECKSUMS.write_text('\n'.join(checksum_lines)+'\n', encoding='utf-8')
print(f'Inventory rows: {len(rows)}')
print(f'Checksummed files: {len(checksum_lines)}')
