# Session 1.5 Complex DQ Checks

Generated: 2026-06-22 19:24
Source: `_Claude/INPUTS/ems_runs_*.csv` (13 files)


---

## Check 1 -- Stub Records

Rows where every column except INCIDENT_DT, INCIDENT_COUNTY, NALOXONE_GIVEN_FLG,
and MEDICATION_GIVEN_OTHER_FLG is null. Rows with either flag = 1 are not stubs.

| Year | Total Rows | Stubs | Stub % |
|------|----------:|------:|-------:|
| 2014 | 418,661 | 0 | 0.00% |
| 2015 | 519,648 | 1 | 0.00% |
| 2016 | 645,016 | 0 | 0.00% |
| 2017 | 594,146 | 2 | 0.00% |
| 2018 | 364,945 | 0 | 0.00% |
| 2019 | 905,603 | 0 | 0.00% |
| 2020 | 1,079,141 | 0 | 0.00% |
| 2021 | 1,243,403 | 0 | 0.00% |
| 2022 | 1,141,648 | 0 | 0.00% |
| 2023 | 461,217 | 0 | 0.00% |
| 2024 | 1,613,800 | 4 | 0.00% |
| 2025 | 1,545,309 | 0 | 0.00% |

---

## Check 2 -- Timestamp Ordering Violations

A violation is flagged when the earlier timestamp >= the later timestamp for a given pair.
Only rows where both timestamps are non-null are tested. UNIT_ARRIVED_TO_PATIENT_DT excluded.

| Year | Pair | Testable Rows | Violations | Violation % |
|------|------|-------------:|----------:|------------:|
| 2014 | NOTIFIED >= ARRIVED_SCENE | 399,260 | 16,822 | 4.21% |
| 2014 | ARRIVED_SCENE >= LEFT_SCENE | 344,263 | 4,728 | 1.37% |
| 2014 | LEFT_SCENE >= ARRIVED_DEST | 324,559 | 7,807 | 2.41% |
| 2015 | NOTIFIED >= ARRIVED_SCENE | 496,921 | 24,519 | 4.93% |
| 2015 | ARRIVED_SCENE >= LEFT_SCENE | 446,169 | 5,994 | 1.34% |
| 2015 | LEFT_SCENE >= ARRIVED_DEST | 411,751 | 9,643 | 2.34% |
| 2016 | NOTIFIED >= ARRIVED_SCENE | 612,136 | 23,434 | 3.83% |
| 2016 | ARRIVED_SCENE >= LEFT_SCENE | 531,510 | 5,444 | 1.02% |
| 2016 | LEFT_SCENE >= ARRIVED_DEST | 493,209 | 7,072 | 1.43% |
| 2017 | NOTIFIED >= ARRIVED_SCENE | 568,471 | 20,424 | 3.59% |
| 2017 | ARRIVED_SCENE >= LEFT_SCENE | 492,050 | 5,467 | 1.11% |
| 2017 | LEFT_SCENE >= ARRIVED_DEST | 459,027 | 5,857 | 1.28% |
| 2018 | NOTIFIED >= ARRIVED_SCENE | 330,608 | 15,164 | 4.59% |
| 2018 | ARRIVED_SCENE >= LEFT_SCENE | 228,399 | 3,768 | 1.65% |
| 2018 | LEFT_SCENE >= ARRIVED_DEST | 186,317 | 3,559 | 1.91% |
| 2019 | NOTIFIED >= ARRIVED_SCENE | 879,567 | 21,951 | 2.50% |
| 2019 | ARRIVED_SCENE >= LEFT_SCENE | 767,420 | 5,970 | 0.78% |
| 2019 | LEFT_SCENE >= ARRIVED_DEST | 735,047 | 5,801 | 0.79% |
| 2020 | NOTIFIED >= ARRIVED_SCENE | 1,039,531 | 21,347 | 2.05% |
| 2020 | ARRIVED_SCENE >= LEFT_SCENE | 864,292 | 4,240 | 0.49% |
| 2020 | LEFT_SCENE >= ARRIVED_DEST | 806,830 | 5,159 | 0.64% |
| 2021 | NOTIFIED >= ARRIVED_SCENE | 1,190,279 | 22,425 | 1.88% |
| 2021 | ARRIVED_SCENE >= LEFT_SCENE | 955,542 | 5,205 | 0.54% |
| 2021 | LEFT_SCENE >= ARRIVED_DEST | 885,221 | 6,277 | 0.71% |
| 2022 | NOTIFIED >= ARRIVED_SCENE | 1,111,199 | 1,099,436 | 98.94% |
| 2022 | ARRIVED_SCENE >= LEFT_SCENE | 918,547 | 910,286 | 99.10% |
| 2022 | LEFT_SCENE >= ARRIVED_DEST | 846,959 | 838,995 | 99.06% |
| 2023 | NOTIFIED >= ARRIVED_SCENE | 449,099 | 444,841 | 99.05% |
| 2023 | ARRIVED_SCENE >= LEFT_SCENE | 361,704 | 358,563 | 99.13% |
| 2023 | LEFT_SCENE >= ARRIVED_DEST | 333,313 | 330,110 | 99.04% |
| 2024 | NOTIFIED >= ARRIVED_SCENE | 1,582,828 | 1,568,302 | 99.08% |
| 2024 | ARRIVED_SCENE >= LEFT_SCENE | 978,971 | 970,012 | 99.08% |
| 2024 | LEFT_SCENE >= ARRIVED_DEST | 888,200 | 878,978 | 98.96% |
| 2025 | NOTIFIED >= ARRIVED_SCENE | 1,514,594 | 1,499,196 | 98.98% |
| 2025 | ARRIVED_SCENE >= LEFT_SCENE | 1,020,564 | 1,011,230 | 99.09% |
| 2025 | LEFT_SCENE >= ARRIVED_DEST | 916,565 | 906,552 | 98.91% |

