# EMS Runs Profiling Report (Indiana EMS, 2014-2025)

Generated: 2026-06-22
Source: `./data/ems_runs_*.csv`
Method: chunked full-file scan (pandas, 200k-row chunks), all columns read as string.

---

## 1. Schema (all years identical)

22 columns, identical names and order across all 13 files. No columns added or removed in any year. Only formatting variance: `ems_runs_2019.csv` quotes every header and field; all other years are unquoted. Header whitespace exists in the data dictionary (`INJURY_FLG `, `CHIEF_COMPLAINT_ANATOMIC_LOC `, etc.) and is stripped during profiling.

| # | Column | Dictionary type | Profiled type |
|---|--------|-----------------|---------------|
| 1 | INCIDENT_DT | date | datetime (date only after 2021) |
| 2 | INCIDENT_COUNTY | text | categorical (92 values) |
| 3 | CHIEF_COMPLAINT_DISPATCH | text | free text |
| 4 | CHIEF_COMPLAINT_ANATOMIC_LOC | text | categorical |
| 5 | PRIMARY_SYMPTOM | text | categorical/free text |
| 6 | PROVIDER_IMPRESSION_PRIMARY | text | high-cardinality (coded + free text) |
| 7 | DISPOSITION_ED | text | categorical (near-empty) |
| 8 | DISPOSITION_HOSPITAL | text | categorical (near-empty) |
| 9 | INJURY_FLG | flag | text Yes/No/Unknown |
| 10 | NALOXONE_GIVEN_FLG | flag | binary 0/1 |
| 11 | MEDICATION_GIVEN_OTHER_FLG | flag | binary 0/1 |
| 12 | DESTINATION_TYPE | text | categorical |
| 13 | PROVIDER_TYPE_STRUCTURE | text | categorical (4-5 values) |
| 14 | PROVIDER_TYPE_SERVICE | text | categorical (5-6 values) |
| 15 | PROVIDER_TYPE_SERVICE_LEVEL | text | categorical (6-8 values) |
| 16 | PROVIDER_TO_SCENE_MINS | numeric | integer minutes |
| 17 | PROVIDER_TO_DESTINATION_MINS | numeric | integer minutes |
| 18 | UNIT_NOTIFIED_BY_DISPATCH_DT | datetime | datetime |
| 19 | UNIT_ARRIVED_ON_SCENE_DT | datetime | datetime |
| 20 | UNIT_ARRIVED_TO_PATIENT_DT | datetime | datetime |
| 21 | UNIT_LEFT_SCENE_DT | datetime | datetime |
| 22 | PATIENT_ARRIVED_DESTINATION_DT | datetime | datetime |

There is no incident ID, patient ID, unit ID, or record ID in any file. There is no natural primary key.

---

## 2. Volume Trend

| Year | Rows | Change (Year-over-Year) |
|------|-----:|-----------:|
| 2014 | 418,661 | - |
| 2015 | 519,648 | +24.1% |
| 2016 | 645,016 | +24.1% |
| 2017 | 594,146 | -7.9% |
| 2018 | 364,945 | -38.6% |
| 2019 | 905,603 | +148.1% |
| 2020 | 1,079,141 | +19.2% |
| 2021 | 1,243,403 | +15.2% |
| 2022 | 1,141,648 | -8.2% |
| 2023 | 461,217 | -59.6% |
| 2024 | 1,613,800 | +249.9% |
| 2025 | 1,545,309 | -4.2% |

Total: 10,532,537 rows.

The 2018 and 2023 dips and the 2019/2024 spikes are too large to be real call-volume change. They indicate reporting/extract coverage changes (agencies onboarding/offboarding the state registry, or partial-year extracts), not actual EMS demand. Flag as a known limitation; do not treat year-over-year counts as demand trends without agency-level normalization.

---

## 3. Null Rates (% null, by column and year)

