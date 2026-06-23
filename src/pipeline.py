"""Pipeline entry point: orchestrate extract -> stage -> transform -> load for
each source year under a single load_id. Logs run timestamps, row counts, step
status, and errors. Idempotent: re-runs skip already-loaded fact rows."""

import argparse
from datetime import datetime

from extract import read_year
from load import load_dimensions, load_fact, load_quarantine, next_load_id
from stage import stage_dataframe
from transform import transform
from utils import get_connection, get_logger, load_config, load_county_set


def _select_years(cfg):
    """All configured years, or only the load window for incremental mode."""
    years = cfg["paths"]["years"]
    if cfg["etl"]["load_mode"] == "incremental":
        window = cfg["etl"].get("load_window_years") or []
        if window:
            return [y for y in years if y in window]
    return list(years)


def _run_year(conn, cfg, year, load_id, county_set, run_year, logger, totals):
    """Process one source year end to end and accumulate totals."""
    bs = cfg["etl"]["batch_size"]
    df = read_year(cfg["paths"]["source_dir"], cfg["paths"]["source_pattern"], year)
    extracted = len(df)
    staged = stage_dataframe(conn, df, load_id, bs)
    fact, qdf, stats = transform(df, load_id, county_set, run_year)
    quarantined = load_quarantine(conn, qdf, bs)
    fact = load_dimensions(conn, fact, bs)
    inserted, skipped = load_fact(conn, fact, bs)
    logger.info(
        f"year={year} status=OK extracted={extracted} staged={staged} "
        f"rejected={stats['rejected']} quarantined={quarantined} "
        f"fact_inserted={inserted} fact_skipped={skipped} "
        f"injury_repairs={stats['injury_repairs']} ts_repairs={stats['timestamp_repairs']} "
        f"ordering_violations={stats['ordering_violations']} reasons={stats['reject_by_reason']}"
    )
    for key, val in (("extracted", extracted), ("staged", staged),
                     ("rejected", stats["rejected"]), ("inserted", inserted),
                     ("skipped", skipped)):
        totals[key] += val


def run(config_path):
    """Run the full pipeline for all selected years under one load_id."""
    cfg = load_config(config_path)
    conn = get_connection(cfg["db"])
    load_id = next_load_id(conn)
    logger = get_logger(cfg["logging"]["log_dir"], cfg["logging"]["log_level"], load_id)
    county_set = load_county_set(cfg["reference"]["counties_file"])
    years = _select_years(cfg)
    run_year = datetime.now().year
    logger.info(f"START load_id={load_id} env={cfg['env']} "
                f"mode={cfg['etl']['load_mode']} years={years}")
    totals = {"extracted": 0, "staged": 0, "rejected": 0, "inserted": 0, "skipped": 0}
    for year in years:
        try:
            _run_year(conn, cfg, year, load_id, county_set, run_year, logger, totals)
        except Exception as exc:  # noqa: BLE001 -- log and continue to next year
            logger.error(f"year={year} status=FAILED error={exc!r}")
    logger.info(f"DONE load_id={load_id} totals={totals}")
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NEMSIS EMS ETL pipeline")
    parser.add_argument("--config", default="./config/params.yaml")
    run(parser.parse_args().config)