---

## Check 3 -- Duration vs. Timestamp Consistency (Pre-2022 Only)

Mismatch = |stored_minutes - derived_minutes| > 1.
2022+ files excluded (timestamps midnight-truncated; comparison is invalid).

| Year | Field | Testable Rows | Mismatches | Mismatch % |
|------|-------|-------------:|----------:|----------:|
| 2014 | PROVIDER_TO_SCENE_MINS | 393,342 | 174,643 | 44.40% |
| 2014 | PROVIDER_TO_DESTINATION_MINS | 324,428 | 321,543 | 99.11% |
| 2015 | PROVIDER_TO_SCENE_MINS | 483,567 | 213,157 | 44.08% |
| 2015 | PROVIDER_TO_DESTINATION_MINS | 411,650 | 407,615 | 99.02% |
| 2016 | PROVIDER_TO_SCENE_MINS | 596,518 | 258,462 | 43.33% |
| 2016 | PROVIDER_TO_DESTINATION_MINS | 493,041 | 488,773 | 99.13% |
| 2017 | PROVIDER_TO_SCENE_MINS | 560,379 | 269,377 | 48.07% |
| 2017 | PROVIDER_TO_DESTINATION_MINS | 458,955 | 454,673 | 99.07% |
| 2018 | PROVIDER_TO_SCENE_MINS | 328,935 | 146,204 | 44.45% |
| 2018 | PROVIDER_TO_DESTINATION_MINS | 186,132 | 183,303 | 98.48% |
| 2019 | PROVIDER_TO_SCENE_MINS | 878,421 | 408,545 | 46.51% |
| 2019 | PROVIDER_TO_DESTINATION_MINS | 734,819 | 729,949 | 99.34% |
| 2020 | PROVIDER_TO_SCENE_MINS | 1,038,437 | 471,501 | 45.40% |
| 2020 | PROVIDER_TO_DESTINATION_MINS | 806,463 | 801,429 | 99.38% |
| 2021 | PROVIDER_TO_SCENE_MINS | 1,189,364 | 524,509 | 44.10% |
| 2021 | PROVIDER_TO_DESTINATION_MINS | 884,936 | 879,588 | 99.40% |

---

## Check 4 -- PROVIDER_TYPE Combination Frequency

All years combined. Sorted descending by count. Flag = combination < 0.1% of total rows.

Total rows across all years: 10,532,537

