# Repository manifest for the v1.1.1 local maintenance candidate

This candidate corrects checksum and cross-platform serialization infrastructure.
It is not a published release, a created tag, or publication authorization.

## Exact byte basis and coverage

- Every payload size and SHA-256 is read directly from the selected Git-tree blob.
- No checkout newline conversion, untracked file, timestamp or host path enters the indexes.
- Inventory and category counts exclude exactly these three current generated indexes:
  - REPOSITORY_FILE_INVENTORY_v1.1.1.csv
  - REPOSITORY_MANIFEST_v1.1.1.md
  - SHA256SUMS_v1.1.1.txt
- The checksum index covers every tracked payload plus the exact canonical inventory and manifest bytes.
- The checksum index excludes only itself (SHA256SUMS_v1.1.1.txt), avoiding recursive self-hashing.
- There are no directory, suffix or binary-file exclusions among tracked regular files.
- Unsupported non-regular entries fail closed; they are never silently skipped.
- The three v1.1.0 index files remain historical payload and are included without rewriting them.
- A full candidate tree ID cannot be embedded here without circularity; verification binds the selected tree externally.

## Reproduction and verification

1. Stage the complete local candidate payload, including the generator and candidate release note.
2. Run python generate_release_inventory.py to read the exact git write-tree result.
3. Stage the three generated v1.1.1 indexes.
4. Run python generate_release_inventory.py --check against the resulting staged tree.
5. In a fresh checkout of the audited local candidate, run python generate_release_inventory.py --tree HEAD --check.
6. Regenerate with --tree HEAD and require zero diff; retain the selected tree ID in external audit evidence.

--check is read-only for working files. It requires all three generated indexes in the selected tree,
compares their exact stored blob bytes with deterministic recomputation, verifies checksum coverage
and every listed tree-blob digest, and checks the three working index files against those same bytes.
Without --tree, Git may write the local index tree object; no source file is staged and no commit or tag is created.

## Scientific and governance boundaries

- MFP weights/intercept, Gaussian windows, drying-route score map, capillary equation/thresholds and OPR rules are unchanged.
- Seed and candidate data, scores and rankings are unchanged; canonical bytes target the ten parent v1.1.0 Git blobs.
- The MFP-Score/OPR workflow remains a synthetic-curated deterministic demonstration.
- Source-grounded scoring, ranking, training and synthetic imputation remain disabled.
- This infrastructure correction establishes no new model validation or experimental synthesis claim.
- The v1.1.0 tag, commit history, manuscript v46.1, and human/scientific authority remain unchanged.
- Independent IMPL-03-AUDIT-01 and separate authorization remain necessary before any GitHub write, tag or release.

## File counts by category

- demonstration outputs and validation reports: 15
- immutable expected output identity: 1
- legacy demonstration data: 3
- preserved historical v1.1.0 indexes: 3
- root release metadata/documentation: 9
- software and validation: 10
- source-grounded evidence: 26
- supplementary software documentation/configuration: 14

Total indexed payload files: 81
Total checksum records: 83
Total files in the complete candidate tree: 84
