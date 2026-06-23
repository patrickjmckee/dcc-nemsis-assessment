# ./data_quality/raw_ems_dq.md

## Raw Data Quality Observations

### 2026-06-22 -- Profiling of ems_runs_2014..2025 (10.5M rows, 13 files)

- Schema is identical across all 13 files: same 22 columns, same names, same order. No breaking changes. Only 2019 quotes its headers/fields; all others unquoted.
- No natural key in any file: no incident ID, patient ID, unit ID, or record ID. One row = one EMS run. Reliable de-duplication is not possible.
- DISPOSITION_ED and DISPOSITION_HOSPITAL are ~97-99.8% null every year. Effectively empty; near-zero analytic value.
- CHIEF_COMPLAINT_ANATOMIC_LOC is 49-71% null every year.
- CHIEF_COMPLAINT_DISPATCH was ~30% null in 2014-2016, then near-zero from 2018 on (capture improvement).
- INCIDENT_DT, NALOXONE_GIVEN_FLG, MEDICATION_GIVEN_OTHER_FLG are never null in any year.
- INCIDENT_COUNTY is stable at exactly 92 distinct values (Indiana has 92 counties). Clean dimension.
- PROVIDER_IMPRESSION_PRIMARY cardinality explodes 91 (2014) -> 1,831 (2025). Coding scheme changed from short pick list to ICD-style/free text. Needs crosswalk; not a stable dimension as-is.
- DESTINATION_TYPE domain grows 10 -> 28 over the period; DISPOSITION_ED/HOSPITAL domains expanded ~2017-2018.
- PROVIDER_TYPE_STRUCTURE / _SERVICE / _SERVICE_LEVEL are small and stable (4-8 values). Clean dimensions.
- Flag encoding is inconsistent: INJURY_FLG is text (Yes/No, plus Unknown from 2015 on); NALOXONE_GIVEN_FLG and MEDICATION_GIVEN_OTHER_FLG are numeric 0/1.
- 2018 NALOXONE_GIVEN_FLG has a single value (0) all year -- likely a capture gap, not reality.
- Duration fields (PROVIDER_TO_SCENE_MINS, PROVIDER_TO_DESTINATION_MINS): negatives appear 2022+ (impossible); extreme maxima every year up to ~11.5M minutes (~22 years). Need range validation and quarantine.
- Unit/patient timestamp fields contain out-of-range values: historic-impossible (1824, 1901, 1952, 1958, 1959) and future-impossible (2040, 2043, 2048). INCIDENT_DT itself is always within its file year.
- Timestamp granularity drops from full time-of-day (<=2021) to date-only midnight (2022+). Derived timing metrics not comparable across that boundary.
- Volume swings (2018 -38.6%, 2023 -59.6%, 2019 +148%, 2024 +250%) are too large to be real demand; they reflect reporting/extract coverage changes. Do not treat yearly row counts as demand trends.



## 2026-06-22 19:24 -- Session 1.5 Complex DQ Checks

### Check 1: Stub Records
- 2014: 0 stubs / 418,661 rows (0.00%)
- 2015: 1 stubs / 519,648 rows (0.00%)
- 2016: 0 stubs / 645,016 rows (0.00%)
- 2017: 2 stubs / 594,146 rows (0.00%)
- 2018: 0 stubs / 364,945 rows (0.00%)
- 2019: 0 stubs / 905,603 rows (0.00%)
- 2020: 0 stubs / 1,079,141 rows (0.00%)
- 2021: 0 stubs / 1,243,403 rows (0.00%)
- 2022: 0 stubs / 1,141,648 rows (0.00%)
- 2023: 0 stubs / 461,217 rows (0.00%)
- 2024: 4 stubs / 1,613,800 rows (0.00%)
- 2025: 0 stubs / 1,545,309 rows (0.00%)