| PROVIDER_TYPE_STRUCTURE | PROVIDER_TYPE_SERVICE | PROVIDER_TYPE_SERVICE_LEVEL | Count | % | Flag |
|------------------------|----------------------|----------------------------|------:|--:|:----:|
| Fire Department | 911 Response (Scene) with Transport Capability | 2009 Paramedic | 2,365,156 | 22.456% |  |
| Governmental, Non-Fire | 911 Response (Scene) with Transport Capability | 2009 Paramedic | 2,354,421 | 22.354% |  |
| Hospital | 911 Response (Scene) with Transport Capability | 2009 Paramedic | 1,635,037 | 15.524% |  |
| Private, Nonhospital | Medical Transport (Convalescent, Interfacility Transfer Hospital and Nursing Home) | 2009 Paramedic | 1,129,145 | 10.721% |  |
| Private, Nonhospital | 911 Response (Scene) with Transport Capability | 2009 Paramedic | 831,986 | 7.899% |  |
| Fire Department | 911 Response (Scene) without Transport Capability | 2009 Paramedic | 413,346 | 3.924% |  |
| Hospital | Medical Transport (Convalescent, Interfacility Transfer Hospital and Nursing Home) | 2009 Paramedic | 280,194 | 2.660% |  |
| Private, Nonhospital | Critical Care (Ground) | 2009 Paramedic | 205,181 | 1.948% |  |
| Private, Nonhospital | 911 Response (Scene) with Transport Capability | 2009 Emergency Medical Technician (EMT) | 164,672 | 1.563% |  |
| Private, Nonhospital | Medical Transport (Convalescent, Interfacility Transfer Hospital and Nursing Home) | 2009 Emergency Medical Technician (EMT) | 145,369 | 1.380% |  |
| Private, Nonhospital | 911 Response (Scene) with Transport Capability | EMT-Paramedic | 116,797 | 1.109% |  |
| Fire Department | 911 Response (Scene) with Transport Capability | 2009 Emergency Medical Technician (EMT) | 103,408 | 0.982% |  |
| Governmental, Non-Fire | 911 Response (Scene) with Transport Capability | 2009 Emergency Medical Technician (EMT) | 89,150 | 0.846% |  |
| Hospital | 911 Response (Scene) with Transport Capability | EMT-Paramedic | 84,199 | 0.799% |  |
| Private, Nonhospital | Medical Transport (Convalescent, Interfacility Transfer Hospital and Nursing Home) | _NULL_ | 70,478 | 0.669% |  |
| Hospital | Air Medical | Nurse | 60,606 | 0.575% |  |
| Governmental, Non-Fire | 911 Response (Scene) with Transport Capability | _NULL_ | 55,787 | 0.530% |  |
| _NULL_ | _NULL_ | _NULL_ | 53,539 | 0.508% |  |
| Hospital | 911 Response (Scene) with Transport Capability | _NULL_ | 46,936 | 0.446% |  |
| Fire Department | 911 Response (Scene) without Transport Capability | 2009 Emergency Medical Technician (EMT) | 38,795 | 0.368% |  |
| Private, Nonhospital | Medical Transport (Convalescent, Interfacility Transfer Hospital and Nursing Home) | EMT-Paramedic | 35,681 | 0.339% |  |
| Fire Department | 911 Response (Scene) with Transport Capability | 2009 Advanced Emergency Medical Technician (AEMT) | 30,560 | 0.290% |  |
| Private, Nonhospital | Air Medical | Nurse | 27,674 | 0.263% |  |
| Hospital | Critical Care (Ground) | 2009 Paramedic | 26,854 | 0.255% |  |
| Private, Nonhospital | Air Medical | 2009 Paramedic | 22,469 | 0.213% |  |
| Private, Nonhospital | Critical Care (Ground) | EMT-Paramedic | 19,710 | 0.187% |  |
| Private, Nonhospital | 911 Response (Scene) with Transport Capability | 2009 Advanced Emergency Medical Technician (AEMT) | 18,669 | 0.177% |  |
| Governmental, Non-Fire | Medical Transport (Convalescent, Interfacility Transfer Hospital and Nursing Home) | 2009 Paramedic | 15,295 | 0.145% |  |
| Community, Non-Profit | 911 Response (Scene) with Transport Capability | EMT-Intermediate | 12,492 | 0.119% |  |
| Hospital | Medical Transport (Convalescent, Interfacility Transfer Hospital and Nursing Home) | 2009 Emergency Medical Technician (EMT) | 11,925 | 0.113% |  |
| Governmental, Non-Fire | 911 Response (Scene) with Transport Capability | 2009 Advanced Emergency Medical Technician (AEMT) | 11,145 | 0.106% |  |
| Hospital | Air Medical | 2009 Paramedic | 8,813 | 0.084% | <0.1% |
| Fire Department | 911 Response (Scene) without Transport Capability | 2009 Emergency Medical Responder (EMR) | 8,132 | 0.077% | <0.1% |
| Private, Nonhospital | _NULL_ | 2009 Advanced Emergency Medical Technician (AEMT) | 6,023 | 0.057% | <0.1% |
| Governmental, Non-Fire | Medical Transport (Convalescent, Interfacility Transfer Hospital and Nursing Home) | 2009 Advanced Emergency Medical Technician (AEMT) | 4,482 | 0.043% | <0.1% |
| Hospital | 911 Response (Scene) without Transport Capability | 2009 Paramedic | 4,274 | 0.041% | <0.1% |
| Governmental, Non-Fire | 911 Response (Scene) with Transport Capability | EMT-Paramedic | 4,180 | 0.040% | <0.1% |
| Private, Nonhospital | 911 Response (Scene) with Transport Capability | Nurse | 3,274 | 0.031% | <0.1% |
| Hospital | _NULL_ | EMT-Paramedic | 2,448 | 0.023% | <0.1% |
| Fire Department | 911 Response (Scene) without Transport Capability | 2009 Advanced Emergency Medical Technician (AEMT) | 2,211 | 0.021% | <0.1% |
| Private, Nonhospital | 911 Response (Scene) with Transport Capability | EMT-Basic | 1,756 | 0.017% | <0.1% |
| Fire Department | 911 Response (Scene) without Transport Capability | _NULL_ | 1,689 | 0.016% | <0.1% |
| Private, Nonhospital | 911 Response (Scene) with Transport Capability | _NULL_ | 1,535 | 0.015% | <0.1% |
| Community, Non-Profit | 911 Response (Scene) with Transport Capability | EMT-Basic | 1,222 | 0.012% | <0.1% |
| Private, Nonhospital | Rescue | 2009 Emergency Medical Technician (EMT) | 1,199 | 0.011% | <0.1% |
| Private, Nonhospital | _NULL_ | _NULL_ | 770 | 0.007% | <0.1% |
| Hospital | Air Medical | EMT-Paramedic | 718 | 0.007% | <0.1% |
| Governmental, Non-Fire | 911 Response (Scene) without Transport Capability | 2009 Paramedic | 672 | 0.006% | <0.1% |
| Private, Nonhospital | 911 Response (Scene) without Transport Capability | 2009 Emergency Medical Technician (EMT) | 671 | 0.006% | <0.1% |
| Governmental, Non-Fire | 911 Response (Scene) without Transport Capability | 2009 Emergency Medical Technician (EMT) | 669 | 0.006% | <0.1% |
| Hospital | Rescue | 2009 Paramedic | 598 | 0.006% | <0.1% |
| Fire Department | 911 Response (Scene) with Transport Capability | EMT-Paramedic | 344 | 0.003% | <0.1% |
| Hospital | Critical Care (Ground) | Nurse | 140 | 0.001% | <0.1% |
| Fire Department | 911 Response (Scene) without Transport Capability | EMT-Basic | 38 | 0.000% | <0.1% |
| Fire Department | Rescue | 2009 Emergency Medical Responder (EMR) | 2 | 0.000% | <0.1% |
| Fire Department | Rescue | 2009 Emergency Medical Technician (EMT) | 1 | 0.000% | <0.1% |

