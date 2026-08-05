# Descriptor policy

## Core rule

Layer A stores what the primary source reports. Layer B may project only semantically compatible fields under an approved policy. Missing values remain null/not_reported/not_applicable. No silent imputation is allowed.

## Four value classes

1. `source_reported`: explicitly stated for the exact condition-level record.
2. `approved_derived`: calculated only from complete sample-specific source quantities using a documented formula and approved derivation rule. None are approved in.
3. `external_lookup`: handbook/database values with source, composition and temperature. None are approved for scoring in.
4. `prohibited_imputed`: generic defaults, framework-family averages, post-synthesis values substituted for synthesis-state variables, or model-convenience fills. Always prohibited.

## Current decision

`scoring_admitted = false` for every record. The purpose of is descriptive evidence integration and source diversification, not prediction.
