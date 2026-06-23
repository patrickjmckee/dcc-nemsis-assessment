"""Transform: validate source rows, split rejects into quarantine, normalize
and clean the survivors, and compute the fact row_hash.

Reject criteria and field repairs follow MEMORY/dq-rules.md and the SESSION 3
spec. Field-level repairs (out-of-window timestamps nulled, INJURY_FLG mapped)
do not reject the row; they are counted and logged only."""

from datetime import date

import numpy as np
import pandas as pd

from utils import SOURCE_COLUMNS, normalize_county, row_hash

# Reject window for INCIDENT_DT lower bound (dq-rules rule 1).
_MIN_INCIDENT_DATE = pd.Timestamp("2013-01-01")
# Duration valid range in minutes (dq-rules rule 3).
_DURATION_MAX = 1440
_INJURY_DOMAIN = {"yes": "Yes", "no": "No", "unknown": "Unknown"}

# Source timestamp column -> fact column.
_TS_MAP = {
    "UNIT_NOTIFIED_BY_DISPATCH_DT": "unit_notified_dt",
    "UNIT_ARRIVED_ON_SCENE_DT": "unit_arrived_scene_dt",
    "UNIT_ARRIVED_TO_PATIENT_DT": "unit_arrived_patient_dt",
    "UNIT_LEFT_SCENE_DT": "unit_left_scene_dt",
    "PATIENT_ARRIVED_DESTINATION_DT": "patient_arrived_destination_dt",
}
# Ordering chain (SESSION 1.5 Check 2; excludes arrived_to_patient).
_ORDER_CHAIN = [
    "unit_notified_dt",
    "unit_arrived_scene_dt",
    "unit_left_scene_dt",
    "patient_arrived_destination_dt",
]


def _numeric_invalid(raw):
    """Return (numeric series, invalid mask) for a duration column.
    Invalid = present but non-numeric, negative, or > 1440. NULL is allowed."""
    num = pd.to_numeric(raw, errors="coerce")
    invalid = raw.notna() & (num.isna() | (num < 0) | (num > _DURATION_MAX))
    return num, invalid


def _reason(df, parsed_dt, county_norm, county_set, max_date):
    """First-failing reject reason per row (None if the row passes)."""
    _, scene_bad = _numeric_invalid(df["PROVIDER_TO_SCENE_MINS"])
    _, dest_bad = _numeric_invalid(df["PROVIDER_TO_DESTINATION_MINS"])
    flags_bad = ~df["NALOXONE_GIVEN_FLG"].isin(["0", "1"]) | ~df[
        "MEDICATION_GIVEN_OTHER_FLG"
    ].isin(["0", "1"])
    provider_null = df["PROVIDER_TYPE_STRUCTURE"].isna() | df["PROVIDER_TYPE_SERVICE"].isna()
    rules = [
        (parsed_dt.isna(), "INCIDENT_DT_INVALID"),
        ((parsed_dt < _MIN_INCIDENT_DATE) | (parsed_dt >= max_date), "INCIDENT_DT_OUT_OF_RANGE"),
        (~county_norm.isin(county_set), "INCIDENT_COUNTY_INVALID"),
        (scene_bad | dest_bad, "DURATION_MINS_OUT_OF_RANGE"),
        (flags_bad, "FLAG_INVALID"),
        (provider_null, "PROVIDER_TYPE_NULL"),
    ]
    reason = pd.Series(np.nan, index=df.index, dtype=object)
    for mask, code in rules:
        reason[reason.isna() & mask.fillna(False)] = code
    return reason


def _map_injury(series):
    """Map INJURY_FLG to {Yes, No, Unknown}; count values forced to Unknown."""
    lowered = series.fillna("unknown").str.strip().str.lower()
    mapped = lowered.map(_INJURY_DOMAIN).fillna("Unknown")
    repairs = int((~lowered.isin(_INJURY_DOMAIN)).sum())
    return mapped, repairs


def _window_timestamps(clean, incident_ts):
    """Parse the 5 unit/patient timestamps; null any outside
    [incident_date - 1d, incident_date + 7d]. Returns (dict of series, repairs)."""
    lower = incident_ts - pd.Timedelta(days=1)
    upper = incident_ts + pd.Timedelta(days=7)
    out, repairs = {}, 0
    for src, fact_col in _TS_MAP.items():
        parsed = pd.to_datetime(clean[src], format="ISO8601", errors="coerce")
        outside = parsed.notna() & ((parsed < lower) | (parsed > upper))
        repairs += int(outside.sum())
        out[fact_col] = parsed.mask(outside)
    return out, repairs


