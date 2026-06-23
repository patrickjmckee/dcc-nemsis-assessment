/* ============================================================================
   04_stg_ems_quarantine.sql
   NEMSIS Indiana EMS -- Reject / quarantine table (stg schema)
   Target: SQL Server (T-SQL)

   Holds rows rejected by ETL validation (per dq-rules.md reject criteria):
     INCIDENT_DT_NULL, INCIDENT_COUNTY_INVALID,
     DURATION_MINS_OUT_OF_RANGE, FLAG_INVALID, ...
   Stores the raw source columns verbatim (varchar(MAX)) so a row can be
   inspected, corrected, and re-loaded.

   Idempotency: PK (load_id, source_year, row_hash) prevents re-quarantining
   the same row within the same run.

   Run 01_stg_ems_raw.sql first (shares the stg schema).
   ============================================================================ */

IF SCHEMA_ID(N'stg') IS NULL
    EXEC (N'CREATE SCHEMA stg AUTHORIZATION dbo;');
GO

IF OBJECT_ID(N'stg.stg_ems_quarantine', N'U') IS NOT NULL
    DROP TABLE stg.stg_ems_quarantine;
GO

CREATE TABLE stg.stg_ems_quarantine
(
    /* ---- Raw source columns (verbatim, untyped) ---- */
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

    /* ---- Quarantine metadata ---- */
    row_hash                VARCHAR(32)     NOT NULL,
    quarantine_reason       VARCHAR(500)    NOT NULL,
    load_id                 INT             NOT NULL,
    quarantine_timestamp    DATETIME2(3)    NOT NULL
                            CONSTRAINT DF_quarantine_ts DEFAULT (SYSUTCDATETIME()),
    source_year             INT             NOT NULL,

    CONSTRAINT PK_stg_ems_quarantine
        PRIMARY KEY CLUSTERED (load_id, source_year, row_hash)
);
GO

CREATE NONCLUSTERED INDEX IX_quarantine_reason_ts
    ON stg.stg_ems_quarantine (quarantine_reason, quarantine_timestamp);
GO
