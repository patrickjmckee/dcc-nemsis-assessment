"""Load: resolve dimension surrogate keys (Type 1 overwrite, Type 2 versioned),
then batch-insert the fact and quarantine rows idempotently.

Dimensions are loaded set-based via a temp table + INSERT ... WHERE NOT EXISTS.
Type 2 members get valid_from = MIN(incident_date) for the natural-key tuple,
valid_to NULL, is_current 1. Fact idempotency is enforced by pre-filtering on
UNIQUE(row_hash, source_year); duplicates are skipped and counted, never abort
the run."""

import pandas as pd

from utils import SOURCE_COLUMNS, insert_batches, row_hash

_FACT_COLS = [
    "incident_date_key", "county_key", "complaint_key", "flags_key",
    "provider_type_key", "destination_type_key", "disposition_key",
    "provider_to_scene_mins", "provider_to_destination_mins",
    "unit_notified_dt", "unit_arrived_scene_dt", "unit_arrived_patient_dt",
    "unit_left_scene_dt", "patient_arrived_destination_dt",
    "provider_impression_primary", "row_hash", "load_id", "source_year",
]
_FACT_INT_COLS = [
    "incident_date_key", "county_key", "complaint_key", "flags_key",
    "provider_type_key", "destination_type_key", "disposition_key",
    "provider_to_scene_mins", "provider_to_destination_mins", "load_id", "source_year",
]
_FACT_SQL = (
    "INSERT INTO dw.fact_ems_run (" + ", ".join(_FACT_COLS) + ") VALUES ("
    + ", ".join(["?"] * len(_FACT_COLS)) + ")"
)
_Q_COLS = SOURCE_COLUMNS + ["row_hash", "quarantine_reason", "load_id", "source_year"]
_Q_SQL = (
    "INSERT INTO stg.stg_ems_quarantine (" + ", ".join(_Q_COLS) + ") VALUES ("
    + ", ".join(["?"] * len(_Q_COLS)) + ")"
)
_INT_SQL_TYPES = {"INT", "SMALLINT", "TINYINT", "BIGINT"}


def next_load_id(conn):
    """MAX(load_id)+1 from staging, or 1 when empty. One value per run."""
    cur = conn.cursor()
    cur.execute("SELECT ISNULL(MAX(load_id), 0) + 1 FROM stg.stg_ems_raw")
    val = cur.fetchone()[0]
    cur.close()
    return int(val)


def _records(df, cols, int_cols):
    """DataFrame -> list of tuples, NaN/NaT -> None, int_cols -> nullable int."""
    out = df[cols].copy()
    for c in int_cols:
        out[c] = out[c].astype("Int64")
    obj = out.astype(object).where(out.notna(), None)
    return list(map(tuple, obj.to_numpy()))


def _fetch_map(conn, table, nat_cols, key_col, where=""):
    """Build {natural-key tuple: surrogate key} from a dimension table."""
    cur = conn.cursor()
    sel = ", ".join(f"[{c}]" for c in nat_cols)
    cur.execute(f"SELECT {sel}, [{key_col}] FROM {table} {where}")
    mapping = {tuple(r[:-1]): r[-1] for r in cur.fetchall()}
    cur.close()
    return mapping


def _load_type1(conn, members, table, key_col, nat, attrs, batch_size):
    """Insert new Type 1 members (overwrite semantics, insert-if-absent)."""
    cols = nat + attrs
    names = [c for c, _ in cols]
    nat_names = [c for c, _ in nat]
    tmp = "#t1_" + table.split(".")[-1]
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {tmp}")
    cur.execute(f"CREATE TABLE {tmp} (" + ", ".join(f"[{c}] {t}" for c, t in cols) + ")")
    conn.commit()
    int_cols = [c for c, t in cols if t in _INT_SQL_TYPES]
    ins = (f"INSERT INTO {tmp} (" + ", ".join(f"[{c}]" for c in names)
           + ") VALUES (" + ", ".join(["?"] * len(names)) + ")")
    insert_batches(conn, ins, _records(members, names, int_cols), batch_size)
    join = " AND ".join(f"d.[{c}] = t.[{c}]" for c in nat_names)
    sel = ", ".join(f"[{c}]" for c in names)
    cur.execute(f"INSERT INTO {table} ({sel}) SELECT {sel} FROM {tmp} t "
                f"WHERE NOT EXISTS (SELECT 1 FROM {table} d WHERE {join})")
    cur.execute(f"DROP TABLE {tmp}")
    conn.commit()
    cur.close()
    return _fetch_map(conn, table, nat_names, key_col)


