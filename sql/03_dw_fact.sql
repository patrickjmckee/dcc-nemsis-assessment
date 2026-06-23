/* ============================================================================
   03_dw_fact.sql
   NEMSIS Indiana EMS -- Fact table (dw schema)
   Target: SQL Server (T-SQL)

   Grain: one row per EMS run (no natural key in source; one CSV row = one run).
   run_count = 1 per row supports additive aggregation.

   FK rules per SESSION 2 spec:
     NOT NULL: incident_date_key, county_key, complaint_key, flags_key,
               provider_type_key
     NULL:     destination_type_key, disposition_key
   Type 2 FKs point at a specific surrogate version (point-in-time resolved
   by the ETL at load time, not by the database).

   Idempotency: UNIQUE(row_hash, source_year) blocks re-insertion of the same
   source row within the same source file across re-runs.

   Run 02_dw_dimensions.sql before this script (FK dependencies).
   ============================================================================ */

IF OBJECT_ID(N'dw.fact_ems_run', N'U') IS NOT NULL
    DROP TABLE dw.fact_ems_run;
GO

CREATE TABLE dw.fact_ems_run
(
    run_key                     BIGINT          IDENTITY(1,1)   NOT NULL,

    /* ---- Dimension foreign keys ---- */
    incident_date_key           INT             NOT NULL,
    county_key                  INT             NOT NULL,
    complaint_key               INT             NOT NULL,
    flags_key                   INT             NOT NULL,
    provider_type_key           INT             NOT NULL,
    destination_type_key        INT             NULL,
    disposition_key             INT             NULL,

    /* ---- Measures ---- */
    provider_to_scene_mins          INT         NULL,
    provider_to_destination_mins    INT         NULL,
    run_count                       INT         NOT NULL CONSTRAINT DF_fact_ems_run_count DEFAULT (1),

    /* ---- Unit / patient timestamps (validation scoped 2014-2021 in ETL) ---- */
    unit_notified_dt                DATETIME2(0)    NULL,
    unit_arrived_scene_dt           DATETIME2(0)    NULL,
    unit_arrived_patient_dt         DATETIME2(0)    NULL,
    unit_left_scene_dt              DATETIME2(0)    NULL,
    patient_arrived_destination_dt  DATETIME2(0)    NULL,

    /* ---- Degenerate dimension ---- */
    provider_impression_primary     VARCHAR(MAX)    NULL,

    /* ---- Natural key / audit ---- */
    row_hash                        VARCHAR(32)     NOT NULL,
    load_id                         INT             NOT NULL,
    source_year                     INT             NOT NULL,
    quarantine_flag                 BIT             NOT NULL CONSTRAINT DF_fact_ems_run_qflag DEFAULT (0),

    CONSTRAINT PK_fact_ems_run PRIMARY KEY NONCLUSTERED (run_key),

    /* Measure range guards (per dq-rules.md rule 3; NULL allowed) */
    CONSTRAINT CK_fact_scene_mins
        CHECK (provider_to_scene_mins IS NULL
               OR provider_to_scene_mins BETWEEN 0 AND 1440),
    CONSTRAINT CK_fact_dest_mins
        CHECK (provider_to_destination_mins IS NULL
               OR provider_to_destination_mins BETWEEN 0 AND 1440),

    /* Idempotency / de-duplication */
    CONSTRAINT UQ_fact_ems_run_hash UNIQUE (row_hash, source_year),

    /* Foreign keys */
    CONSTRAINT FK_fact_dim_date
        FOREIGN KEY (incident_date_key)     REFERENCES dw.dim_date (incident_date_key),
    CONSTRAINT FK_fact_dim_county
        FOREIGN KEY (county_key)            REFERENCES dw.dim_county (county_key),
    CONSTRAINT FK_fact_dim_complaint
        FOREIGN KEY (complaint_key)         REFERENCES dw.dim_complaint (complaint_key),
    CONSTRAINT FK_fact_dim_run_flags
        FOREIGN KEY (flags_key)             REFERENCES dw.dim_run_flags (flags_key),
    CONSTRAINT FK_fact_dim_provider_type
        FOREIGN KEY (provider_type_key)     REFERENCES dw.dim_provider_type (provider_type_key),
    CONSTRAINT FK_fact_dim_destination_type
        FOREIGN KEY (destination_type_key)  REFERENCES dw.dim_destination_type (destination_type_key),
    CONSTRAINT FK_fact_dim_disposition
        FOREIGN KEY (disposition_key)       REFERENCES dw.dim_disposition (disposition_key)
);
GO

/* Clustered on the most common analytic access path (date + county). */
CREATE CLUSTERED INDEX CIX_fact_ems_run_date_county
    ON dw.fact_ems_run (incident_date_key, county_key);
GO

/* Supports idempotency checks and per-load reconciliation. */
CREATE NONCLUSTERED INDEX IX_fact_ems_run_load
    ON dw.fact_ems_run (load_id, source_year);
GO
