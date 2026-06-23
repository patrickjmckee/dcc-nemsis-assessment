#!/usr/bin/env python3
"""Session 1.5 Complex DQ Checks -- Indiana EMS Data (2014-2025)

Quick scan (not a full re-profile).
Checks:
  1. Stub records
  2. Timestamp ordering violations
  3. Duration vs. timestamp consistency (pre-2022 only)
  4. PROVIDER_TYPE combination frequency
  5. County-year event volume distribution
"""

import glob
import re
from collections import Counter
from datetime import datetime

import pandas as pd

INPUTS_GLOB = "_Claude/INPUTS/ems_runs_*.csv"
OUTPUT_MD = "_Claude/OUTPUTS/dq_complex_checks.md"
DQ_APPEND = "data_quality/raw_ems_dq.md"
CHUNK_SIZE = 200_000

STUB_EXCLUDE = frozenset(
    {"INCIDENT_DT", "INCIDENT_COUNTY", "NALOXONE_GIVEN_FLG", "MEDICATION_GIVEN_OTHER_FLG"}
)
TS_PAIRS = [
    ("UNIT_NOTIFIED_BY_DISPATCH_DT", "UNIT_ARRIVED_ON_SCENE_DT"),
    ("UNIT_ARRIVED_ON_SCENE_DT", "UNIT_LEFT_SCENE_DT"),
    ("UNIT_LEFT_SCENE_DT", "PATIENT_ARRIVED_DESTINATION_DT"),
]
DUR_CHECKS = [
    ("PROVIDER_TO_SCENE_MINS", "UNIT_NOTIFIED_BY_DISPATCH_DT", "UNIT_ARRIVED_ON_SCENE_DT"),
    ("PROVIDER_TO_DESTINATION_MINS", "UNIT_NOTIFIED_BY_DISPATCH_DT", "PATIENT_ARRIVED_DESTINATION_DT"),
]
DT_COLS = [
    "UNIT_NOTIFIED_BY_DISPATCH_DT",
    "UNIT_ARRIVED_ON_SCENE_DT",
    "UNIT_ARRIVED_TO_PATIENT_DT",
    "UNIT_LEFT_SCENE_DT",
    "PATIENT_ARRIVED_DESTINATION_DT",
]
PROVIDER_COLS = ["PROVIDER_TYPE_STRUCTURE", "PROVIDER_TYPE_SERVICE", "PROVIDER_TYPE_SERVICE_LEVEL"]


def year_from_path(filepath):
    m = re.search(r"(\d{4})\.csv$", filepath)
    return int(m.group(1)) if m else None


def iter_chunks(filepath):
    for chunk in pd.read_csv(filepath, chunksize=CHUNK_SIZE, dtype=str, low_memory=False):
        chunk.columns = [c.strip() for c in chunk.columns]
        for col in DT_COLS:
            if col in chunk.columns:
                chunk[col] = pd.to_datetime(chunk[col], errors="coerce")
        yield chunk


def check1_stubs(chunk, null_cols):
    all_null = chunk[null_cols].isna().all(axis=1)
    flag_active = chunk["NALOXONE_GIVEN_FLG"].str.strip().eq("1") | chunk[
        "MEDICATION_GIVEN_OTHER_FLG"
    ].str.strip().eq("1")
    return int(all_null.sum()), int((all_null & ~flag_active).sum())


def check2_ts_ordering(chunk):
    results = {}
    for col_a, col_b in TS_PAIRS:
        mask = chunk[col_a].notna() & chunk[col_b].notna()
        n_test = int(mask.sum())
        if n_test == 0:
            results[(col_a, col_b)] = (0, 0)
        else:
            violations = int((chunk.loc[mask, col_a] >= chunk.loc[mask, col_b]).sum())
            results[(col_a, col_b)] = (n_test, violations)
    return results


def check3_duration(chunk):
    results = {}
    for stored_col, start_col, end_col in DUR_CHECKS:
        mask = chunk[stored_col].notna() & chunk[start_col].notna() & chunk[end_col].notna()
        if not mask.any():
            results[stored_col] = (0, 0)
            continue
        sub = chunk.loc[mask]
        stored = pd.to_numeric(sub[stored_col], errors="coerce")
        derived = (sub[end_col] - sub[start_col]).dt.total_seconds() / 60.0
        valid = stored.notna() & derived.notna()
        n_test = int(valid.sum())
        mismatches = int((abs(stored[valid] - derived[valid]) > 1).sum()) if n_test > 0 else 0
        results[stored_col] = (n_test, mismatches)
    return results


def update_provider_counter(chunk, counter):
    sub = chunk[PROVIDER_COLS].fillna("_NULL_")
    for key, cnt in sub.groupby(PROVIDER_COLS).size().items():
        counter[tuple(key)] += int(cnt)


def update_county_year(chunk, year, county_year):
    for county, cnt in chunk["INCIDENT_COUNTY"].fillna("_NULL_").value_counts().items():
        county_year[(str(county).strip(), year)] += int(cnt)


