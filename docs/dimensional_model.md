# Dimensional Model -- Indiana EMS Runs (Kimball)

Date: 2026-06-22
Inputs: `data_dictionary.csv`, `profiling_report.md`
Target platform: SQL Server (T-SQL), schemas `stg` (staging) and `dw` (warehouse).

---

## 1. Grain

One row in the fact table for each EMS run per source dataset.

Rationale:
- Source has no incident ID, patient ID, unit ID, or record ID. There is no key to support a finer grain (per-patient or per-disposition) and no key to roll multiple rows into a single incident.
- Every row represents a single dispatched-unit encounter described by one incident date, one county, one chief complaint, one provider impression, one disposition, one destination, and the unit's timestamps. That is the run grain.

Alternatives Considered:
- "One disposition" or "one patient" grain was considered and rejected. Disposition columns are 97-99% null and there is no patient identifier, so neither can define or refine the grain.

Result: fact is a transaction-grain fact. Without a natural key, the row identity is a hash of business columns plus source year.

---

## 2. Dimensions

Reusable across any future EMS fact

| Dimension | Source column(s) | Grain | Role | SCD |
|-----------|------------------|-------|------|-----|
| dim_complaint | CHIEF_COMPLAINT_DISPATCH, CHIEF_COMPLAINT_ANATOMIC_LOC, PRIMARY_SYMPTOM | singular combination of dispatch-complaint, anatomic location, and eSituation.09 (parallel to provider impression) | Local to fact | Type 2 |
| dim_county | INCIDENT_COUNTY | one Indiana county | Conformed | Type 1 |
| dim_date | INCIDENT_DT (date part) | one calendar day | Conformed (shared by all date roles) | Type 1 |
| dim_destination_type | DESTINATION_TYPE | one destination-type code | Conformed | Type 2 |
| dim_disposition | DISPOSITION_ED, DISPOSITION_HOSPITAL | one ED+hospital disposition combination | Conformed | Type 2 |
| dim_provider_type | PROVIDER_TYPE_STRUCTURE, PROVIDER_TYPE_SERVICE, PROVIDER_TYPE_SERVICE_LEVEL | one structure/service/level combination | Conformed | Type 2 |
| dim_run_flags | INJURY_FLG, NALOXONE_GIVEN_FLG, MEDICATION_GIVEN_OTHER_FLG | one flag combination (junk dimension) | Local to fact | Type 1 |

### Degenerate and Retained On Fact

The four non-incident unit timestamps (UNIT_NOTIFIED_BY_DISPATCH_DT, UNIT_ARRIVED_ON_SCENE_DT, UNIT_ARRIVED_TO_PATIENT_DT, UNIT_LEFT_SCENE_DT, PATIENT_ARRIVED_DESTINATION_DT) stay on the fact as datetime columns rather than impactful date dimensions. Data quality is poor due to truncation and out-of-bounds values. Intra-day timing is the analytic value, which a day-grain dim_date would discard. A timestamp-based date FK can be added later if day-grain analysis is needed.

As a Type 2 SCD PROVIDER_IMPRESSION_PRIMARY is unreliable. It is retained as degenerate text on fact. From 2014 to 2025 cardinality increased by more than 2000% with change from a coded field to free-text.

---

## 3. SCD decisions and rationale

| Dimension | SCD | Rationale | Alternative rejected |
|-----------|-----|-----------|----------------------|
| dim_complaint | Type 2 | Captures dispatch-coded complaint and anatomic location with symptom differentiator. CHIEF_COMPLAINT_DISPATCH null rate dropped precipitously after 2017 indicating  maturation not system change as in PROVIDER_IMPRESSION_PRIMARY. This preserves integrity of original value at load time both before and after 2018. | Type 1 would restate older reduced coverage records under more recent coding conventions. An impression dimension was considered to capture clinical-narrative but PROVIDER_IMPRESSION_PRIMARY values standard changed making it unreliable as a versioned dimension. |
| dim_county | Type 1 | The 92 Indiana counties are a fixed reference set. Only a label correction would ever change, and history of a typo is not worth tracking. | Type 2 -- no business demand for county-attribute history in this source. |
| dim_date | Type 1 | Calendar attributes are immutable; a given date's year/month/quarter never change. Effectively Type 0. | Type 2 adds rows that never change -- pointless. |
| dim_destination_type | Type 2 | DESTINATION_TYPE domain grew from 10 to 28 distinct values over the period -- the code list demonstrably drifts. Type 2 keeps point-in-time code semantics. | Type 1 loses the meaning a code carried in earlier years. |
| dim_disposition | Type 2 | DISPOSITION_ED/HOSPITAL domains expanded ~2017-2018. Same drift argument as destination. | Type 1 -- same loss-of-meaning problem. |
| dim_run_flags | Type 1 | Junk dimension holding the small cross-product of three flags. The combinations are fixed; nothing changes over time. | Type 2 -- no attribute can change. |
| dim_provider_type | Type 2 | NEMSIS provider-type code lists are revised between standard versions; the profiling shows label/domain drift across years. Type 2 preserves which classification applied when each run was loaded, so historical runs keep their original meaning. | Type 1 would silently restate old runs under new labels and corrupt trend analysis. |

Note: datasets showed no clearly defineable slowly-changing dimensions with a stable business key (i.e., no agency, facility, or patient identity). Type 2 dimensions used code-list with value drift across the 12-year span. Type 2 dimensions were retained to preserve point-in-time code semantics for accurate historical reporting as registry-relevant use case.

---

## 4. Surrogate keys

- Every dimension gets an integer identity surrogate key (`<dim>_key`).
- Type 2 dimensions carry natural/business key, `row_hash`, `valid_from`, `valid_to`, `is_current`.
- Type 1 dimensions carry the natural key plus attributes and updates overwrite in place.
- Fact carries surrogate FKs, plus measures, timestamps, and audit columns without natural-key text.

---

## 5. Measures

fact_ems_run centered

| Measure | Source | Notes |
|---------|--------|-------|
| provider_to_scene_mins | PROVIDER_TO_SCENE_MINS | Validated to a plausible range; out-of-range -> quarantine. |
| provider_to_destination_mins | PROVIDER_TO_DESTINATION_MINS | Same validation. |
| run_count | derived = 1 | Additive count for aggregation. |

The two minute measures are semi-additive (averageable per dimension, not summable across unrelated runs in a meaningful way); `run_count` is fully additive.

---

## 6. Star schema (ERD)

See `erd.mmd` (Mermaid source). Rendered structure: one central `fact_ems_run` referencing the conformed dimensions; `dim_date` is referenced once as incident date, but if per unit timestamp-based dimensions are added they can be incorporated as references.
