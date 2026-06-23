"""Pipeline entry point: orchestrate extract -> stage -> transform -> load for
each source year under a single load_id. Logs run timestamps, row counts, step
status, and errors. Idempotent: re-runs skip already-loaded fact rows."""

import argparse
from collections import Counter
from datetime import datetime

from extract import read_year_chunks
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


def _process_chunk(conn, chunk, load_id, county_set, run_year, batch_size, acc):
    """Stage, transform, and load one chunk; fold counts into the accumulator."""
    acc["extracted"] += len(chunk)
    acc["staged"] += stage_dataframe(conn, chunk, load_id, batch_size)
    fact, qdf, stats = transform(chunk, load_id, county_set, run_year)
    acc["quarantined"] += load_quarantine(conn, qdf, batch_size)
    fact = load_dimensions(conn, fact, batch_size)
    inserted, skipped = load_fact(conn, fact, batch_size)
    acc["inserted"] += inserted
    acc["skipped"] += skipped
    acc["rejected"] += stats["rejected"]
    acc["injury_repairs"] += stats["injury_repairs"]
    acc["timestamp_repairs"] += stats["timestamp_repairs"]
    if stats["ordering_violations"]:
        acc["ordering"] += stats["ordering_violations"]
    acc["reasons"].update(stats["reject_by_reason"])


def _run_year(conn, cfg, year, load_id, county_set, run_year, logger, totals):
    """Stream one source year in chunks and accumulate totals."""
    bs = cfg["etl"]["batch_size"]
    chunk_size = cfg["etl"].get("read_chunk_size") or bs * 20
    acc = {k: 0 for k in ("extracted", "staged", "rejected", "inserted",
                          "skipped", "quarantined", "injury_repairs",
                          "timestamp_repairs", "ordering")}
    acc["reasons"] = Counter()
    for chunk in read_year_chunks(cfg["paths"]["source_dir"],
                                  cfg["paths"]["source_pattern"], year, chunk_size):
        _process_chunk(conn, chunk, load_id, county_set, run_year, bs, acc)
    ordering = acc["ordering"] if 2014 <= year <= 2021 else None
    logger.info(
        f"year={year} status=OK extracted={acc['extracted']} staged={acc['staged']} "
        f"rejected={acc['rejected']} quarantined={acc['quarantined']} "
        f"fact_inserted={acc['inserted']} fact_skipped={acc['skipped']} "
        f"injury_repairs={acc['injury_repairs']} ts_repairs={acc['timestamp_repairs']} "
        f"ordering_violations={ordering} reasons={dict(acc['reasons'])}"
    )
    for key in ("extracted", "staged", "rejected", "inserted", "skipped"):
        totals[key] += acc[key]


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