### Check 2: Timestamp Ordering Violations (notable pairs)
- 2014 / NOTIFIED >= ARRIVED_SCENE: 16,822 violations / 399,260 testable (4.21%)
- 2014 / ARRIVED_SCENE >= LEFT_SCENE: 4,728 violations / 344,263 testable (1.37%)
- 2014 / LEFT_SCENE >= ARRIVED_DEST: 7,807 violations / 324,559 testable (2.41%)
- 2015 / NOTIFIED >= ARRIVED_SCENE: 24,519 violations / 496,921 testable (4.93%)
- 2015 / ARRIVED_SCENE >= LEFT_SCENE: 5,994 violations / 446,169 testable (1.34%)
- 2015 / LEFT_SCENE >= ARRIVED_DEST: 9,643 violations / 411,751 testable (2.34%)
- 2016 / NOTIFIED >= ARRIVED_SCENE: 23,434 violations / 612,136 testable (3.83%)
- 2016 / ARRIVED_SCENE >= LEFT_SCENE: 5,444 violations / 531,510 testable (1.02%)
- 2016 / LEFT_SCENE >= ARRIVED_DEST: 7,072 violations / 493,209 testable (1.43%)
- 2017 / NOTIFIED >= ARRIVED_SCENE: 20,424 violations / 568,471 testable (3.59%)
- 2017 / ARRIVED_SCENE >= LEFT_SCENE: 5,467 violations / 492,050 testable (1.11%)
- 2017 / LEFT_SCENE >= ARRIVED_DEST: 5,857 violations / 459,027 testable (1.28%)
- 2018 / NOTIFIED >= ARRIVED_SCENE: 15,164 violations / 330,608 testable (4.59%)
- 2018 / ARRIVED_SCENE >= LEFT_SCENE: 3,768 violations / 228,399 testable (1.65%)
- 2018 / LEFT_SCENE >= ARRIVED_DEST: 3,559 violations / 186,317 testable (1.91%)
- 2019 / NOTIFIED >= ARRIVED_SCENE: 21,951 violations / 879,567 testable (2.50%)
- 2019 / ARRIVED_SCENE >= LEFT_SCENE: 5,970 violations / 767,420 testable (0.78%)
- 2019 / LEFT_SCENE >= ARRIVED_DEST: 5,801 violations / 735,047 testable (0.79%)
- 2020 / NOTIFIED >= ARRIVED_SCENE: 21,347 violations / 1,039,531 testable (2.05%)
- 2020 / ARRIVED_SCENE >= LEFT_SCENE: 4,240 violations / 864,292 testable (0.49%)
- 2020 / LEFT_SCENE >= ARRIVED_DEST: 5,159 violations / 806,830 testable (0.64%)
- 2021 / NOTIFIED >= ARRIVED_SCENE: 22,425 violations / 1,190,279 testable (1.88%)
- 2021 / ARRIVED_SCENE >= LEFT_SCENE: 5,205 violations / 955,542 testable (0.54%)
- 2021 / LEFT_SCENE >= ARRIVED_DEST: 6,277 violations / 885,221 testable (0.71%)
- 2022 / NOTIFIED >= ARRIVED_SCENE: 1,099,436 violations / 1,111,199 testable (98.94%)
- 2022 / ARRIVED_SCENE >= LEFT_SCENE: 910,286 violations / 918,547 testable (99.10%)
- 2022 / LEFT_SCENE >= ARRIVED_DEST: 838,995 violations / 846,959 testable (99.06%)
- 2023 / NOTIFIED >= ARRIVED_SCENE: 444,841 violations / 449,099 testable (99.05%)
- 2023 / ARRIVED_SCENE >= LEFT_SCENE: 358,563 violations / 361,704 testable (99.13%)
- 2023 / LEFT_SCENE >= ARRIVED_DEST: 330,110 violations / 333,313 testable (99.04%)
- 2024 / NOTIFIED >= ARRIVED_SCENE: 1,568,302 violations / 1,582,828 testable (99.08%)
- 2024 / ARRIVED_SCENE >= LEFT_SCENE: 970,012 violations / 978,971 testable (99.08%)
- 2024 / LEFT_SCENE >= ARRIVED_DEST: 878,978 violations / 888,200 testable (98.96%)
- 2025 / NOTIFIED >= ARRIVED_SCENE: 1,499,196 violations / 1,514,594 testable (98.98%)
- 2025 / ARRIVED_SCENE >= LEFT_SCENE: 1,011,230 violations / 1,020,564 testable (99.09%)
- 2025 / LEFT_SCENE >= ARRIVED_DEST: 906,552 violations / 916,565 testable (98.91%)

