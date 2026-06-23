"""Extract: read one source-year CSV into a DataFrame, trimming header
whitespace and enforcing the expected 22-column schema."""

from pathlib import Path

import pandas as pd

from utils import SOURCE_COLUMNS


def read_year(source_dir, source_pattern, year):
    """Read ems_runs_<year>.csv as all-string columns, '' coerced to NaN.

    Trims header whitespace (dq-rules rule 7) and validates the schema against
    SOURCE_COLUMNS. Returns a DataFrame with the 22 source columns plus
    source_year. Empty strings become NaN so null handling is uniform.
    """
    path = Path(source_dir) / source_pattern.format(year=year)
    df = pd.read_csv(
        path,
        dtype=str,
        keep_default_na=True,
        na_values=[""],
        skipinitialspace=True,
    )
    df.columns = [c.strip() for c in df.columns]
    missing = [c for c in SOURCE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name}: missing expected columns {missing}")
    df = df[SOURCE_COLUMNS].copy()
    df["source_year"] = int(year)
    return df
