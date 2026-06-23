/* ============================================================================
   02_dw_dimensions.sql
   NEMSIS Indiana EMS -- Warehouse dimension tables (dw schema)
   Target: SQL Server (T-SQL)

   Kimball dimensional model. Surrogate keys = INT IDENTITY.
   SCD strategy:
     Type 1 (overwrite, stable attributes): dim_date, dim_county,
             dim_complaint, dim_run_flags
     Type 2 (history, code-list drift):     dim_provider_type,
             dim_destination_type, dim_disposition

   Type 2 mechanics (row_hash / valid_from / valid_to / is_current) are
   computed by the ETL, not the DDL. See decisions.md for rationale.
   ============================================================================ */

IF SCHEMA_ID(N'dw') IS NULL
    EXEC (N'CREATE SCHEMA dw AUTHORIZATION dbo;');
GO

/* ============================================================================
   TYPE 1 DIMENSIONS
   ============================================================================ */

/* ---- dim_date (Type 1) --------------------------------------------------- */
IF OBJECT_ID(N'dw.dim_date', N'U') IS NOT NULL
    DROP TABLE dw.dim_date;
GO
CREATE TABLE dw.dim_date
(
    incident_date_key   INT             IDENTITY(1,1)   NOT NULL,
    incident_date       DATE            NOT NULL,
    [year]              SMALLINT        NOT NULL,
    [month]             TINYINT         NOT NULL,
    [quarter]           TINYINT         NOT NULL,
    day_of_week         TINYINT         NOT NULL,
    CONSTRAINT PK_dim_date PRIMARY KEY CLUSTERED (incident_date_key),
    CONSTRAINT UQ_dim_date_incident_date UNIQUE (incident_date)
);
GO
CREATE NONCLUSTERED INDEX IX_dim_date_incident_date
    ON dw.dim_date (incident_date);
GO

/* ---- dim_county (Type 1) ------------------------------------------------- */
/* county_name is the natural key and stores the normalized form
   (uppercase, trimmed, periods stripped) produced by the ETL. */
IF OBJECT_ID(N'dw.dim_county', N'U') IS NOT NULL
    DROP TABLE dw.dim_county;
GO
CREATE TABLE dw.dim_county
(
    county_key      INT             IDENTITY(1,1)   NOT NULL,
    county_name     VARCHAR(100)    NOT NULL,
    CONSTRAINT PK_dim_county PRIMARY KEY NONCLUSTERED (county_key),
    CONSTRAINT UQ_dim_county_name UNIQUE (county_name)
);
GO
/* Clustered on the natural key for fast lookup during fact load. */
CREATE CLUSTERED INDEX CIX_dim_county_name
    ON dw.dim_county (county_name);
GO

/* ---- dim_complaint (Type 2) ---------------------------------------------- */
/* Natural-key columns are NOT NULL DEFAULT '' (empty string).                 */
/* ETL coerces NULL source values to '' before insert and hash computation.    */
/* This allows UNIQUE(natural_key, valid_from) without nullable-column issues. */
/* valid_from = INCIDENT_DT of the first run containing this complaint tuple.  */
IF OBJECT_ID(N'dw.dim_complaint', N'U') IS NOT NULL
    DROP TABLE dw.dim_complaint;
GO
CREATE TABLE dw.dim_complaint
(
    complaint_key               INT             IDENTITY(1,1)   NOT NULL,
    chief_complaint_dispatch    VARCHAR(255)    NOT NULL    CONSTRAINT DF_complaint_dispatch    DEFAULT (''),
    anatomic_location           VARCHAR(255)    NOT NULL    CONSTRAINT DF_complaint_anatomic    DEFAULT (''),
    primary_symptom             VARCHAR(255)    NOT NULL    CONSTRAINT DF_complaint_symptom     DEFAULT (''),
    row_hash                    VARCHAR(32)     NOT NULL,
    valid_from                  DATE            NOT NULL,
    valid_to                    DATE            NULL,
    is_current                  BIT             NOT NULL,
    CONSTRAINT PK_dim_complaint PRIMARY KEY NONCLUSTERED (complaint_key),
    CONSTRAINT UQ_dim_complaint_version
        UNIQUE (chief_complaint_dispatch, anatomic_location, primary_symptom, valid_from)
);
GO
CREATE CLUSTERED INDEX CIX_dim_complaint_pit
    ON dw.dim_complaint (chief_complaint_dispatch, anatomic_location, primary_symptom, valid_to DESC);