| Column | 2014 | 2016 | 2018 | 2020 | 2022 | 2024 | 2025 |
|--------|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
| INCIDENT_DT | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| INCIDENT_COUNTY | 0.18 | 0.26 | 0.12 | 0.05 | 0.01 | 0.01 | 0.01 |
| CHIEF_COMPLAINT_DISPATCH | 31.2 | 30.3 | 0.65 | 0.04 | 0.03 | 0.01 | 0.01 |
| CHIEF_COMPLAINT_ANATOMIC_LOC | 70.9 | 66.8 | 70.4 | 49.2 | 53.1 | 65.8 | 62.8 |
| PRIMARY_SYMPTOM | 37.0 | 39.5 | 42.0 | 25.1 | 23.4 | 18.2 | 16.2 |
| PROVIDER_IMPRESSION_PRIMARY | 47.0 | 56.8 | 45.3 | 20.6 | 19.6 | 13.9 | 13.6 |
| DISPOSITION_ED | 99.5 | 99.0 | 99.3 | 99.4 | 99.4 | 96.8 | 97.3 |
| DISPOSITION_HOSPITAL | 99.2 | 99.3 | 99.7 | 99.8 | 99.8 | 97.5 | 97.9 |
| INJURY_FLG | 24.0 | 34.5 | 33.1 | 14.9 | 17.7 | 15.7 | 15.3 |
| NALOXONE_GIVEN_FLG | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| MEDICATION_GIVEN_OTHER_FLG | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| DESTINATION_TYPE | 24.9 | 26.4 | 42.6 | 25.1 | 24.0 | 18.8 | 18.2 |
| PROVIDER_TYPE_STRUCTURE | 0.0 | 0.96 | 0.0 | 0.0 | 0.37 | 0.97 | 1.3 |
| PROVIDER_TYPE_SERVICE | 0.47 | 0.97 | 0.0 | 0.0 | 0.37 | 0.97 | 1.3 |
| PROVIDER_TYPE_SERVICE_LEVEL | 0.15 | 5.5 | 0.51 | 0.57 | 1.0 | 2.9 | 3.0 |
| PROVIDER_TO_SCENE_MINS | 6.0 | 7.5 | 9.9 | 3.8 | 2.7 | 2.0 | 2.1 |
| PROVIDER_TO_DESTINATION_MINS | 22.5 | 23.6 | 49.0 | 25.3 | 25.8 | 22.1 | 21.9 |
| UNIT_NOTIFIED_BY_DISPATCH_DT | 0.24 | 0.25 | 0.07 | 0.04 | 0.05 | 0.02 | 0.02 |
| UNIT_ARRIVED_ON_SCENE_DT | 4.5 | 5.1 | 9.4 | 3.7 | 2.7 | 1.9 | 2.0 |
| UNIT_ARRIVED_TO_PATIENT_DT | 18.0 | 18.4 | 33.1 | 14.4 | 16.2 | 35.6 | 29.7 |
| UNIT_LEFT_SCENE_DT | 17.6 | 17.6 | 37.4 | 19.9 | 19.5 | 39.3 | 33.9 |
| PATIENT_ARRIVED_DESTINATION_DT | 22.3 | 17.6 | 22.9 | 24.8 | 21.7 | 21.7 | 21.7 |

Key points:
- DISPOSITION_ED and DISPOSITION_HOSPITAL are effectively empty (97-99.8% null every year). They cannot support analytics. These are hospital-outcome elements that EMS agencies rarely receive back.
- CHIEF_COMPLAINT_ANATOMIC_LOC is half to two-thirds null every year.
- CHIEF_COMPLAINT_DISPATCH was ~30% null in 2014-2016, then dropped to near-zero from 2018 on (data-capture improvement).
- INCIDENT_DT, NALOXONE_GIVEN_FLG, MEDICATION_GIVEN_OTHER_FLG are never null (mandatory at source).

---

## 4. Cardinality (key fields)

| Field | 2014 | 2016 | 2018 | 2020 | 2022 | 2024 | 2025 | Interpretation |
|-------|-----:|-----:|-----:|-----:|-----:|-----:|-----:|----------------|
| INCIDENT_COUNTY | 92 | 92 | 92 | 92 | 92 | 92 | 92 | Stable. Indiana has exactly 92 counties. Clean dimension. |
| PROVIDER_IMPRESSION_PRIMARY | 91 | 154 | 974 | 1,710 | 1,771 | 1,813 | 1,831 | Explodes over time. Coding scheme changed from a short pick list to ICD-10-style codes / free text. Needs mapping. |
| DISPOSITION_ED | 5 | 5 | 21 | 21 | 19 | 21 | 21 | Domain expanded ~2017-2018. |
| DISPOSITION_HOSPITAL | 12 | 7 | 23 | 19 | 19 | 19 | 20 | Domain drift. |
| DESTINATION_TYPE | 10 | 16 | 17 | 15 | 24 | 26 | 28 | Domain grows steadily. |
| PROVIDER_TYPE_STRUCTURE | 5 | 5 | 5 | 5 | 5 | 4 | 4 | Small, stable. Clean dimension. |
| PROVIDER_TYPE_SERVICE | 5 | 5 | 6 | 6 | 6 | 6 | 5 | Small, stable. Clean dimension. |
| PROVIDER_TYPE_SERVICE_LEVEL | 8 | 8 | 8 | 7 | 7 | 6 | 6 | Small, stable. Clean dimension. |

