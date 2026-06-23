"""Extract: stream one source-year CSV in chunks, trimming header whitespace
and enforcing the expected 22-column schema."""

from pathlib import Path

import pandas as pd

from utils import SOURCE_COLUMNS


def _validate_columns(columns, name):
    """Trim header whitespace (dq-rules rule 7) and verify the source schema."""
    trimmed = [c.strip() for c in columns]
    missing = [c for c in SOURCE_COLUMNS if c not in trimmed]
    if missing:
        raise ValueError(f"{name}: missing expected columns {missing}")
    return trimmed


def read_year_chunks(source_dir, source_pattern, year, chunk_size):
    """Yield schema-validated chunks of ems_runs_<year>.csv.

    Columns are read as strings; only '' is treated as null
    (keep_default_na=False) so literal source tokens like 'None'/'NA'/'NULL'
    survive verbatim instead of being coerced to NaN. Each chunk carries the 22
    source columns plus source_year. Chunking caps peak memory for the large
    (400MB+) files.
    """
    path = Path(source_dir) / source_pattern.format(year=year)
    reader = pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        na_values=[""],
        skipinitialspace=True,
        chunksize=chunk_size,
    )
    for chunk in reader:
        chunk.columns = _validate_columns(chunk.columns, path.name)
        chunk = chunk[SOURCE_COLUMNS].copy()
        chunk["source_year"] = int(year)
        yield chunk