def _ordering_violations(timestamps):
    """Count rows violating the timestamp chain (both ends non-null)."""
    bad = pd.Series(False, index=next(iter(timestamps.values())).index)
    for left, right in zip(_ORDER_CHAIN, _ORDER_CHAIN[1:]):
        a, b = timestamps[left], timestamps[right]
        bad = bad | (a.notna() & b.notna() & (a >= b))
    return int(bad.sum())


def _build_fact(clean, parsed_clean, hashes_clean, load_id):
    """Assemble the cleaned fact-ready frame and field-repair stats."""
    incident_ts = parsed_clean.dt.normalize()
    injury, injury_repairs = _map_injury(clean["INJURY_FLG"])
    timestamps, ts_repairs = _window_timestamps(clean, incident_ts)
    scene = pd.to_numeric(clean["PROVIDER_TO_SCENE_MINS"], errors="coerce")
    dest = pd.to_numeric(clean["PROVIDER_TO_DESTINATION_MINS"], errors="coerce")
    fact = pd.DataFrame(index=clean.index)
    fact["incident_date"] = incident_ts
    fact["county_name"] = clean["INCIDENT_COUNTY"].map(normalize_county)
    fact["chief_complaint_dispatch"] = clean["CHIEF_COMPLAINT_DISPATCH"]
    fact["anatomic_location"] = clean["CHIEF_COMPLAINT_ANATOMIC_LOC"]
    fact["primary_symptom"] = clean["PRIMARY_SYMPTOM"]
    fact["injury_flag"] = injury
    fact["naloxone_flag"] = clean["NALOXONE_GIVEN_FLG"]
    fact["medication_flag"] = clean["MEDICATION_GIVEN_OTHER_FLG"]
    fact["destination_code"] = clean["DESTINATION_TYPE"]
    fact["disposition_ed"] = clean["DISPOSITION_ED"]
    fact["disposition_hospital"] = clean["DISPOSITION_HOSPITAL"]
    fact["structure"] = clean["PROVIDER_TYPE_STRUCTURE"]
    fact["service"] = clean["PROVIDER_TYPE_SERVICE"]
    fact["level"] = clean["PROVIDER_TYPE_SERVICE_LEVEL"]
    fact["provider_impression_primary"] = clean["PROVIDER_IMPRESSION_PRIMARY"]
    fact["provider_to_scene_mins"] = scene
    fact["provider_to_destination_mins"] = dest
    for col, series in timestamps.items():
        fact[col] = series
    fact["row_hash"] = hashes_clean
    fact["source_year"] = clean["source_year"]
    fact["load_id"] = load_id
    stats = {
        "injury_repairs": injury_repairs,
        "timestamp_repairs": ts_repairs,
        "ordering_violations": _ordering_violations(timestamps),
    }
    return fact, stats


def _build_quarantine(df, reason, hashes, load_id):
    """Raw 22 source columns plus quarantine metadata for rejected rows."""
    qmask = reason.notna()
    qdf = df.loc[qmask, SOURCE_COLUMNS].where(df.loc[qmask, SOURCE_COLUMNS].notna(), None)
    qdf = qdf.copy()
    qdf["row_hash"] = hashes[qmask]
    qdf["quarantine_reason"] = reason[qmask]
    qdf["load_id"] = load_id
    qdf["source_year"] = df.loc[qmask, "source_year"]
    return qdf


def transform(df, load_id, county_set, run_year):
    """Validate, split, and clean one year's rows.

    Returns (fact_df, quarantine_df, stats). Ordering checks are computed for
    2014-2021 only; for later years the count is reported as None."""
    max_date = pd.Timestamp(date(run_year + 1, 1, 1))
    parsed_dt = pd.to_datetime(df["INCIDENT_DT"], format="ISO8601", errors="coerce")
    county_norm = df["INCIDENT_COUNTY"].map(normalize_county)
    hashes = df[SOURCE_COLUMNS].fillna("").apply(lambda r: row_hash(r.tolist()), axis=1)
    reason = _reason(df, parsed_dt, county_norm, county_set, max_date)
    qdf = _build_quarantine(df, reason, hashes, load_id)
    clean_mask = reason.isna()
    clean = df.loc[clean_mask]
    fact, stats = _build_fact(clean, parsed_dt[clean_mask], hashes[clean_mask], load_id)
    if not (2014 <= df["source_year"].iloc[0] <= 2021):
        stats["ordering_violations"] = None
    stats["rejected"] = int(reason.notna().sum())
    stats["reject_by_reason"] = reason.value_counts().to_dict()
    return fact, qdf, stats
