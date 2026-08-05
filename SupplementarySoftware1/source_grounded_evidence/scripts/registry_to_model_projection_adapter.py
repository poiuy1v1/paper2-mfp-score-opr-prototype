#!/usr/bin/env python3
"""Validate Layer-A evidence records and generate projection-readiness outputs.

This adapter does not call the MFP scorer, does not generate rankings, and does not
impute or externally derive missing values. All scoring_admitted values are false.
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path

MISSING = {'', 'null', 'none', 'not_reported_in_source', 'not_applicable'}
REQUIRED_LAYER_A = [
    'record_id','source_id','source_identifier','source_location','material_name',
    'reported_sample_form','outcome_status','evidence_confidence'
]
MAPPING = [
    ('modulator_concentration_m','source_reported_modulator_concentration_m'),
    ('precursor_concentration_m','source_reported_precursor_concentration_m'),
    ('temperature_c','temperature_c'),
    ('drying_route','drying_route'),
    ('pore_radius_nm','source_reported_pore_radius_nm'),
    ('surface_tension_mN_m','source_reported_surface_tension_mN_m'),
    ('contact_angle_deg','source_reported_contact_angle_deg'),
    ('framework_stability_z','source_reported_framework_stability_z'),
]
ALLOWED_OUTCOMES = {
    'confirmed_monolith','confirmed_gel_or_monolithic_intermediate',
    'explicit_non_monolithic_or_failed_outcome','powder_only_under_reported_conditions',
    'ambiguous','not_assessed'
}

def present(v: str | None) -> bool:
    return str(v).strip().lower() not in MISSING

def main(registry_csv: str, out_dir: str) -> int:
    reg_path=Path(registry_csv); out=Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    with reg_path.open(encoding='utf-8-sig', newline='') as f:
        rows=list(csv.DictReader(f))
    decisions=[]; blockers=[]; errors=[]
    seen=set()
    for r in rows:
        rid=r.get('record_id','')
        duplicate=rid in seen
        seen.add(rid)
        layer_errors=[f for f in REQUIRED_LAYER_A if not present(r.get(f))]
        if r.get('outcome_status') not in ALLOWED_OUTCOMES:
            layer_errors.append('outcome_status_not_in_controlled_vocabulary')
        if r.get('imputation_used') != 'none':
            layer_errors.append('imputation_used_must_equal_none')
        if duplicate:
            layer_errors.append('duplicate_record_id')
        condition_valid=all(present(r.get(k)) for k in ['material_name','synthesis_or_gelation_route','reported_sample_form','outcome_status'])
        available=[]; missing=[]
        for target,source in MAPPING:
            (available if present(r.get(source)) else missing).append(target)
        coverage=len(available)/len(MAPPING)
        row_blockers=list(missing)
        if layer_errors: row_blockers.extend(layer_errors)
        if not condition_valid: row_blockers.append('condition_unit_invalid')
        # current-release hard stop: even complete records are not admitted without a separately approved scoring policy.
        projection_status='retain_in_layer_A_do_not_score'
        scoring_admitted=False
        decisions.append({
            'record_id':rid,
            'layer_A_valid':str(not layer_errors).lower(),
            'condition_unit_valid':str(condition_valid).lower(),
            'required_field_coverage':f'{coverage:.3f}',
            'available_reported_fields':'|'.join(available),
            'missing_reported_fields':'|'.join(missing),
            'derived_field_requested':'false',
            'derived_field_approved':'false',
            'imputation_used':'none',
            'projection_status':projection_status,
            'projection_blockers':'|'.join(row_blockers),
            'scoring_admitted':'false',
        })
        for field in row_blockers:
            blockers.append({'record_id':rid,'blocker':field,'blocker_class':'missing_or_policy_blocker'})
        errors.extend(f'{rid}:{e}' for e in layer_errors)
    dfields=list(decisions[0].keys())
    with (out/'MODEL_INPUT_PROJECTION_CANDIDATES.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=dfields); w.writeheader(); w.writerows(decisions)
    with (out/'MODEL_INPUT_PROJECTION_BLOCKERS.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['record_id','blocker','blocker_class']); w.writeheader(); w.writerows(blockers)
    report={
        'validation_scope':'Layer-A schema and projection-readiness only; no scoring',
        'status':'PASS' if not errors else 'FAIL',
        'record_count':len(rows),
        'layer_A_valid_count':sum(d['layer_A_valid']=='true' for d in decisions),
        'condition_unit_valid_count':sum(d['condition_unit_valid']=='true' for d in decisions),
        'scoring_admitted_count':0,
        'synthetic_imputation_count':0,
        'derived_field_request_count':0,
        'errors':errors,
        'warnings':[],
        'hard_stop':'No MFP or OPR scoring is called in the current evidence release.'
    }
    (out/'ADAPTER_VALIDATION_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
    return 0 if not errors else 1

if __name__=='__main__':
    if len(sys.argv)!=3:
        raise SystemExit('usage: registry_to_model_projection_adapter.py REGISTRY.csv OUTPUT_DIR')
    raise SystemExit(main(sys.argv[1],sys.argv[2]))