def _load_type2(conn, members, table, key_col, nat_cols, batch_size):
    """Insert new Type 2 versions (natural-key tuple not currently present)."""
    tmp = "#t2_" + table.split(".")[-1]
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {tmp}")
    coldef = ", ".join(f"[{c}] VARCHAR(255)" for c in nat_cols)
    cur.execute(f"CREATE TABLE {tmp} ({coldef}, row_hash VARCHAR(32), valid_from DATE)")
    conn.commit()
    cols = nat_cols + ["row_hash", "valid_from"]
    ins = (f"INSERT INTO {tmp} (" + ", ".join(f"[{c}]" for c in cols)
           + ") VALUES (" + ", ".join(["?"] * len(cols)) + ")")
    insert_batches(conn, ins, _records(members, cols, []), batch_size)
    join = " AND ".join(f"d.[{c}] = t.[{c}]" for c in nat_cols)
    natsel = ", ".join(f"[{c}]" for c in nat_cols)
    cur.execute(
        f"INSERT INTO {table} ({natsel}, row_hash, valid_from, valid_to, is_current) "
        f"SELECT {natsel}, t.row_hash, t.valid_from, NULL, 1 FROM {tmp} t "
        f"WHERE NOT EXISTS (SELECT 1 FROM {table} d WHERE {join} AND d.is_current = 1)")
    cur.execute(f"DROP TABLE {tmp}")
    conn.commit()
    cur.close()
    return _fetch_map(conn, table, nat_cols, key_col, "WHERE is_current = 1")


def _date_members(fact):
    """Distinct incident dates with calendar attributes (day_of_week = 1..7)."""
    ts = pd.to_datetime(fact["incident_date"]).drop_duplicates()
    return pd.DataFrame({
        "incident_date": ts.dt.date,
        "year": ts.dt.year,
        "month": ts.dt.month,
        "quarter": ts.dt.quarter,
        "day_of_week": ts.dt.dayofweek + 1,
    })


def _type2_members(fact, cols, mask=None):
    """Distinct natural-key tuples with valid_from = MIN(incident_date) and
    row_hash over the tuple. NULLs coerced to '' (sentinel-friendly).

    valid_from is the min incident_date within the batch being loaded. Because
    _load_type2 only inserts a tuple when no current row exists, the persisted
    valid_from reflects the first batch/chunk/year that introduced the tuple,
    not necessarily the global earliest date (relevant only for out-of-order
    incremental loads; this source has no real SCD versioning)."""
    sub = fact if mask is None else fact[mask]
    m = sub[cols].fillna("").copy()
    m["incident_date"] = pd.to_datetime(sub["incident_date"]).dt.date
    g = (m.groupby(cols, as_index=False)["incident_date"].min()
         .rename(columns={"incident_date": "valid_from"}))
    g["row_hash"] = g[cols].apply(lambda r: row_hash(r.tolist()), axis=1)
    return g


def _lookup(df, cols, mapping, fill=None, null_mask=None):
    """Resolve surrogate keys for each row via a vectorized left merge (no
    row-by-row lookup); null_mask forces NULL FK. Unmatched keys stay NaN."""
    left = df[cols].fillna(fill) if fill is not None else df[cols]
    cols = list(cols)
    if mapping:
        md = pd.DataFrame([(*k, v) for k, v in mapping.items()], columns=cols + ["__k"])
        merged = left.merge(md, on=cols, how="left", sort=False)
        s = pd.Series(merged["__k"].to_numpy(), index=df.index, dtype="object")
    else:
        s = pd.Series([None] * len(df), index=df.index, dtype="object")
    if null_mask is not None:
        s[null_mask.values] = None
    return s


