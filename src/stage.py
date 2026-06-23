"""Stage: land raw source rows verbatim into stg.stg_ems_raw in batches.

No type inference, no constraints -- the 22 source columns are written as-is
(NULL preserved), tagged with source_year and load_id for partitioning and
load tracking."""

from utils import SOURCE_COLUMNS, insert_batches

_COLUMNS = SOURCE_COLUMNS + ["source_year", "load_id"]
_INSERT_SQL = (
    "INSERT INTO stg.stg_ems_raw ("
    + ", ".join(_COLUMNS)
    + ") VALUES ("
    + ", ".join(["?"] * len(_COLUMNS))
    + ")"
)


def stage_dataframe(conn, df, load_id, batch_size):
    """Insert the extracted DataFrame into stg.stg_ems_raw. Returns row count.

    NaN is converted to None so empty source values land as SQL NULL.
    """
    staged = df.copy()
    staged["load_id"] = load_id
    staged = staged.where(staged.notna(), None)
    rows = list(staged[_COLUMNS].itertuples(index=False, name=None))
    # fast=False: stg_ems_raw is all VARCHAR(MAX) columns.
    return insert_batches(conn, _INSERT_SQL, rows, batch_size, fast=False)