GO

/* ---- dim_run_flags (Type 1 junk dimension) ------------------------------- */
IF OBJECT_ID(N'dw.dim_run_flags', N'U') IS NOT NULL
    DROP TABLE dw.dim_run_flags;
GO
CREATE TABLE dw.dim_run_flags
(
    flags_key       INT             IDENTITY(1,1)   NOT NULL,
    injury_flag     VARCHAR(10)     NOT NULL,
    naloxone_flag   VARCHAR(1)      NOT NULL,
    medication_flag VARCHAR(1)      NOT NULL,
    CONSTRAINT PK_dim_run_flags PRIMARY KEY CLUSTERED (flags_key),
    CONSTRAINT UQ_dim_run_flags UNIQUE (injury_flag, naloxone_flag, medication_flag)
);
GO

/* ============================================================================
   TYPE 2 DIMENSIONS
   row_hash: varchar(32) MD5 of natural-key attributes, set by ETL.
   valid_to: NULL when is_current = 1; else (next valid_from - 1 day).
   UNIQUE(natural_key, valid_from) blocks duplicate versions on one date.
   ============================================================================ */

/* ---- dim_provider_type (Type 2) ------------------------------------------ */
IF OBJECT_ID(N'dw.dim_provider_type', N'U') IS NOT NULL
    DROP TABLE dw.dim_provider_type;
GO
CREATE TABLE dw.dim_provider_type
(
    provider_type_key   INT             IDENTITY(1,1)   NOT NULL,
    [structure]         VARCHAR(100)    NOT NULL,
    [service]           VARCHAR(100)    NOT NULL,
    [level]             VARCHAR(100)    NOT NULL,
    row_hash            VARCHAR(32)     NOT NULL,
    valid_from          DATE            NOT NULL,
    valid_to            DATE            NULL,
    is_current          BIT             NOT NULL,
    CONSTRAINT PK_dim_provider_type PRIMARY KEY NONCLUSTERED (provider_type_key),
    CONSTRAINT UQ_dim_provider_type_version
        UNIQUE ([structure], [service], [level], valid_from)
);
GO
CREATE CLUSTERED INDEX CIX_dim_provider_type_pit
    ON dw.dim_provider_type ([structure], [service], [level], valid_to DESC);
GO

/* ---- dim_destination_type (Type 2) --------------------------------------- */
IF OBJECT_ID(N'dw.dim_destination_type', N'U') IS NOT NULL
    DROP TABLE dw.dim_destination_type;
GO
CREATE TABLE dw.dim_destination_type
(
    destination_type_key    INT             IDENTITY(1,1)   NOT NULL,
    destination_code        VARCHAR(100)    NOT NULL,
    row_hash                VARCHAR(32)     NOT NULL,
    valid_from              DATE            NOT NULL,
    valid_to                DATE            NULL,
    is_current              BIT             NOT NULL,
    CONSTRAINT PK_dim_destination_type PRIMARY KEY NONCLUSTERED (destination_type_key),
    CONSTRAINT UQ_dim_destination_type_version
        UNIQUE (destination_code, valid_from)
);
GO
CREATE CLUSTERED INDEX CIX_dim_destination_type_pit
    ON dw.dim_destination_type (destination_code, valid_to DESC);
GO

/* ---- dim_disposition (Type 2) -------------------------------------------- */
IF OBJECT_ID(N'dw.dim_disposition', N'U') IS NOT NULL
    DROP TABLE dw.dim_disposition;
GO
CREATE TABLE dw.dim_disposition
(
    disposition_key     INT             IDENTITY(1,1)   NOT NULL,
    disposition_ed      VARCHAR(255)    NOT NULL,
    disposition_hospital VARCHAR(255)   NOT NULL,
    row_hash            VARCHAR(32)     NOT NULL,
    valid_from          DATE            NOT NULL,
    valid_to            DATE            NULL,
    is_current          BIT             NOT NULL,
    CONSTRAINT PK_dim_disposition PRIMARY KEY NONCLUSTERED (disposition_key),
    CONSTRAINT UQ_dim_disposition_version
        UNIQUE (disposition_ed, disposition_hospital, valid_from)
);
GO
CREATE CLUSTERED INDEX CIX_dim_disposition_pit
    ON dw.dim_disposition (disposition_ed, disposition_hospital, valid_to DESC);
GO