def load_dimensions(conn, fact, batch_size):
    """Load all dimensions and return fact augmented with surrogate FK columns."""
    if fact.empty:
        return fact
    ts = pd.to_datetime(fact["incident_date"])
    date_map = _load_type1(
        conn, _date_members(fact), "dw.dim_date", "incident_date_key",
        [("incident_date", "DATE")],
        [("year", "SMALLINT"), ("month", "TINYINT"), ("quarter", "TINYINT"),
         ("day_of_week", "TINYINT")], batch_size)
    county_map = _load_type1(
        conn, fact[["county_name"]].drop_duplicates(), "dw.dim_county", "county_key",
        [("county_name", "VARCHAR(100)")], [], batch_size)
    flags_cols = ["injury_flag", "naloxone_flag", "medication_flag"]
    flags_map = _load_type1(
        conn, fact[flags_cols].drop_duplicates(), "dw.dim_run_flags", "flags_key",
        [("injury_flag", "VARCHAR(10)"), ("naloxone_flag", "VARCHAR(1)"),
         ("medication_flag", "VARCHAR(1)")], [], batch_size)
    comp_cols = ["chief_complaint_dispatch", "anatomic_location", "primary_symptom"]
    comp_map = _load_type2(conn, _type2_members(fact, comp_cols),
                           "dw.dim_complaint", "complaint_key", comp_cols, batch_size)
    prov_cols = ["structure", "service", "level"]
    prov_map = _load_type2(conn, _type2_members(fact, prov_cols),
                           "dw.dim_provider_type", "provider_type_key", prov_cols, batch_size)
    dest_mask = fact["destination_code"].notna()
    dest_map = _load_type2(conn, _type2_members(fact, ["destination_code"], dest_mask),
                           "dw.dim_destination_type", "destination_type_key",
                           ["destination_code"], batch_size)
    disp_cols = ["disposition_ed", "disposition_hospital"]
    disp_mask = fact[disp_cols].notna().any(axis=1)
    disp_map = _load_type2(conn, _type2_members(fact, disp_cols, disp_mask),
                           "dw.dim_disposition", "disposition_key", disp_cols, batch_size)
    out = fact.copy()
    out["incident_date_key"] = _lookup(out.assign(_inc_date=ts.dt.date),
                                       ["_inc_date"], date_map)
    out["county_key"] = _lookup(out, ["county_name"], county_map)
    out["flags_key"] = _lookup(out, flags_cols, flags_map)
    out["complaint_key"] = _lookup(out, comp_cols, comp_map, fill="")
    out["provider_type_key"] = _lookup(out, prov_cols, prov_map, fill="")
    out["destination_type_key"] = _lookup(out, ["destination_code"], dest_map,
                                          fill="", null_mask=~dest_mask)
    out["disposition_key"] = _lookup(out, disp_cols, disp_map,
                                     fill="", null_mask=~disp_mask)
    required = ["incident_date_key", "county_key", "complaint_key",
                "flags_key", "provider_type_key"]
    missing = [c for c in required if out[c].isna().any()]
    if missing:
        raise ValueError(f"unresolved NOT NULL dimension keys {missing} "
                         f"(year {int(out['source_year'].iloc[0])})")
    return out


def load_quarantine(conn, qdf, batch_size):
    """Insert quarantined rows, deduped on (source_year, row_hash). Returns count."""
    if qdf.empty:
        return 0
    q = qdf.drop_duplicates(["source_year", "row_hash"])
    # fast=False: quarantine stores the 22 raw VARCHAR(MAX) source columns.
    return insert_batches(conn, _Q_SQL, _records(q, _Q_COLS, ["load_id", "source_year"]),
                          batch_size, fast=False)


def load_fact(conn, fact, batch_size):
    """Idempotent fact load. Returns (inserted, skipped). Existing (row_hash,
    source_year) and within-batch duplicates are skipped and counted."""
    if fact.empty:
        return 0, 0
    year = int(fact["source_year"].iloc[0])
    cur = conn.cursor()
    cur.execute("SELECT row_hash FROM dw.fact_ems_run WHERE source_year = ?", year)
    existing = {r[0] for r in cur.fetchall()}
    cur.close()
    deduped = fact.drop_duplicates("row_hash")
    new = deduped[~deduped["row_hash"].isin(existing)]
    skipped = len(fact) - len(new)
    inserted = insert_batches(conn, _FACT_SQL, _records(new, _FACT_COLS, _FACT_INT_COLS),
                              batch_size)
    return inserted, skipped
