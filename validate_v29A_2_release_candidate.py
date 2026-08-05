#!/usr/bin/env python3
"""Validate the v1.1.0 release candidate without publishing or scoring."""
from __future__ import annotations
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SW = ROOT / 'SupplementarySoftware1'
EVID = SW / 'source_grounded_evidence'
errors=[]; warnings=[]

def require(p: Path):
    if not p.exists(): errors.append(f'missing:{p.relative_to(ROOT)}')

for rel in [
    'README.md','LICENSE','CITATION.cff','.zenodo.json','RELEASE_NOTES_v1.1.0.md',
    'SupplementarySoftware1/run_all.py','SupplementarySoftware1/validate_outputs.py',
    'SupplementarySoftware1/source_grounded_evidence/data/AUTHORITATIVE_EVIDENCE_REGISTRY.csv',
    'SupplementarySoftware1/source_grounded_evidence/data/HUMAN_VERIFICATION_CHANGELOG.csv',
    'SupplementarySoftware1/source_grounded_evidence/data/Source_Grounded_Evidence_Workbook.xlsx',
    'SupplementarySoftware1/source_grounded_evidence/docs/AUTHOR_ATTESTATION_RECORD.md',
    'SupplementarySoftware1/source_grounded_evidence/docs/LITERATURE_RETRIEVAL_SCREENING_AND_VERIFICATION.md',
    'SupplementarySoftware1/source_grounded_evidence/data/CANDIDATE_EVIDENCE_CLASSIFICATION.csv',
]: require(ROOT/rel)

# Registry human-verification gate.
reg=EVID/'data/AUTHORITATIVE_EVIDENCE_REGISTRY.csv'
if reg.exists():
    with reg.open(newline='',encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
    if len(rows)!=49: errors.append(f'registry_row_count:{len(rows)}')
    statuses=[r.get('human_verification_status','') for r in rows]
    if any(x!='human_verified' for x in statuses): errors.append('registry_not_49_of_49_human_verified')
    if any(not r.get('verification_date') for r in rows): errors.append('missing_verification_date')
    if any('Jinnan Wei' not in r.get('verifier','') for r in rows): errors.append('missing_human_verifier')

# Frozen changelog.
cl=EVID/'data/HUMAN_VERIFICATION_CHANGELOG.csv'
if cl.exists():
    with cl.open(newline='',encoding='utf-8-sig') as f: crows=list(csv.DictReader(f))
    if len(crows)!=49: errors.append(f'changelog_row_count:{len(crows)}')
    if any(r.get('final_human_verification_status')!='human_verified' for r in crows): errors.append('changelog_status_not_locked')

# Metadata should not pre-fill a not-yet-minted release DOI or release date.
for p in [ROOT/'.zenodo.json', SW/'zenodo_metadata.json']:
    if p.exists():
        obj=json.loads(p.read_text(encoding='utf-8'))
        if 'doi' in obj: errors.append(f'prefilled_doi:{p.name}')
        if 'publication_date' in obj: errors.append(f'prefilled_publication_date:{p.name}')
        if str(obj.get('version','')) not in {'v1.1.0','1.1.0'}: errors.append(f'wrong_version:{p.name}')
cff=(ROOT/'CITATION.cff').read_text(encoding='utf-8') if (ROOT/'CITATION.cff').exists() else ''
if re.search(r'^doi\s*:',cff,re.M): errors.append('prefilled_doi:CITATION.cff')
if re.search(r'^date-released\s*:',cff,re.M): errors.append('prefilled_release_date:CITATION.cff')
if not re.search(r'^version:\s*[\"\']?v?1\.1\.0[\"\']?\s*$',cff,re.M): errors.append('wrong_version:CITATION.cff')

# Authorship and funding administrative lock.
for p in [ROOT/'CITATION.cff', SW/'CITATION.cff']:
    if p.exists():
        t=p.read_text(encoding='utf-8')
        if 'given-names: "Jinnan"' not in t or 'given-names: "Andrew E. H."' not in t:
            errors.append('author_metadata_incomplete:'+str(p.relative_to(ROOT)))
        if 'aehw2@cam.ac.uk' not in t:
            errors.append('corresponding_author_email_missing:'+str(p.relative_to(ROOT)))
for p in [ROOT/'.zenodo.json', SW/'zenodo_metadata.json']:
    if p.exists():
        obj=json.loads(p.read_text(encoding='utf-8'))
        names=[c.get('name','') for c in obj.get('creators',[])]
        if names != ['Wei, Jinnan','Wheatley, Andrew E. H.']:
            errors.append('zenodo_creator_order_or_names:'+str(p.relative_to(ROOT)))
for p in [ROOT/'README.md', ROOT/'RELEASE_NOTES_v1.1.0.md', SW/'README.md', SW/'RELEASE_CANDIDATE_STATUS.md']:
    if p.exists():
        t=p.read_text(encoding='utf-8')
        if 'Andrew E. H. Wheatley' not in t or 'Jinnan Wei' not in t:
            errors.append('release_facing_author_lock_missing:'+str(p.relative_to(ROOT)))
        if 'no specific grant' not in t.lower():
            errors.append('funding_lock_missing:'+str(p.relative_to(ROOT)))
status=(SW/'RELEASE_CANDIDATE_STATUS.md').read_text(encoding='utf-8') if (SW/'RELEASE_CANDIDATE_STATUS.md').exists() else ''
if 'READY FOR CODEX LOCAL INTEGRATION AND VALIDATION' not in status:
    errors.append('overlay_not_released_for_local_integration')
if 'author confirmation required' in status.lower():
    errors.append('stale_administrative_hold')

# Source-grounded scoring lock.
for forbidden in ['mfp_scores.csv','candidate_opr_table.csv','calibration_summary.json']:
    hits=[p for p in EVID.rglob(forbidden)]
    if hits: errors.append('forbidden_source_grounded_output:'+forbidden)
for p in (EVID/'scripts').glob('*.py'):
    txt=p.read_text(encoding='utf-8')
    if re.search(r'import\s+.*mfp_score|from\s+.*mfp_score|candidate_ranking|opr_optimizer',txt):
        errors.append('source_grounded_scorer_import:'+p.name)

# Scientific framing in release-facing text.
for p in [ROOT/'README.md',ROOT/'RELEASE_NOTES_v1.1.0.md',SW/'README.md']:
    if p.exists():
        t=p.read_text(encoding='utf-8')
        if 'Monolithic Formation Probability' in t: errors.append('probability_language:'+p.name)
        if 'pending_user_or_coauthor_confirmation' in t: errors.append('pending_verification_language:'+p.name)

report={
    'scope':'v29A.2 authorship/funding-locked repository release-candidate validation; no Git, release, DOI minting or source-grounded scoring',
    'status':'PASS' if not errors else 'FAIL',
    'errors':errors,
    'warnings':warnings,
    'human_verified_count':49 if not errors or reg.exists() else None,
    'scoring_admitted':False,
    'release_action_performed':False,
}
print(json.dumps(report,indent=2))
raise SystemExit(0 if not errors else 1)