---

## 5. Value-range and domain issues

### 5.1 Duration fields (impossible values)
`PROVIDER_TO_SCENE_MINS` and `PROVIDER_TO_DESTINATION_MINS`:
- Negative values appear from 2022 onward (was 0 before): 2022 (103/109 negatives), 2023 (55/55), 2024 (129/100), 2025 (73/81). A negative response time is impossible.
- Extreme maxima every year: up to 11,571,854 minutes (~22 years) in 2022, 10,519,220 in 2025, 9,466,619 in 2019. These are data-entry or unit errors. A plausible upper bound is a few thousand minutes.
- 2024 min of -8,415,413 on PROVIDER_TO_DESTINATION_MINS is a gross outlier.

### 5.2 Date fields (out-of-range)
INCIDENT_DT is always within its file's year (clean). The unit/patient timestamp fields are not:
- Historic-impossible values: UNIT_LEFT_SCENE_DT min 1824-04-15 (2015), 1901-06-26 (2016), 1959-05-12 (2019), 1958-04-28 (2020); PATIENT_ARRIVED_DESTINATION_DT min 1952-03-26 (2020).
- Future-impossible values: UNIT_LEFT_SCENE_DT max 2043-08-17 (2021), 2040-02-03 (2024), 2048-02-22 (2025); UNIT_ARRIVED_TO_PATIENT_DT max 2029-01-29 (2025); PATIENT_ARRIVED_DESTINATION_DT max 2025-12-23 in the 2022 file.
- Cross-year bleed: timestamps legitimately spill a few days into the next year (incident late in December, patient arrives in January). Small forward spill is valid; multi-year and pre-1990 values are not.

### 5.3 Timestamp granularity change
Through 2021, unit timestamps carry full time-of-day (e.g. `2020-12-31 23:59:51`). From 2022 onward most timestamps are truncated to midnight (`2022-12-31 00:00:00`), so intra-day timing is lost. This breaks any computed-duration validation against the *_MINS fields for 2022+.

### 5.4 Flag encoding inconsistency
- INJURY_FLG: text. 2014 had only `Yes`/`No`; from 2015 on a third value `Unknown` appears.
- NALOXONE_GIVEN_FLG / MEDICATION_GIVEN_OTHER_FLG: numeric `0`/`1`.
- 2018 NALOXONE_GIVEN_FLG has a single distinct value (`0`) for the entire year, i.e. naloxone was never recorded as given. Likely a capture gap that year, not reality.

### 5.5 Duplicates
No natural key exists, so exact-duplicate detection would require hashing the full row. Not computed in this pass (would require a second full scan). Given no incident ID, true de-duplication is not possible; flag as a limitation.

---

## 6. Aggregate findings

1. Schema is stable across all 12 years -- no breaking changes, no column drift. The only structural variance is CSV quoting in 2019. A single staging table definition serves all years.
2. No natural/business key. One row = one EMS run. There is no way to link runs to patients, units, or incidents, and no way to de-duplicate reliably. This constrains the dimensional model to a run-grain fact with no patient or unit dimension keyed from source.
3. Two columns (DISPOSITION_ED, DISPOSITION_HOSPITAL) are ~99% empty and carry almost no analytic value.
4. PROVIDER_IMPRESSION_PRIMARY changed coding systems over time (91 -> 1,831 distinct). Without a crosswalk it cannot be a stable conformed dimension; treat as degenerate/text or map to NEMSIS impression codes.
5. Duration fields and unit timestamps contain impossible values (negatives, multi-year spans, 19th-century and future dates). These require range-validation rules and quarantine.
6. Timestamp granularity drops to date-only in 2022+, so derived timing metrics are not comparable before/after 2022.
7. Clean, low-cardinality dimension candidates: INCIDENT_COUNTY (92), PROVIDER_TYPE_STRUCTURE, PROVIDER_TYPE_SERVICE, PROVIDER_TYPE_SERVICE_LEVEL, DESTINATION_TYPE.
