# Database Model

Source of truth: [`sql/schema.sql`](../sql/schema.sql). This document describes the
conceptual model; for the full DDL (constraints, indexes), see the SQL file.

## Entity–relationship diagram (textual)

```
patients (1) ───< comorbidities
patients (1) ───< prescriptions >─── (1) medications
patients (1) ───< alerts >─── (0..1) prescriptions
alerts   (0..1) >─── beers_pim_criteria
patients (1) ───< risk_scores
```

## Tables

### `patients`
Minimal record, **without PII**. `pseudonym` is a non-reversible identifier
(e.g., a hash) used to correlate with external systems without exposing identity.
`egfr_ml_min_1_73m2` is the estimated glomerular filtration rate (CKD-EPI), used by
the renal-adjustment rules.

### `comorbidities`
Active diagnoses (ICD-10) used by the disease–drug interaction rules (e.g., `I50`
heart failure enables the contraindicated-NSAID criterion).

### `medications`
Master catalog coded by **ATC** (Anatomical Therapeutic Chemical, WHO). Matching
against `beers_pim_criteria` is done by ATC prefix (`atc_pattern`), allowing a
criterion to cover an entire class (e.g., `N05BA` = all benzodiazepines) or a
specific molecule (e.g., `A10BB01` = glibenclamide).

### `beers_pim_criteria`
The central table of the rule engine. Each row is a criterion with:
- `criteria_type`: how the criterion is evaluated (independent of diagnosis,
  disease-specific, drug–drug interaction, renal adjustment);
- `atc_pattern` / `interacting_atc_pattern`: matching keys;
- `related_condition_icd10`: used when the criterion depends on a comorbidity;
- `egfr_threshold_ml_min`: used when the criterion depends on renal function;
- `rationale`, `recommendation`, `source_reference`: explanatory text shown in the alert.

See [`docs/beers_criteria.md`](beers_criteria.md) for the disclaimer about the
illustrative nature of this subset.

### `prescriptions`
One row per prescribed medication. The "active" state (`end_date IS NULL OR
end_date >= CURRENT_DATE`) is computed at query time by the
`v_active_prescriptions` view and, in the domain layer, by the
`Prescription.is_active` property — deliberately **not** materialized as a
generated column, because PostgreSQL requires an immutable expression in
`GENERATED` columns and `CURRENT_DATE` is not immutable. `duration_days` (computed
in `domain.entities.Prescription`) is used by the chronic-use rules (PPI > 8 weeks,
metoclopramide > 12 weeks).

### `alerts`
Persisted output of the rule engine — enables auditing (who reviewed, when, and the
status: open/acknowledged/substituted/dismissed-with-justification).

### `risk_scores`
Aggregated snapshot per assessment run: counts (PIM, DDI, comorbidities), the
rule-based risk level, and optionally the ML model probability with `model_version`
for traceability (which model produced which score).

## Why PostgreSQL

- **JSONB** (`risk_scores.explanation`) to store semi-structured explainability
  without an extra table;
- the **`uuid-ossp` extension** for UUID primary keys (avoids the volume/sequence
  leakage that serial IDs would expose);
- **views** (`v_active_prescriptions`) centralize the "active prescription" logic,
  evaluated at query time, keeping it consistent without a trigger;
- maturity in healthcare environments (HIPAA/LGPD compliance tooling, RLS for
  future multi-tenancy).