### Check 3: Duration vs. Timestamp Consistency (pre-2022)
- 2014 / PROVIDER_TO_SCENE_MINS: 174,643 mismatches / 393,342 testable (44.40%)
- 2014 / PROVIDER_TO_DESTINATION_MINS: 321,543 mismatches / 324,428 testable (99.11%)
- 2015 / PROVIDER_TO_SCENE_MINS: 213,157 mismatches / 483,567 testable (44.08%)
- 2015 / PROVIDER_TO_DESTINATION_MINS: 407,615 mismatches / 411,650 testable (99.02%)
- 2016 / PROVIDER_TO_SCENE_MINS: 258,462 mismatches / 596,518 testable (43.33%)
- 2016 / PROVIDER_TO_DESTINATION_MINS: 488,773 mismatches / 493,041 testable (99.13%)
- 2017 / PROVIDER_TO_SCENE_MINS: 269,377 mismatches / 560,379 testable (48.07%)
- 2017 / PROVIDER_TO_DESTINATION_MINS: 454,673 mismatches / 458,955 testable (99.07%)
- 2018 / PROVIDER_TO_SCENE_MINS: 146,204 mismatches / 328,935 testable (44.45%)
- 2018 / PROVIDER_TO_DESTINATION_MINS: 183,303 mismatches / 186,132 testable (98.48%)
- 2019 / PROVIDER_TO_SCENE_MINS: 408,545 mismatches / 878,421 testable (46.51%)
- 2019 / PROVIDER_TO_DESTINATION_MINS: 729,949 mismatches / 734,819 testable (99.34%)
- 2020 / PROVIDER_TO_SCENE_MINS: 471,501 mismatches / 1,038,437 testable (45.40%)
- 2020 / PROVIDER_TO_DESTINATION_MINS: 801,429 mismatches / 806,463 testable (99.38%)
- 2021 / PROVIDER_TO_SCENE_MINS: 524,509 mismatches / 1,189,364 testable (44.10%)
- 2021 / PROVIDER_TO_DESTINATION_MINS: 879,588 mismatches / 884,936 testable (99.40%)

### Interpretation and rule changes

- **Check 1 (Stubs):** 7 stubs across 10.5M rows (<0.01%). Not material. No quarantine rule change.
- **Check 2 (Ordering, 2022+):** 99% violation rate is an artifact of midnight truncation -- all unit timestamps become identical midnight values, making ordering checks meaningless. Timestamp ordering validation must be restricted to 2014-2021 only. Do not flag 2022+ ordering violations as DQ errors.
- **Check 2 (Ordering, 2014-2021):** Real violation rates are 1.88-4.93% for NOTIFIED vs. ARRIVED_SCENE (highest), 0.49-1.65% for ARRIVED_SCENE vs. LEFT_SCENE, 0.64-2.41% for LEFT_SCENE vs. ARRIVED_DEST. These are data entry errors. The ETL will null violating timestamps (field-level repair) rather than quarantine the row.
- **Check 3 (Duration mismatch):** PROVIDER_TO_DESTINATION_MINS mismatches at 98-99% -- the field does NOT measure PATIENT_ARRIVED_DESTINATION_DT - UNIT_NOTIFIED_BY_DISPATCH_DT. Reference point unknown. PROVIDER_TO_SCENE_MINS at ~44-48% mismatch also suggests a different start reference. Load stored values as-is; derivation-based validation is not applicable.
- **Check 4 (Provider combos):** 5 combinations cover ~80% of records. "EMT-Paramedic" and "2009 Paramedic" appear as separate values for the same certification level under different NEMSIS code versions -- confirms code-list drift. 16 rare combos (<0.1%) are flagged for manual review.
- **Check 5 (County-year):** "ST JOSEPH" (2014-2022) and "ST. JOSEPH" (2023-2025) are the same county. **ETL must normalize county names (strip periods, uppercase, trim) before dimension lookup.** Rule 2 in dq-rules.md amended accordingly.
