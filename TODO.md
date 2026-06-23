# dcc-nemsis-assessment/TODO.md

## Blocked

- [ ] Execute DDL (`/sql/01-04`) against a SQL Server instance, then run `pipeline.py` end-to-end. DB-write paths (dim/fact batch inserts, idempotent re-run skip, partition load) are spec-verified only -- no SQL Server in env. (Session 3, 2026-06-23)
- [ ] Validate fact/quarantine row-count reconciliation and Type 2 dim point-in-time joins against loaded data once a DB is available.

## Next Version

-[] S3 bucket
-[] Databricks DeltaLake

## Enhancements

-[]
