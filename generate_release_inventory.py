#!/usr/bin/env python3
"""Generate or verify v1.1.1 local-candidate indexes from exact Git blobs.

Stage all candidate payload changes first, run this script, stage its three
generated indexes, then run with --check. --tree REF selects a specific tree,
commit, or tag; without it the source is the current index (git write-tree).
Neither mode stages files, creates commits/tags, or accesses remotes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
INVENTORY = 'REPOSITORY_FILE_INVENTORY_v1.1.1.csv'
MANIFEST = 'REPOSITORY_MANIFEST_v1.1.1.md'
CHECKSUMS = 'SHA256SUMS_v1.1.1.txt'
INDEX_NAMES = frozenset({INVENTORY, MANIFEST, CHECKSUMS})


def git(*arguments: str) -> bytes:
    result = subprocess.run(
        ['git', '-C', str(ROOT), *arguments],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=30,
    )
    if result.returncode:
        raise ValueError(result.stderr.decode('utf-8', errors='replace').strip())
    return result.stdout


def resolve_tree(reference: str | None) -> str:
    if reference is None:
        return git('write-tree').decode('ascii').strip()
    return git(
        'rev-parse', '--verify', '--end-of-options', reference + '^{tree}',
    ).decode('ascii').strip()


def read_tree(tree: str) -> dict[str, bytes]:
    """Read all tracked regular blobs, including binaries and old indexes.

    Unsupported entries fail closed rather than silently reducing coverage.
    Text bytes are never normalized or read from the working tree.
    """
    files: dict[str, bytes] = {}
    casefold_names: set[str] = set()
    for entry in git('ls-tree', '-r', '-z', '--full-tree', tree).split(b'\0'):
        if not entry:
            continue
        metadata, raw_path = entry.split(b'\t', 1)
        mode, object_type, object_id = metadata.decode('ascii').split()
        path = raw_path.decode('utf-8')
        parts = path.split('/')
        if (
            not path or path.startswith('/') or '\\' in path
            or any(part in {'', '.', '..'} for part in parts)
            or any(ord(char) < 32 or ord(char) == 127 for char in path)
        ):
            raise ValueError(f'Unsupported checksum path: {path!r}')
        if path in files or path.casefold() in casefold_names:
            raise ValueError(f'Duplicate or case-colliding tree path: {path!r}')
        if object_type != 'blob' or mode not in {'100644', '100755'}:
            raise ValueError(f'Unsupported tree entry: {mode} {object_type} {path}')
        casefold_names.add(path.casefold())
        files[path] = git('cat-file', 'blob', object_id)
    if not files:
        raise ValueError('An empty tree cannot be a release candidate')
    return files


def category(path: str) -> str:
    if path in {
        'REPOSITORY_FILE_INVENTORY_v1.1.0.csv',
        'REPOSITORY_MANIFEST_v1.1.0.md', 'SHA256SUMS_v1.1.0.txt',
    }:
        return 'preserved historical v1.1.0 indexes'
    if path.startswith('SupplementarySoftware1/source_grounded_evidence/'):
        return 'source-grounded evidence'
    if path.startswith('SupplementarySoftware1/outputs/'):
        return 'demonstration outputs and validation reports'
    if path.startswith('SupplementarySoftware1/data/'):
        return 'legacy demonstration data'
    if path.startswith('SupplementarySoftware1/expected/'):
        return 'immutable expected output identity'
    if path.startswith('.github/') or path.endswith('.py'):
        return 'software and validation'
    if path.startswith('SupplementarySoftware1/'):
        return 'supplementary software documentation/configuration'
    if len(PurePosixPath(path).parts) == 1:
        return 'root release metadata/documentation'
    return 'repository documentation'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utf8_lf(text: str) -> bytes:
    if '\r' in text:
        raise ValueError('Non-canonical CR in generated index')
    return text.encode('utf-8')


def build_indexes(files: dict[str, bytes]) -> tuple[dict[str, bytes], int]:
    # Only the three new indexes are excluded here to avoid self-hashing.
    # Historical indexes are ordinary payload and never rewritten.
    payload = {name: data for name, data in files.items() if name not in INDEX_NAMES}
    rows = [
        {'path': name, 'category': category(name), 'bytes': len(payload[name]),
         'sha256': digest(payload[name])}
        for name in sorted(payload)
    ]
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(
        buffer, fieldnames=['path', 'category', 'bytes', 'sha256'],
        lineterminator='\n',
    )
    writer.writeheader()
    writer.writerows(rows)
    inventory_bytes = utf8_lf(buffer.getvalue())
    counts: dict[str, int] = {}
    for row in rows:
        counts[row['category']] = counts.get(row['category'], 0) + 1
    lines = [
        '# Repository manifest for the v1.1.1 local maintenance candidate', '',
        'This candidate corrects checksum and cross-platform serialization infrastructure.',
        'It is not a published release, a created tag, or publication authorization.', '',
        '## Exact byte basis and coverage', '',
        '- Every payload size and SHA-256 is read directly from the selected Git-tree blob.',
        '- No checkout newline conversion, untracked file, timestamp or host path enters the indexes.',
        '- Inventory and category counts exclude exactly these three current generated indexes:',
        *[f'  - {name}' for name in sorted(INDEX_NAMES)],
        '- The checksum index covers every tracked payload plus the exact canonical inventory and manifest bytes.',
        f'- The checksum index excludes only itself ({CHECKSUMS}), avoiding recursive self-hashing.',
        '- There are no directory, suffix or binary-file exclusions among tracked regular files.',
        '- Unsupported non-regular entries fail closed; they are never silently skipped.',
        '- The three v1.1.0 index files remain historical payload and are included without rewriting them.',
        '- A full candidate tree ID cannot be embedded here without circularity; verification binds the selected tree externally.', '',
        '## Reproduction and verification', '',
        '1. Stage the complete local candidate payload, including the generator and candidate release note.',
        '2. Run python generate_release_inventory.py to read the exact git write-tree result.',
        '3. Stage the three generated v1.1.1 indexes.',
        '4. Run python generate_release_inventory.py --check against the resulting staged tree.',
        '5. In a fresh checkout of the audited local candidate, run python generate_release_inventory.py --tree HEAD --check.',
        '6. Regenerate with --tree HEAD and require zero diff; retain the selected tree ID in external audit evidence.', '',
        '--check is read-only for working files. It requires all three generated indexes in the selected tree,',
        'compares their exact stored blob bytes with deterministic recomputation, verifies checksum coverage',
        'and every listed tree-blob digest, and checks the three working index files against those same bytes.',
        'Without --tree, Git may write the local index tree object; no source file is staged and no commit or tag is created.', '',
        '## Scientific and governance boundaries', '',
        '- MFP weights/intercept, Gaussian windows, drying-route score map, capillary equation/thresholds and OPR rules are unchanged.',
        '- Seed and candidate data, scores and rankings are unchanged; canonical bytes target the ten parent v1.1.0 Git blobs.',
        '- The MFP-Score/OPR workflow remains a synthetic-curated deterministic demonstration.',
        '- Source-grounded scoring, ranking, training and synthetic imputation remain disabled.',
        '- This infrastructure correction establishes no new model validation or experimental synthesis claim.',
        '- The v1.1.0 tag, commit history, manuscript v46.1, and human/scientific authority remain unchanged.',
        '- Independent IMPL-03-AUDIT-01 and separate authorization remain necessary before any GitHub write, tag or release.', '',
        '## File counts by category', '',
        *[f'- {key}: {counts[key]}' for key in sorted(counts)], '',
        f'Total indexed payload files: {len(rows)}',
        f'Total checksum records: {len(rows) + 2}',
        f'Total files in the complete candidate tree: {len(rows) + 3}', '',
    ]
    manifest_bytes = utf8_lf('\n'.join(lines))
    covered = {**payload, INVENTORY: inventory_bytes, MANIFEST: manifest_bytes}
    checksum_bytes = utf8_lf(''.join(
        f'{digest(covered[name])}  {name}\n' for name in sorted(covered)
    ))
    return {
        INVENTORY: inventory_bytes, MANIFEST: manifest_bytes,
        CHECKSUMS: checksum_bytes,
    }, len(rows)


def check_indexes(files: dict[str, bytes], expected: dict[str, bytes]) -> list[str]:
    failures = []
    for name, data in expected.items():
        if name not in files:
            failures.append(f'MISSING_TREE_INDEX: {name}')
        elif files[name] != data:
            failures.append(f'TREE_INDEX_BYTE_MISMATCH: {name}')
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            failures.append(f'MISSING_OR_UNSAFE_WORKING_INDEX: {name}')
        elif path.read_bytes() != data:
            failures.append(f'WORKING_INDEX_BYTE_MISMATCH: {name}')
    # Independently verify stored-index coverage and each actual tree blob.
    if CHECKSUMS in files:
        records = {}
        try:
            for line in files[CHECKSUMS].decode('utf-8').splitlines():
                sha, name = line.split('  ', 1)
                if name in records or len(sha) != 64 or any(c not in '0123456789abcdef' for c in sha):
                    raise ValueError('Duplicate path or invalid SHA-256')
                records[name] = sha
            if set(records) != set(files) - {CHECKSUMS}:
                failures.append('CHECKSUM_COVERAGE_MISMATCH')
            for name, sha in records.items():
                if name not in files or digest(files[name]) != sha:
                    failures.append(f'TREE_BLOB_CHECKSUM_MISMATCH: {name}')
        except (UnicodeError, ValueError) as exc:
            failures.append(f'INVALID_CHECKSUM_INDEX: {exc}')
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', help='Exact Git tree/commit/tag to read; default: git write-tree')
    parser.add_argument('--check', action='store_true', help='Verify stored tree and working indexes without rewriting them')
    args = parser.parse_args()
    try:
        tree = resolve_tree(args.tree)
        files = read_tree(tree)
        indexes, count = build_indexes(files)
        if args.check:
            failures = check_indexes(files, indexes)
            if failures:
                print(json.dumps({'status': 'FAIL', 'tree': tree, 'failures': failures}, indent=2))
                return 1
        else:
            for name in INDEX_NAMES:
                path = ROOT / name
                if path.is_symlink() or (path.exists() and not path.is_file()):
                    raise ValueError(f'Unsafe generated-index destination: {name}')
            for name, data in indexes.items():
                (ROOT / name).write_bytes(data)
        print(json.dumps({
            'status': 'PASS' if args.check else 'GENERATED_STAGE_INDEXES_BEFORE_CHECK',
            'tree': tree, 'inventory_records': count, 'checksum_records': count + 2,
            'tree_blob_basis': True, 'check_performed': args.check,
        }, indent=2))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({'status': 'FAIL', 'error': str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
