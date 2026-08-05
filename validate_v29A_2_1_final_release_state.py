#!/usr/bin/env python3
"""Validate v1.1.0 release state, scientific locks and full-tree archive hygiene."""
from __future__ import annotations
import csv
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SW=ROOT/'SupplementarySoftware1'
EVID=SW/'source_grounded_evidence'
errors=[]
warnings=[]
retained_hits=[]


def require(rel: str):
    p=ROOT/rel
    if not p.exists(): errors.append(f'missing:{rel}')

required=[
 'README.md','LICENSE','CITATION.cff','.zenodo.json','RELEASE_NOTES_v1.1.0.md',
 'SupplementarySoftware1/README.md','SupplementarySoftware1/RELEASE_STATUS.md',
 'SupplementarySoftware1/REPRODUCIBILITY.md','SupplementarySoftware1/REPRODUCIBILITY_CHECKLIST.md',
 'SupplementarySoftware1/SOFTWARE_RESOURCE_SUMMARY.md','SupplementarySoftware1/run_all.py',
 'SupplementarySoftware1/validate_outputs.py',
 'SupplementarySoftware1/source_grounded_evidence/data/AUTHORITATIVE_EVIDENCE_REGISTRY.csv',
 'SupplementarySoftware1/source_grounded_evidence/data/HUMAN_VERIFICATION_CHANGELOG.csv',
 'SupplementarySoftware1/source_grounded_evidence/data/Source_Grounded_Evidence_Workbook.xlsx',
 'SupplementarySoftware1/source_grounded_evidence/docs/AUTHOR_ATTESTATION_RECORD.md',
 'SupplementarySoftware1/source_grounded_evidence/docs/LITERATURE_RETRIEVAL_SCREENING_AND_VERIFICATION.md',
 'SupplementarySoftware1/source_grounded_evidence/data/CANDIDATE_EVIDENCE_CLASSIFICATION.csv',
 'generate_release_inventory.py',
]
for rel in required: require(rel)

# Stable release wording.
release_texts=[
 'README.md','RELEASE_NOTES_v1.1.0.md','SupplementarySoftware1/README.md',
 'SupplementarySoftware1/RELEASE_STATUS.md','SupplementarySoftware1/REPRODUCIBILITY.md',
 'SupplementarySoftware1/REPRODUCIBILITY_CHECKLIST.md','SupplementarySoftware1/SOFTWARE_RESOURCE_SUMMARY.md',
]
for rel in release_texts:
    p=ROOT/rel
    if not p.exists(): continue
    t=p.read_text(encoding='utf-8')
    for forbidden in ['release candidate','READY FOR CODEX','not executed','GitHub tag/release: not created','Zenodo DOI: not minted']:
        if forbidden.lower() in t.lower(): errors.append(f'stale_release_state:{rel}:{forbidden}')

# Metadata.
for rel in ['.zenodo.json','SupplementarySoftware1/zenodo_metadata.json']:
    p=ROOT/rel
    if not p.exists(): continue
    try: obj=json.loads(p.read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'invalid_json:{rel}:{exc}'); continue
    if obj.get('version') not in {'v1.1.0','1.1.0'}: errors.append(f'wrong_version:{rel}')
    if 'doi' in obj: errors.append(f'prefilled_version_doi:{rel}')
    if 'publication_date' in obj: errors.append(f'prefilled_publication_date:{rel}')
    names=[c.get('name') for c in obj.get('creators',[])]
    if names != ['Wei, Jinnan','Wheatley, Andrew E. H.']: errors.append(f'creator_order:{rel}')
    if 'release candidate' in str(obj.get('notes','')).lower(): errors.append(f'stale_metadata_note:{rel}')

for rel in ['CITATION.cff','SupplementarySoftware1/CITATION.cff']:
    p=ROOT/rel
    if not p.exists(): continue
    t=p.read_text(encoding='utf-8')
    if not re.search(r'^version:\s*["\']?v?1\.1\.0["\']?\s*$',t,re.M): errors.append(f'wrong_cff_version:{rel}')
    if re.search(r'^doi\s*:',t,re.M): errors.append(f'prefilled_version_doi:{rel}')
    if re.search(r'^date-released\s*:',t,re.M): errors.append(f'prefilled_release_date:{rel}')
    if 'given-names: "Jinnan"' not in t or 'given-names: "Andrew E. H."' not in t: errors.append(f'authors_missing:{rel}')

