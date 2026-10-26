-- =====================================================================
-- FLEETLOGIX · DIMENSIÓN CALENDARIO (TABLA FÍSICA)
-- ---------------------------------------------------------------------
-- Alternativa a la vista v_dim_date: crea una TABLA materializada con
-- todos los atributos de calendario. Recomendada para dashboards porque
-- tiene mejor performance que la vista recursiva.
-- =====================================================================

DROP TABLE IF EXISTS dim_date CASCADE;

CREATE TABLE dim_date (
    date_key          INT         PRIMARY KEY,         -- YYYYMMDD (int)
    date              DATE        UNIQUE NOT NULL,
    year              SMALLINT    NOT NULL,
    quarter           SMALLINT    NOT NULL,
    quarter_name      VARCHAR(5)  NOT NULL,            -- Q1, Q2, Q3, Q4
    month             SMALLINT    NOT NULL,
    month_name        VARCHAR(20) NOT NULL,
    month_short       VARCHAR(5)  NOT NULL,
    year_month        CHAR(7)     NOT NULL,            -- YYYY-MM
    week_of_year      SMALLINT    NOT NULL,
    day_of_month      SMALLINT    NOT NULL,
    day_of_year       SMALLINT    NOT NULL,
    day_of_week       SMALLINT    NOT NULL,            -- 0 = Sun
    day_name          VARCHAR(15) NOT NULL,
    day_name_short    VARCHAR(5)  NOT NULL,
    is_weekend        BOOLEAN     NOT NULL,
    is_weekday        BOOLEAN     NOT NULL,
    is_month_start    BOOLEAN     NOT NULL,
    is_month_end      BOOLEAN     NOT NULL,
    is_quarter_start  BOOLEAN     NOT NULL,
    is_quarter_end    BOOLEAN     NOT NULL,
    is_year_start     BOOLEAN     NOT NULL,
    is_year_end       BOOLEAN     NOT NULL
);

INSERT INTO dim_date
SELECT
    TO_CHAR(d, 'YYYYMMDD')::int,
    d,
    EXTRACT(YEAR    FROM d)::smallint,
    EXTRACT(QUARTER FROM d)::smallint,
    'Q' || EXTRACT(QUARTER FROM d)::text,
    EXTRACT(MONTH   FROM d)::smallint,
    TO_CHAR(d, 'TMMonth'),
    TO_CHAR(d, 'TMMon'),
    TO_CHAR(d, 'YYYY-MM'),
    EXTRACT(WEEK    FROM d)::smallint,
    EXTRACT(DAY     FROM d)::smallint,
    EXTRACT(DOY     FROM d)::smallint,
    EXTRACT(DOW     FROM d)::smallint,
    TO_CHAR(d, 'TMDay'),
    TO_CHAR(d, 'TMDy'),
    EXTRACT(DOW FROM d) IN (0, 6),
    EXTRACT(DOW FROM d) NOT IN (0, 6),
    d = DATE_TRUNC('month',   d),
    d = (DATE_TRUNC('month',   d) + INTERVAL '1 month - 1 day')::date,
    d = DATE_TRUNC('quarter', d),
    d = (DATE_TRUNC('quarter', d) + INTERVAL '3 months - 1 day')::date,
    d = DATE_TRUNC('year',    d),
    d = (DATE_TRUNC('year',    d) + INTERVAL '1 year - 1 day')::date
FROM generate_series(DATE '2024-01-01', DATE '2027-12-31', INTERVAL '1 day') AS d;

CREATE INDEX idx_dim_date_year_month ON dim_date(year, month);
CREATE INDEX idx_dim_date_year       ON dim_date(year);

COMMENT ON TABLE dim_date IS 'Dimensión calendario 2024-2027 para análisis de series temporales en Streamlit/Plotly';

-- Verificación
SELECT COUNT(*) AS total_days, MIN(date) AS start_date, MAX(date) AS end_date FROM dim_date;