def process_files(filepaths):
    stub_by_year = {}
    ts_by_year = {}
    dur_by_year = {}
    provider_counter = Counter()
    county_year = Counter()

    for filepath in sorted(filepaths):
        year = year_from_path(filepath)
        print(f"  processing {year}...", flush=True)

        stub_by_year[year] = {"total": 0, "stubs": 0}
        ts_by_year[year] = {pair: [0, 0] for pair in TS_PAIRS}
        if year < 2022:
            dur_by_year[year] = {col: [0, 0] for col, _, _ in DUR_CHECKS}

        null_cols = None

        for chunk in iter_chunks(filepath):
            if null_cols is None:
                null_cols = [c for c in chunk.columns if c not in STUB_EXCLUDE]

            all_null_count, stub_count = check1_stubs(chunk, null_cols)
            stub_by_year[year]["total"] += len(chunk)
            stub_by_year[year]["stubs"] += stub_count

            for pair, (n_test, n_viol) in check2_ts_ordering(chunk).items():
                ts_by_year[year][pair][0] += n_test
                ts_by_year[year][pair][1] += n_viol

            if year < 2022:
                for field, (n_test, n_miss) in check3_duration(chunk).items():
                    dur_by_year[year][field][0] += n_test
                    dur_by_year[year][field][1] += n_miss

            update_provider_counter(chunk, provider_counter)
            update_county_year(chunk, year, county_year)

    return stub_by_year, ts_by_year, dur_by_year, provider_counter, county_year


def fmt_pct(n, d):
    return f"{n / d * 100:.2f}%" if d > 0 else "N/A"


def format_check1(stub_by_year):
    lines = [
        "## Check 1 -- Stub Records\n",
        "Rows where every column except INCIDENT_DT, INCIDENT_COUNTY, NALOXONE_GIVEN_FLG,",
        "and MEDICATION_GIVEN_OTHER_FLG is null. Rows with either flag = 1 are not stubs.\n",
        "| Year | Total Rows | Stubs | Stub % |",
        "|------|----------:|------:|-------:|",
    ]
    for year in sorted(stub_by_year):
        d = stub_by_year[year]
        lines.append(f"| {year} | {d['total']:,} | {d['stubs']:,} | {fmt_pct(d['stubs'], d['total'])} |")
    return "\n".join(lines)


def format_check2(ts_by_year):
    pair_labels = {
        ("UNIT_NOTIFIED_BY_DISPATCH_DT", "UNIT_ARRIVED_ON_SCENE_DT"): "NOTIFIED >= ARRIVED_SCENE",
        ("UNIT_ARRIVED_ON_SCENE_DT", "UNIT_LEFT_SCENE_DT"): "ARRIVED_SCENE >= LEFT_SCENE",
        ("UNIT_LEFT_SCENE_DT", "PATIENT_ARRIVED_DESTINATION_DT"): "LEFT_SCENE >= ARRIVED_DEST",
    }
    lines = [
        "## Check 2 -- Timestamp Ordering Violations\n",
        "A violation is flagged when the earlier timestamp >= the later timestamp for a given pair.",
        "Only rows where both timestamps are non-null are tested. UNIT_ARRIVED_TO_PATIENT_DT excluded.\n",
        "| Year | Pair | Testable Rows | Violations | Violation % |",
        "|------|------|-------------:|----------:|------------:|",
    ]
    for year in sorted(ts_by_year):
        for pair in TS_PAIRS:
            n_test, n_viol = ts_by_year[year][pair]
            label = pair_labels[pair]
            lines.append(f"| {year} | {label} | {n_test:,} | {n_viol:,} | {fmt_pct(n_viol, n_test)} |")
    return "\n".join(lines)


def format_check3(dur_by_year):
    field_labels = {
        "PROVIDER_TO_SCENE_MINS": "PROVIDER_TO_SCENE_MINS",
        "PROVIDER_TO_DESTINATION_MINS": "PROVIDER_TO_DESTINATION_MINS",
    }
    lines = [
        "## Check 3 -- Duration vs. Timestamp Consistency (Pre-2022 Only)\n",
        "Mismatch = |stored_minutes - derived_minutes| > 1.",
        "2022+ files excluded (timestamps midnight-truncated; comparison is invalid).\n",
        "| Year | Field | Testable Rows | Mismatches | Mismatch % |",
        "|------|-------|-------------:|----------:|----------:|",
    ]
    for year in sorted(dur_by_year):
        for field, *_ in DUR_CHECKS:
            n_test, n_miss = dur_by_year[year][field]
            lines.append(f"| {year} | {field_labels[field]} | {n_test:,} | {n_miss:,} | {fmt_pct(n_miss, n_test)} |")
    return "\n".join(lines)


