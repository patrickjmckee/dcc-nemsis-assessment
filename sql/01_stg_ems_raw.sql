/* ============================================================================
   01_stg_ems_raw.sql
   NEMSIS Indiana EMS -- Staging landing table
   Target: SQL Server (T-SQL)

   Purpose: Raw CSV landing for all 12 source years (2014-2025).
            One table, all years, no type inference, no constraints.
            VARCHAR(MAX) for every source column (raw landing only).
            Partitioned by source_year for batch load and switch operations.

   Column names match CSV headers exactly (already trimmed; see dq-rules.md
   rule 7 -- ETL trims header whitespace on ingest before insert).
   ============================================================================ */

IF SCHEMA_ID(N'stg') IS NULL
    EXEC (N'CREATE SCHEMA stg AUTHORIZATION dbo;');
GO

/* ----------------------------------------------------------------------------
   Partitioning: one partition per source year. RANGE RIGHT so each boundary
   value (2014..2025) starts its own partition. Extra empty partitions below
   2014 and above 2025 absorb out-of-range loads without failing.
   ---------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM sys.partition_functions WHERE name = N'pf_ems_year')
    CREATE PARTITION FUNCTION pf_ems_year (INT)
    AS RANGE RIGHT FOR VALUES
        (2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025);
GO

IF NOT EXISTS (SELECT 1 FROM sys.partition_schemes WHERE name = N'ps_ems_year')
    CREATE PARTITION SCHEME ps_ems_year
    AS PARTITION pf_ems_year ALL TO ([PRIMARY]);
GO

/* ----------------------------------------------------------------------------
   Staging table
   ---------------------------------------------------------------------------- */
IF OBJECT_ID(N'stg.stg_ems_raw', N'U') IS NOT NULL
    DROP TABLE stg.stg_ems_raw;
GO

CREATE TABLE stg.stg_ems_raw
(
    INCIDENT_DT                     VARCHAR(MAX)    NULL,
    INCIDENT_COUNTY                 VARCHAR(MAX)    NULL,
    CHIEF_COMPLAINT_DISPATCH        VARCHAR(MAX)    NULL,
    CHIEF_COMPLAINT_ANATOMIC_LOC    VARCHAR(MAX)    NULL,
    PRIMARY_SYMPTOM                 VARCHAR(MAX)    NULL,
    PROVIDER_IMPRESSION_PRIMARY     VARCHAR(MAX)    NULL,
    DISPOSITION_ED                  VARCHAR(MAX)    NULL,
    DISPOSITION_HOSPITAL            VARCHAR(MAX)    NULL,
    INJURY_FLG                      VARCHAR(MAX)    NULL,
    NALOXONE_GIVEN_FLG              VARCHAR(MAX)    NULL,
    MEDICATION_GIVEN_OTHER_FLG      VARCHAR(MAX)    NULL,
    DESTINATION_TYPE                VARCHAR(MAX)    NULL,
    PROVIDER_TYPE_STRUCTURE         VARCHAR(MAX)    NULL,
    PROVIDER_TYPE_SERVICE           VARCHAR(MAX)    NULL,
    PROVIDER_TYPE_SERVICE_LEVEL     VARCHAR(MAX)    NULL,
    PROVIDER_TO_SCENE_MINS          VARCHAR(MAX)    NULL,
    PROVIDER_TO_DESTINATION_MINS    VARCHAR(MAX)    NULL,
    UNIT_NOTIFIED_BY_DISPATCH_DT    VARCHAR(MAX)    NULL,
    UNIT_ARRIVED_ON_SCENE_DT        VARCHAR(MAX)    NULL,
    UNIT_ARRIVED_TO_PATIENT_DT      VARCHAR(MAX)    NULL,
    UNIT_LEFT_SCENE_DT              VARCHAR(MAX)    NULL,
    PATIENT_ARRIVED_DESTINATION_DT  VARCHAR(MAX)    NULL,
    /* Audit / partitioning column populated by ETL from source filename */
    source_year                     INT             NOT NULL,
    load_id                         INT             NOT NULL
)
ON ps_ems_year (source_year);
GO