---

## Check 5 -- County-Year Event Volume Distribution

Row counts per (INCIDENT_COUNTY, year). Zero-count county-years are flagged.

| County | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|--------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| ADAMS | 2,416 | 2,508 | 2,627 | 3,422 | 1,288 | 2,540 | 2,842 | 3,209 | 2,669 | 1,228 | 4,887 | 4,236 |
| ALLEN | 11,474 | 12,410 | 7,350 | 10,154 | 10,675 | 46,774 | 53,117 | 58,357 | 49,121 | 16,592 | 61,586 | 72,652 |
| BARTHOLOMEW | 9,873 | 11,002 | 11,345 | 9,497 | 4,058 | 7,486 | 10,703 | 13,272 | 14,882 | 5,767 | 20,282 | 16,869 |
| BENTON | 28 | 695 | 773 | 789 | 378 | 877 | 1,309 | 1,523 | 1,569 | 798 | 2,052 | 1,878 |
| BLACKFORD | 343 | 1,246 | 1,051 | 118 | 679 | 1,557 | 1,612 | 1,766 | 1,532 | 285 | 2,427 | 2,062 |
| BOONE | 4,198 | 6,562 | 6,624 | 2,736 | 1,935 | 6,104 | 7,118 | 7,320 | 7,728 | 2,972 | 9,597 | 9,005 |
| BROWN | 1,571 | 1,937 | 1,793 | 1,582 | 701 | 986 | 1,452 | 1,522 | 1,351 | 422 | 2,445 | 1,975 |
| CARROLL | 1,615 | 1,679 | 1,969 | 1,607 | 635 | 1,387 | 1,814 | 1,889 | 1,711 | 713 | 2,251 | 2,292 |
| CASS | 203 | 338 | 419 | 360 | 2,073 | 3,117 | 4,607 | 5,136 | 5,763 | 2,662 | 9,636 | 9,936 |
| CLARK | 93 | 108 | 1,947 | 554 | 50 | 1,560 | 17,631 | 21,434 | 20,624 | 7,758 | 19,486 | 23,886 |
| CLAY | 1,737 | 2,951 | 3,420 | 3,488 | 913 | 2,873 | 3,620 | 4,119 | 4,292 | 1,766 | 4,273 | 4,397 |
| CLINTON | 4,095 | 3,928 | 4,418 | 4,136 | 2,161 | 3,580 | 4,944 | 5,068 | 4,947 | 1,846 | 6,994 | 5,768 |
| CRAWFORD | 1,219 | 600 | 1,301 | 1,544 | 349 | 1,064 | 1,154 | 1,432 | 1,181 | 494 | 1,331 | 1,387 |
| DAVIESS | 564 | 952 | 1,014 | 1,513 | 1,443 | 3,859 | 4,556 | 4,713 | 4,717 | 1,748 | 6,714 | 7,465 |
| DEARBORN | 802 | 3,567 | 5,176 | 6,729 | 3,916 | 6,185 | 6,163 | 7,112 | 6,589 | 3,022 | 10,873 | 8,072 |
| DECATUR | 1,009 | 3,962 | 4,243 | 4,593 | 2,662 | 5,264 | 4,274 | 3,676 | 2,841 | 1,753 | 2,543 | 2,104 |
| DEKALB | 60 | 1,793 | 1,944 | 76 | 144 | 3,739 | 4,456 | 5,051 | 5,127 | 2,174 | 9,510 | 9,389 |
| DELAWARE | 6,502 | 15,314 | 14,762 | 13,640 | 5,306 | 26,504 | 31,475 | 33,565 | 26,102 | 9,273 | 43,669 | 41,607 |
| DUBOIS | 4,253 | 4,354 | 3,022 | 4,468 | 947 | 2,969 | 3,961 | 6,140 | 6,244 | 2,406 | 9,659 | 7,738 |
| ELKHART | 6,132 | 8,061 | 9,889 | 10,949 | 5,696 | 18,807 | 18,893 | 22,095 | 20,165 | 8,295 | 29,862 | 37,234 |
| FAYETTE | 3,516 | 3,379 | 4,642 | 5,143 | 1,995 | 3,936 | 5,763 | 7,178 | 6,782 | 3,110 | 9,714 | 7,112 |
| FLOYD | 21 | 145 | 4,715 | 2,489 | 428 | 1,509 | 9,556 | 15,045 | 13,367 | 3,686 | 11,453 | 15,194 |
| FOUNTAIN | 1,769 | 1,904 | 1,872 | 1,938 | 554 | 2,037 | 2,213 | 2,468 | 2,245 | 999 | 3,681 | 2,721 |
| FRANKLIN | 304 | 273 | 938 | 2,834 | 1,394 | 4,345 | 3,529 | 3,358 | 3,242 | 1,282 | 2,599 | 2,587 |
| FULTON | 1,970 | 2,123 | 2,396 | 3,484 | 1,601 | 2,232 | 2,651 | 2,973 | 3,193 | 1,238 | 4,596 | 4,429 |
| GIBSON | 4,205 | 4,484 | 4,417 | 4,135 | 2,064 | 4,035 | 4,398 | 4,803 | 4,743 | 1,987 | 8,716 | 9,114 |
| GRANT | 7,771 | 11,062 | 11,288 | 10,724 | 5,886 | 13,504 | 18,636 | 20,252 | 18,830 | 6,850 | 22,308 | 18,447 |
| GREENE | 3,358 | 3,048 | 1,025 | 943 | 1,226 | 3,576 | 4,247 | 4,879 | 4,676 | 1,800 | 7,938 | 5,782 |
| HAMILTON | 15,618 | 18,098 | 22,299 | 17,571 | 9,726 | 24,090 | 25,438 | 28,185 | 30,224 | 11,915 | 50,037 | 47,259 |
| HANCOCK | 6,057 | 7,119 | 7,772 | 7,592 | 4,188 | 9,869 | 8,914 | 9,062 | 9,671 | 3,581 | 14,698 | 14,130 |
| HARRISON | 58 | 103 | 169 | 128 | 1,003 | 6,453 | 6,902 | 7,094 | 7,118 | 2,784 | 12,303 | 11,483 |
| HENDRICKS | 10,624 | 15,210 | 17,098 | 14,575 | 6,755 | 16,610 | 20,236 | 22,426 | 22,151 | 9,597 | 35,308 | 32,967 |
| HENRY | 4,804 | 10,725 | 11,257 | 11,743 | 4,781 | 8,621 | 9,756 | 10,944 | 10,435 | 4,023 | 15,867 | 15,182 |
| HOWARD | 342 | 5,476 | 9,500 | 10,876 | 4,675 | 12,159 | 16,115 | 19,000 | 19,633 | 7,703 | 24,541 | 21,855 |
| HUNTINGTON | 4,322 | 4,425 | 4,921 | 7,757 | 2,674 | 5,720 | 6,402 | 6,681 | 6,323 | 2,492 | 8,384 | 9,943 |
| JACKSON | 243 | 900 | 6,852 | 7,549 | 2,320 | 6,445 | 6,250 | 6,603 | 7,381 | 2,633 | 8,301 | 7,053 |
| JASPER | 2,990 | 1,932 | 1,654 | 1,541 | 1,216 | 2,237 | 3,343 | 4,314 | 3,908 | 2,019 | 5,999 | 5,153 |
| JAY | 1,923 | 2,076 | 2,424 | 124 | 1,019 | 2,406 | 2,683 | 3,180 | 3,130 | 1,009 | 4,470 | 4,236 |
| JEFFERSON | 6,772 | 7,453 | 7,049 | 7,324 | 4,173 | 7,176 | 6,699 | 7,427 | 7,090 | 2,706 | 7,821 | 7,561 |
| JENNINGS | 1,027 | 1,102 | 956 | 369 | 835 | 3,226 | 3,306 | 3,570 | 3,637 | 1,345 | 3,862 | 3,544 |
| JOHNSON | 8,898 | 15,102 | 16,023 | 14,228 | 5,414 | 19,731 | 20,883 | 25,001 | 23,078 | 9,068 | 30,988 | 29,631 |
| KNOX | 1,510 | 2,871 | 3,102 | 2,225 | 462 | 4,149 | 5,937 | 6,998 | 6,686 | 2,817 | 10,585 | 9,441 |
| KOSCIUSKO | 7,537 | 8,104 | 8,416 | 12,633 | 5,966 | 8,719 | 10,656 | 11,688 | 11,663 | 4,706 | 16,038 | 14,004 |
| LAGRANGE | 2,314 | 2,551 | 2,465 | 3,355 | 1,442 | 2,508 | 2,951 | 3,025 | 2,957 | 1,302 | 5,898 | 5,167 |
| LAKE | 9,194 | 14,769 | 26,112 | 36,351 | 21,827 | 96,881 | 103,072 | 125,034 | 113,579 | 42,246 | 113,514 | 100,516 |
| LAPORTE | 2,060 | 1,930 | 1,998 | 1,670 | 4,495 | 10,766 | 15,513 | 17,274 | 18,072 | 7,435 | 21,664 | 16,773 |
| LAWRENCE | 3,187 | 3,355 | 3,210 | 290 | 272 | 5,717 | 7,388 | 7,362 | 2,335 | 1,714 | 12,683 | 11,283 |
| MADISON | 4,262 | 10,099 | 14,545 | 16,589 | 5,289 | 20,298 | 21,973 | 21,364 | 22,366 | 8,957 | 31,408 | 31,311 |
| MARION | 95,401 | 79,512 | 155,812 | 92,505 | 119,724 | 201,533 | 246,446 | 319,031 | 277,396 | 119,186 | 418,194 | 394,330 |
| MARSHALL | 528 | 1,907 | 2,384 | 3,130 | 1,725 | 4,098 | 5,208 | 4,815 | 4,340 | 1,591 | 6,237 | 9,790 |
| MARTIN | 69 | 66 | 64 | 71 | 34 | 607 | 1,184 | 1,272 | 1,092 | 518 | 1,659 | 1,730 |
| MIAMI | 296 | 367 | 559 | 1,226 | 2,210 | 4,853 | 5,209 | 6,169 | 5,873 | 2,260 | 6,711 | 6,714 |
| MONROE | 13,690 | 15,069 | 5,722 | 391 | 344 | 12,315 | 16,053 | 16,120 | 3,757 | 2,752 | 31,711 | 28,667 |
| MONTGOMERY | 139 | 316 | 468 | 287 | 2,823 | 6,704 | 7,026 | 8,300 | 7,452 | 2,973 | 10,449 | 8,458 |
| MORGAN | 1,054 | 5,238 | 6,811 | 6,742 | 2,405 | 6,819 | 10,372 | 11,418 | 11,128 | 4,386 | 16,817 | 14,946 |
| NEWTON | 181 | 49 | 331 | 400 | 17 | 446 | 588 | 1,564 | 1,569 | 587 | 1,802 | 138 |
| NOBLE | 3,345 | 4,992 | 450 | 2,055 | 3,227 | 5,347 | 5,709 | 5,974 | 6,183 | 2,351 | 11,045 | 9,105 |
| OHIO | 114 | 339 | 809 | 889 | 260 | 568 | 699 | 877 | 862 | 395 | 1,419 | 1,232 |
| ORANGE | 1,364 | 1,407 | 322 | 377 | 140 | 2,553 | 3,679 | 3,604 | 807 | 613 | 5,798 | 4,723 |
| OWEN | 193 | 277 | 156 | 117 | 918 | 1,926 | 2,512 | 2,961 | 2,653 | 1,086 | 2,689 | 2,563 |
| PARKE | 35 | 165 | 142 | 1,049 | 83 | 1,107 | 1,327 | 1,501 | 1,347 | 614 | 2,628 | 2,730 |
| PERRY | 1,447 | 2,147 | 2,164 | 2,732 | 1,281 | 2,999 | 3,011 | 2,939 | 2,603 | 909 | 2,798 | 3,040 |
| PIKE | 1,187 | 1,326 | 1,302 | 1,440 | 539 | 1,341 | 1,458 | 1,750 | 1,657 | 606 | 2,616 | 2,746 |
| PORTER | 4,455 | 9,762 | 13,257 | 21,934 | 5,744 | 16,799 | 22,606 | 24,539 | 22,705 | 11,246 | 32,890 | 33,670 |
| POSEY | 2,141 | 2,326 | 2,011 | 1,908 | 883 | 1,709 | 2,615 | 2,661 | 2,922 | 1,222 | 4,668 | 3,529 |
| PULASKI | 109 | 918 | 1,875 | 532 | 906 | 1,741 | 1,857 | 1,801 | 1,700 | 770 | 2,854 | 2,445 |
| PUTNAM | 1,110 | 2,868 | 626 | 482 | 1,883 | 4,329 | 4,515 | 5,501 | 5,061 | 1,927 | 7,421 | 7,317 |
| RANDOLPH | 1,395 | 993 | 1,627 | 1,772 | 1,054 | 2,718 | 3,689 | 3,836 | 3,466 | 1,407 | 4,648 | 5,230 |
| RIPLEY | 4,822 | 3,325 | 5,974 | 5,726 | 3,700 | 3,831 | 4,699 | 5,464 | 5,594 | 2,116 | 6,506 | 6,050 |
| RUSH | 1,779 | 1,574 | 2,356 | 2,577 | 1,287 | 1,598 | 1,967 | 2,333 | 2,192 | 887 | 2,437 | 2,488 |
| SCOTT | 2,141 | 4,586 | 4,981 | 4,706 | 2,534 | 3,188 | 4,308 | 4,745 | 4,740 | 2,012 | 7,608 | 7,299 |
| SHELBY | 3,642 | 4,553 | 4,046 | 3,581 | 2,026 | 6,910 | 6,499 | 6,771 | 6,791 | 2,666 | 9,523 | 8,660 |
| SPENCER | 2,005 | 2,152 | 2,186 | 3,115 | 922 | 2,080 | 2,312 | 2,520 | 2,379 | 971 | 2,364 | 2,168 |
| ST JOSEPH | 15,236 | 25,038 | 28,912 | 24,145 | 10,572 | 34,909 | 36,130 | 37,090 | 35,728 | **0** | **0** | **0** |
| ST. JOSEPH | **0** | **0** | **0** | **0** | **0** | **0** | **0** | **0** | **0** | 15,414 | 41,197 | 41,372 |
| STARKE | 75 | 752 | 627 | 1,583 | 698 | 1,008 | 512 | 1,019 | 1,052 | 354 | 2,742 | 3,229 |
| STEUBEN | 3,125 | 3,422 | 3,419 | 4,754 | 1,843 | 3,140 | 3,607 | 3,714 | 3,979 | 1,554 | 3,832 | 2,824 |
| SULLIVAN | 3,188 | 3,738 | 3,854 | 2,594 | 1,094 | 2,171 | 2,444 | 2,607 | 2,434 | 967 | 3,984 | 3,833 |
| SWITZERLAND | 1,200 | 1,157 | 1,126 | 996 | 94 | 725 | 944 | 1,024 | 1,116 | 493 | 1,649 | 1,432 |
| TIPPECANOE | 21,554 | 20,551 | 22,874 | 25,815 | 13,751 | 21,005 | 28,874 | 31,323 | 31,567 | 12,683 | 44,437 | 42,443 |
| TIPTON | 1,304 | 1,678 | 1,469 | 1,513 | 596 | 1,459 | 1,644 | 1,902 | 1,816 | 592 | 2,807 | 2,604 |
| UNION | 106 | 153 | 39 | 198 | 25 | 87 | 357 | 763 | 764 | 338 | 1,029 | 1,011 |
| VANDERBURGH | 22,924 | 25,178 | 25,861 | 26,215 | 2,431 | 28,671 | 31,376 | 32,552 | 29,793 | 11,547 | 35,787 | 36,772 |
| VERMILLION | 67 | 834 | 1,053 | 1,269 | 280 | 2,053 | 2,256 | 2,494 | 2,295 | 808 | 3,179 | 4,022 |
| VIGO | 7,772 | 15,234 | 20,261 | 19,745 | 8,022 | 15,252 | 19,184 | 17,779 | 20,356 | 8,213 | 31,784 | 31,258 |
| WABASH | 1,715 | 2,518 | 3,103 | 4,038 | 2,074 | 5,295 | 5,728 | 6,082 | 6,033 | 2,498 | 8,629 | 8,268 |
| WARREN | 1,156 | 1,224 | 1,209 | 1,140 | 783 | 1,343 | 1,377 | 1,364 | 1,371 | 531 | 1,642 | 1,692 |
| WARRICK | 5,212 | 5,770 | 5,987 | 7,292 | 3,304 | 9,290 | 9,423 | 9,747 | 9,421 | 3,431 | 15,215 | 17,791 |
| WASHINGTON | 163 | 2,850 | 3,329 | 3,306 | 1,574 | 2,446 | 3,441 | 3,510 | 3,213 | 1,368 | 3,687 | 3,461 |
| WAYNE | 9,059 | 10,993 | 12,529 | 13,006 | 6,324 | 12,690 | 14,922 | 15,768 | 15,349 | 6,750 | 24,720 | 21,020 |
| WELLS | 1,360 | 2,077 | 2,135 | 1,200 | 881 | 1,678 | 2,268 | 2,364 | 3,402 | 1,269 | 4,676 | 4,136 |
| WHITE | 2,194 | 2,203 | 1,462 | 1,508 | 1,881 | 3,469 | 3,424 | 3,524 | 3,487 | 1,261 | 6,145 | 6,233 |
| WHITLEY | 3,009 | 3,337 | 3,480 | 4,822 | 1,940 | 4,031 | 4,067 | 4,592 | 4,448 | 2,069 | 7,573 | 8,197 |
| _NULL_ | 757 | 922 | 1,650 | 1,128 | 420 | 575 | 504 | 132 | 85 | 48 | 143 | 113 |

**Zero-count county-years:**

- ST JOSEPH / 2023
- ST JOSEPH / 2024
- ST JOSEPH / 2025
- ST. JOSEPH / 2014
- ST. JOSEPH / 2015
- ST. JOSEPH / 2016
- ST. JOSEPH / 2017
- ST. JOSEPH / 2018
- ST. JOSEPH / 2019
- ST. JOSEPH / 2020
- ST. JOSEPH / 2021
- ST. JOSEPH / 2022