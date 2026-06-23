"""Shared helpers for the NEMSIS EMS ETL pipeline: config, logging,
database connection, row hashing, and county normalization."""

import hashlib
import logging
import sys
from pathlib import Path

import yaml

# The 22 source columns in CSV header order. Fact row_hash concatenates these
# values (NULL coerced to '') with '|' in exactly this order.
SOURCE_COLUMNS = [
    "INCIDENT_DT",
    "INCIDENT_COUNTY",
    "CHIEF_COMPLAINT_DISPATCH",
    "CHIEF_COMPLAINT_ANATOMIC_LOC",
    "PRIMARY_SYMPTOM",
    "PROVIDER_IMPRESSION_PRIMARY",
    "DISPOSITION_ED",
    "DISPOSITION_HOSPITAL",
    "INJURY_FLG",
    "NALOXONE_GIVEN_FLG",
    "MEDICATION_GIVEN_OTHER_FLG",
    "DESTINATION_TYPE",
    "PROVIDER_TYPE_STRUCTURE",
    "PROVIDER_TYPE_SERVICE",
    "PROVIDER_TYPE_SERVICE_LEVEL",
    "PROVIDER_TO_SCENE_MINS",
    "PROVIDER_TO_DESTINATION_MINS",
    "UNIT_NOTIFIED_BY_DISPATCH_DT",
    "UNIT_ARRIVED_ON_SCENE_DT",
    "UNIT_ARRIVED_TO_PATIENT_DT",
    "UNIT_LEFT_SCENE_DT",
    "PATIENT_ARRIVED_DESTINATION_DT",
]


def load_config(path):
    """Read the YAML params file into a dict."""
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def get_logger(log_dir, level, load_id):
    """Logger writing to both console and a per-load file."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"ems_etl.load_{load_id}")
    logger.setLevel(getattr(logging, str(level).upper(), logging.INFO))
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_h = logging.FileHandler(Path(log_dir) / f"etl_load_{load_id}.log", encoding="utf-8")
    file_h.setFormatter(fmt)
    stream_h = logging.StreamHandler(sys.stdout)
    stream_h.setFormatter(fmt)
    logger.addHandler(file_h)
    logger.addHandler(stream_h)
    return logger


def get_connection(db):
    """Open a pyodbc connection to SQL Server from the db config block.
    auth: 'trusted' (Windows/integrated, default) or 'sql' (username/password)."""
    import pyodbc

    conn_str = (
        f"DRIVER={{{db['driver']}}};SERVER={db['server']};"
        f"DATABASE={db['database']};TrustServerCertificate=yes"
    )
    if str(db.get("auth", "trusted")).lower() == "sql":
        conn_str += f";UID={db['username']};PWD={db['password']}"
    else:
        conn_str += ";Trusted_Connection=yes"
    return pyodbc.connect(conn_str, autocommit=False)


def insert_batches(conn, sql, rows, batch_size, fast=True):
    """Batch INSERT (no row-by-row execution); commits once at the end and
    returns the row count. fast=False disables fast_executemany for inserts
    that touch VARCHAR(MAX) columns (pyodbc over-binds MAX types on the fast
    path), e.g. the all-MAX staging and quarantine tables."""
    if not rows:
        return 0
    cur = conn.cursor()
    cur.fast_executemany = fast
    for start in range(0, len(rows), batch_size):
        cur.executemany(sql, rows[start:start + batch_size])
    conn.commit()
    cur.close()
    return len(rows)


def row_hash(values):
    """MD5 hex (32-char lowercase) of values joined by '|', NULL coerced to ''."""
    parts = ["" if v is None else str(v) for v in values]
    return hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()


def row_hashes(frame):
    """Vectorized row_hash over a string-column DataFrame (column order defines
    the hash). NULL coerced to ''. Returns a Series of 32-char lowercase MD5 hex.
    The '|' delimiter is fixed by the SESSION 3 spec; values are not escaped, so
    a field literally containing '|' carries a small, spec-accepted collision risk."""
    cols = list(frame.columns)
    joined = frame[cols[0]].fillna("")
    for col in cols[1:]:
        joined = joined + "|" + frame[col].fillna("")
    return joined.map(lambda s: hashlib.md5(s.encode("utf-8")).hexdigest())


def normalize_county(value):
    """Uppercase, strip surrounding whitespace, strip periods (St. Joseph)."""
    if value is None:
        return ""
    return str(value).strip().upper().replace(".", "")


def load_county_set(path):
    """Load the canonical normalized Indiana county names into a set."""
    with open(path, "r", encoding="utf-8") as fh:
        return {line.strip() for line in fh if line.strip()}