# Human verification.
reg=EVID/'data/AUTHORITATIVE_EVIDENCE_REGISTRY.csv'
if reg.exists():
    with reg.open(newline='',encoding='utf-8-sig') as fh: rows=list(csv.DictReader(fh))
    if len(rows)!=49: errors.append(f'registry_rows:{len(rows)}')
    if any(r.get('human_verification_status')!='human_verified' for r in rows): errors.append('registry_not_49_human_verified')
    if any(not r.get('verification_date') or 'Jinnan Wei' not in r.get('verifier','') for r in rows): errors.append('registry_verification_metadata_incomplete')
cl=EVID/'data/HUMAN_VERIFICATION_CHANGELOG.csv'
if cl.exists():
    with cl.open(newline='',encoding='utf-8-sig') as fh: crows=list(csv.DictReader(fh))
    if len(crows)!=49: errors.append(f'changelog_rows:{len(crows)}')
    if any(r.get('final_human_verification_status')!='human_verified' for r in crows): errors.append('changelog_not_locked')

# Scoring lock.
for name in ['mfp_scores.csv','candidate_opr_table.csv','calibration_summary.json']:
    hits=list(EVID.rglob(name)) if EVID.exists() else []
    if hits: errors.append(f'forbidden_source_grounded_output:{name}')
if (EVID/'scripts').exists():
    for p in (EVID/'scripts').glob('*.py'):
        t=p.read_text(encoding='utf-8')
        if re.search(r'(^|\s)(import|from)\s+.*mfp_score|candidate_ranking|opr_optimizer',t):
            errors.append(f'source_grounded_scorer_import:{p.relative_to(ROOT)}')

# Obsolete public-tree paths.
obsolete=[
 'audit','manuscript','submission_materials','FILE_TREE.txt','MANIFEST_FOR_REVIEWERS.md',
 'PACKAGE_CONTENTS.md','PUSH_TO_GITHUB_FROM_D_DRIVE.md','README_v1.0.0_package_note.md',
 'RELEASE_NOTES_v1.0.0.md','SOFTWARE_FILE_INDEX.md','ZIP_README_FOR_REVIEWERS.md',
 'DELETE_PATHS_v29A.txt','GITIGNORE_ADDITIONS_v29A.txt','validate_v29A_2_release_candidate.py',
 'SupplementarySoftware1/RELEASE_CANDIDATE_STATUS.md',
 'SupplementarySoftware1/outputs/release_v1.0.0_run_all.log',
 'SupplementarySoftware1/outputs/release_v1.0.0_validate_outputs.log',
 'SupplementarySoftware1/outputs/run_all_stdout.txt','SupplementarySoftware1/outputs/run_all_stderr.txt',
 'SupplementarySoftware1/outputs/validate_stdout.txt','SupplementarySoftware1/outputs/validate_stderr.txt',
]
for rel in obsolete:
    if (ROOT/rel).exists(): errors.append(f'obsolete_public_path:{rel}')

# Full-tree text scan. Historical prior state in the locked changelog is retained by design.
text_suffixes={'.md','.txt','.json','.csv','.cff','.py','.tex','.bib','.yml','.yaml'}
patterns=[
 'INSERT VERSIONED ZENODO DOI','placeholder DOI','paper2_v18_MITLicenseConfirmedReleaseReady_QC',
 'zenodo_metadata_draft.json','GeminiMinorPatch','FigureBoxWidthPatch','FinalPortalUploadPack',
 'READY FOR CODEX LOCAL INTEGRATION','Local Git integration: not executed',
]
for p in ROOT.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in text_suffixes: continue
    rel=p.relative_to(ROOT).as_posix()
    if '__pycache__' in rel or rel==Path(__file__).name: continue
    try: t=p.read_text(encoding='utf-8-sig')
    except Exception: continue
    for pattern in patterns:
        if pattern.lower() in t.lower(): errors.append(f'public_trace:{rel}:{pattern}')
    if 'pending_user_or_coauthor_confirmation' in t:
        if rel=='SupplementarySoftware1/source_grounded_evidence/data/HUMAN_VERIFICATION_CHANGELOG.csv':
            retained_hits.append({'path':rel,'term':'pending_user_or_coauthor_confirmation','justification':'historical prior status retained in frozen change-control record'})
        else:
            errors.append(f'pending_verification_trace:{rel}')

report={
 'scope':'v1.1.0 final release-state, archive-hygiene, human-verification and no-scoring validation',
 'status':'PASS' if not errors else 'FAIL',
 'errors':errors,
 'warnings':warnings,
 'retained_hits':retained_hits,
 'human_verified_count':49 if reg.exists() else None,
 'scoring_admitted':False,
 'synthetic_imputation_used':False,
 'release_action_performed':False,
}
(ROOT/'PUBLIC_ARCHIVE_HYGIENE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
raise SystemExit(0 if not errors else 1)
