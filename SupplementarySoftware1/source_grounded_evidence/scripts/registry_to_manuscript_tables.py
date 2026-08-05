#!/usr/bin/env python3
"""Generate descriptive manuscript tables from the source-grounded evidence registry.

This script performs descriptive aggregation only. It does not import, invoke, or
reproduce the MFP scorer, OPR ranking, classifier training, calibration, or model
performance metrics.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

REGISTRY = DATA / "AUTHORITATIVE_EVIDENCE_REGISTRY.csv"
SOURCE_SUMMARY = DATA / "DESCRIPTIVE_SOURCE_SUMMARY.csv"
BS = chr(92)
ROW_END = " " + BS + BS

CITATION_KEYS = {
    "SRC01": "ref4",
    "SRC02": "ref55",
    "SRC03": "ref56",
    "SRC04": "ref57",
    "SRC05": "ref58",
    "SRC06": "ref59",
    "SRC07": "ref60",
    "SRC08": "ref61",
    "SRC09": "ref62",
}

SELECTED_PAIRS = [
    ("UiO-66 washing/drying", "P2V25-0001", "P2V25-0003"),
    ("HKUST-1 particle-size/drying window", "P2V26-0028", "P2V26-0033"),
    ("ZIF-8 drying rate", "P2V27-0035", "P2V27-0036"),
    ("ZIF-8 ligand-assisted route", "P2V27-0040", "P2V27-0042"),
    ("ZIF-8 solvent route", "P2V27-0047", "P2V27-0048"),
]

STATUS_LABEL = {
    "confirmed_monolith": "confirmed monolith",
    "confirmed_gel_or_monolithic_intermediate": "gel/intermediate",
    "powder_only_under_reported_conditions": "powder under reported condition",
    "explicit_non_monolithic_or_failed_outcome": "explicit non-monolithic outcome",
    "ambiguous": "ambiguous",
    "not_assessed": "not assessed",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def latex_escape(value: str) -> str:
    value = value or ""
    replacements = {
        BS: BS + "textbackslash{}",
        "&": BS + "&",
        "%": BS + "%",
        "$": BS + "$",
        "#": BS + "#",
        "_": BS + "_",
        "{": BS + "{",
        "}": BS + "}",
        "~": BS + "textasciitilde{}",
        "^": BS + "textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in value)


def concise_condition(row: dict[str, str]) -> str:
    route = row.get("synthesis_or_gelation_route", "")
    temp = row.get("drying_temperature_c", "")
    if temp not in ("", "not_reported_in_source", "not_applicable"):
        return f"{route}; drying {temp} C"
    return route


def source_table(source_rows: list[dict[str, str]]) -> str:
    lines = [
        BS + "begin{table}[htbp]",
        BS + "centering",
        BS + "caption{Source-level composition of the condition-level evidence registry. Counts are descriptive records rather than statistically independent samples or class-balanced labels.}",
        BS + "label{tab:source-coverage}",
        BS + "scriptsize",
        BS + "resizebox{" + BS + "textwidth}{!}{%",
        BS + "begin{tabular}{@{}llllrrrr@{}}",
        BS + "toprule",
        "Source & Year & Venue & Framework families & Records & Monolith & Gel/intermediate & Powder/failure" + ROW_END,
        BS + "midrule",
    ]
    for row in source_rows:
        sid = row["source_id"]
        cite = CITATION_KEYS[sid]
        powder_failure = int(row["powder_only_condition"]) + int(row["explicit_failure"])
        lines.append(
            f"{sid}{BS}cite{{{cite}}} & {latex_escape(row['year'])} & {latex_escape(row['venue'])} & "
            f"{latex_escape(row['framework_families'].replace('|', ', '))} & {row['record_count']} & "
            f"{row['confirmed_monolith']} & {row['gel_or_intermediate']} & {powder_failure}" + ROW_END
        )
    lines += [BS + "bottomrule", BS + "end{tabular}%", "}", BS + "end{table}"]
    return "\n".join(lines) + "\n"


def contrast_table(registry_rows: list[dict[str, str]]) -> tuple[str, list[dict[str, str]]]:
    by_id = {row["record_id"]: row for row in registry_rows}
    selected: list[dict[str, str]] = []
    lines = [
        BS + "begin{table}[htbp]",
        BS + "centering",
        BS + "caption{Representative source-grounded condition contrasts. Each comparison is local to the reported material--condition--outcome units and is not generalized to the framework as a whole.}",
        BS + "label{tab:condition-contrasts}",
        BS + "footnotesize",
        BS + "begin{tabular}{@{}p{2.3cm}p{3.4cm}p{2.4cm}p{3.4cm}p{2.4cm}@{}}",
        BS + "toprule",
        "Contrast & Condition A & Outcome A & Condition B & Outcome B" + ROW_END,
        BS + "midrule",
    ]
    for label, ida, idb in SELECTED_PAIRS:
        a = by_id[ida]
        b = by_id[idb]
        selected.extend([a, b])
        cites = sorted({CITATION_KEYS[a["source_id"]], CITATION_KEYS[b["source_id"]]})
        cite = ",".join(cites)
        lines.append(
            f"{latex_escape(label)}{BS}cite{{{cite}}} & "
            f"{latex_escape(a['material_name'])}: {latex_escape(concise_condition(a))} & "
            f"{latex_escape(a['reported_sample_form'])}; {latex_escape(STATUS_LABEL.get(a['outcome_status'], a['outcome_status']))} & "
            f"{latex_escape(b['material_name'])}: {latex_escape(concise_condition(b))} & "
            f"{latex_escape(b['reported_sample_form'])}; {latex_escape(STATUS_LABEL.get(b['outcome_status'], b['outcome_status']))}" + ROW_END
        )
    lines += [BS + "bottomrule", BS + "end{tabular}", BS + "end{table}"]
    return "\n".join(lines) + "\n", selected


def main() -> None:
    registry = read_csv(REGISTRY)
    sources = read_csv(SOURCE_SUMMARY)
    source_tex = source_table(sources)
    contrast_tex, selected = contrast_table(registry)
    (OUT / "source_coverage_table.tex").write_text(source_tex, encoding="utf-8")
    (OUT / "condition_contrasts_table.tex").write_text(contrast_tex, encoding="utf-8")

    counts = Counter(row["outcome_status"] for row in registry)
    with (OUT / "manuscript_registry_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerow(["record_count", len(registry)])
        writer.writerow(["source_count", len(sources)])
        for key in [
            "confirmed_monolith",
            "confirmed_gel_or_monolithic_intermediate",
            "powder_only_under_reported_conditions",
            "explicit_non_monolithic_or_failed_outcome",
            "ambiguous",
            "not_assessed",
        ]:
            writer.writerow([key, counts[key]])
        writer.writerow(["scoring_admitted", 0])
        writer.writerow(["synthetic_imputation", 0])

    with (OUT / "selected_condition_contrasts.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "record_id", "source_id", "material_name", "synthesis_or_gelation_route",
            "drying_temperature_c", "reported_sample_form", "outcome_status",
            "source_location", "source_url",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in selected:
            writer.writerow({field: row.get(field, "") for field in fields})

    report = {
        "status": "PASS",
        "scope": "descriptive manuscript-table generation only",
        "registry_rows": len(registry),
        "primary_sources": len(sources),
        "selected_condition_contrasts": len(SELECTED_PAIRS),
        "mfp_scores_generated": 0,
        "opr_rankings_generated": 0,
        "classifier_training_performed": False,
        "synthetic_imputation_used": False,
        "scoring_admitted": False,
        "outputs": [
            "source_coverage_table.tex",
            "condition_contrasts_table.tex",
            "manuscript_registry_summary.csv",
            "selected_condition_contrasts.csv",
        ],
    }
    (OUT / "table_generator_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