def format_check4(provider_counter):
    total = sum(provider_counter.values())
    lines = [
        "## Check 4 -- PROVIDER_TYPE Combination Frequency\n",
        "All years combined. Sorted descending by count. Flag = combination < 0.1% of total rows.\n",
        f"Total rows across all years: {total:,}\n",
        "| PROVIDER_TYPE_STRUCTURE | PROVIDER_TYPE_SERVICE | PROVIDER_TYPE_SERVICE_LEVEL | Count | % | Flag |",
        "|------------------------|----------------------|----------------------------|------:|--:|:----:|",
    ]
    for combo, cnt in sorted(provider_counter.items(), key=lambda x: -x[1]):
        pct = cnt / total * 100
        flag = "<0.1%" if pct < 0.1 else ""
        lines.append(f"| {combo[0]} | {combo[1]} | {combo[2]} | {cnt:,} | {pct:.3f}% | {flag} |")
    return "\n".join(lines)


def format_check5(county_year, years):
    all_counties = sorted({c for c, _ in county_year})
    header = "| County | " + " | ".join(str(y) for y in years) + " |"
    sep = "|--------|" + "|".join(["------:" for _ in years]) + "|"
    lines = [
        "## Check 5 -- County-Year Event Volume Distribution\n",
        "Row counts per (INCIDENT_COUNTY, year). Zero-count county-years are flagged.\n",
        header,
        sep,
    ]
    flagged = []
    for county in all_counties:
        counts = [county_year.get((county, y), 0) for y in years]
        cells = " | ".join(f"{c:,}" if c > 0 else "**0**" for c in counts)
        lines.append(f"| {county} | {cells} |")
        for y, c in zip(years, counts):
            if c == 0:
                flagged.append((county, y))
    if flagged:
        lines.append("\n**Zero-count county-years:**\n")
        for county, y in flagged:
            lines.append(f"- {county} / {y}")
    return "\n".join(lines)


def write_full_output(results, years):
    stub_by_year, ts_by_year, dur_by_year, provider_counter, county_year = results
    sections = [
        f"# Session 1.5 Complex DQ Checks\n\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"Source: `_Claude/INPUTS/ems_runs_*.csv` (13 files)\n",
        format_check1(stub_by_year),
        format_check2(ts_by_year),
        format_check3(dur_by_year),
        format_check4(provider_counter),
        format_check5(county_year, years),
    ]
    with open(OUTPUT_MD, "w") as f:
        f.write("\n\n---\n\n".join(sections))
    print(f"Full results written to {OUTPUT_MD}")


def append_dq_summary(stub_by_year, ts_by_year, dur_by_year):
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"\n\n## {today} -- Session 1.5 Complex DQ Checks\n",
        "### Check 1: Stub Records",
    ]
    for year in sorted(stub_by_year):
        d = stub_by_year[year]
        lines.append(f"- {year}: {d['stubs']:,} stubs / {d['total']:,} rows ({fmt_pct(d['stubs'], d['total'])})")

    lines.append("\n### Check 2: Timestamp Ordering Violations (notable pairs)")
    pair_labels = {
        ("UNIT_NOTIFIED_BY_DISPATCH_DT", "UNIT_ARRIVED_ON_SCENE_DT"): "NOTIFIED >= ARRIVED_SCENE",
        ("UNIT_ARRIVED_ON_SCENE_DT", "UNIT_LEFT_SCENE_DT"): "ARRIVED_SCENE >= LEFT_SCENE",
        ("UNIT_LEFT_SCENE_DT", "PATIENT_ARRIVED_DESTINATION_DT"): "LEFT_SCENE >= ARRIVED_DEST",
    }
    for year in sorted(ts_by_year):
        for pair in TS_PAIRS:
            n_test, n_viol = ts_by_year[year][pair]
            if n_test > 0 and n_viol > 0:
                lines.append(
                    f"- {year} / {pair_labels[pair]}: {n_viol:,} violations / {n_test:,} testable ({fmt_pct(n_viol, n_test)})"
                )

    lines.append("\n### Check 3: Duration vs. Timestamp Consistency (pre-2022)")
    for year in sorted(dur_by_year):
        for field, *_ in DUR_CHECKS:
            n_test, n_miss = dur_by_year[year][field]
            if n_test > 0:
                lines.append(f"- {year} / {field}: {n_miss:,} mismatches / {n_test:,} testable ({fmt_pct(n_miss, n_test)})")

    lines.append("\nSee `_Claude/OUTPUTS/dq_complex_checks.md` for full results (Check 4 combos, Check 5 county-year matrix).")

    with open(DQ_APPEND, "a") as f:
        f.write("\n".join(lines))
    print(f"DQ summary appended to {DQ_APPEND}")


def main():
    filepaths = sorted(glob.glob(INPUTS_GLOB))
    if not filepaths:
        raise FileNotFoundError(f"No files found matching {INPUTS_GLOB}")
    years = sorted(year_from_path(p) for p in filepaths)
    print(f"Found {len(filepaths)} files: {years[0]}-{years[-1]}")

    results = process_files(filepaths)
    stub_by_year, ts_by_year, dur_by_year, provider_counter, county_year = results

    write_full_output(results, years)
    append_dq_summary(stub_by_year, ts_by_year, dur_by_year)


if __name__ == "__main__":
    main()
