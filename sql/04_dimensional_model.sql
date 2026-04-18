-- =====================================================
-- FLEETLOGIX - DIMENSIONAL MODEL FOR SNOWFLAKE
-- Proyecto Integrador M2 - Henry Data Science
-- =====================================================

-- =====================================================
-- 1. CREATE DATABASE AND SCHEMA
-- =====================================================

CREATE DATABASE IF NOT EXISTS FLEETLOGIX_DW;
CREATE SCHEMA IF NOT EXISTS FLEETLOGIX_DW.ANALYTICS;

USE DATABASE FLEETLOGIX_DW;
USE SCHEMA ANALYTICS;

-- =====================================================
-- 2. DIMENSION TABLES
-- =====================================================

-- -----------------------------------------------------
-- 2.1 Dimension: dim_date
-- Purpose: Calendar dimension for date-based analysis
-- Type: Type 0 (static, never changes)
-- -----------------------------------------------------
CREATE OR REPLACE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_of_week INT,
    day_name VARCHAR(10),
    day_of_month INT,
    day_of_year INT,
    week_of_year INT,
    month_num INT,
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    holiday_name VARCHAR(50),
    fiscal_quarter INT,
    fiscal_year INT
);

-- Insert date data for 5 years
INSERT INTO dim_date (date_key, full_date, day_of_week, day_name, day_of_month, 
                      day_of_year, week_of_year, month_num, month_name, quarter, year,
                      is_weekend, is_holiday, holiday_name, fiscal_quarter, fiscal_year)
SELECT 
    EXTRACT(YEAR FROM d) * 10000 + EXTRACT(MONTH FROM d) * 100 + EXTRACT(DAY FROM d) AS date_key,
    d AS full_date,
    EXTRACT(DOW FROM d) AS day_of_week,
    TO_CHAR(d, 'Day') AS day_name,
    EXTRACT(DAY FROM d) AS day_of_month,
    EXTRACT(DOY FROM d) AS day_of_year,
    EXTRACT(WEEK FROM d) AS week_of_year,
    EXTRACT(MONTH FROM d) AS month_num,
    TO_CHAR(d, 'Month') AS month_name,
    EXTRACT(QUARTER FROM d) AS quarter,
    EXTRACT(YEAR FROM d) AS year,
    CASE WHEN EXTRACT(DOW FROM d) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend,
    FALSE AS is_holiday,
    NULL AS holiday_name,
    CASE WHEN EXTRACT(QUARTER FROM d) IN (1, 2) THEN 2 
         WHEN EXTRACT(QUARTER FROM d) IN (3) THEN 3 
         ELSE 1 END AS fiscal_quarter,
    EXTRACT(YEAR FROM d) AS fiscal_year
FROM GENERATE_SERIES(DATE '2023-01-01', DATE '2028-12-31', INTERVAL '1 day') AS d;

-- -----------------------------------------------------
-- 2.2 Dimension: dim_time
-- Purpose: Time dimension for hour-based analysis
-- Type: Type 0 (static)
-- -----------------------------------------------------
CREATE OR REPLACE TABLE dim_time (
    time_key INT PRIMARY KEY,
    hour INT,
    minute INT,
    second INT,
    time_of_day VARCHAR(20),
    hour_24 VARCHAR(5),
    hour_12 VARCHAR(8),
    am_pm VARCHAR(2),
    is_business_hour BOOLEAN,
    shift VARCHAR(20)
);

-- Insert time data (24 hours)
INSERT INTO dim_time (time_key, hour, minute, second, time_of_day, hour_24, hour_12, am_pm, is_business_hour, shift)
SELECT 
    h * 100 + m AS time_key,
    h AS hour,
    m AS minute,
    0 AS second,
    CASE 
        WHEN h BETWEEN 0 AND 5 THEN 'Madrugada'
        WHEN h BETWEEN 6 AND 11 THEN 'Manana'
        WHEN h BETWEEN 12 AND 17 THEN 'Tarde'
        ELSE 'Noche'
    END AS time_of_day,
    TO_CHAR(TIME '00:00:00' + (h || ':' || m || ':00')::INTERVAL, 'HH24:MI') AS hour_24,
    TO_CHAR(TIME '00:00:00' + (h || ':' || m || ':00')::INTERVAL, 'HH:MI AM') AS hour_12,
    CASE WHEN h < 12 THEN 'AM' ELSE 'PM' END AS am_pm,
    CASE WHEN h BETWEEN 8 AND 18 THEN TRUE ELSE FALSE END AS is_business_hour,
    CASE 
        WHEN h BETWEEN 6 AND 14 THEN 'Turno 1'
        WHEN h BETWEEN 14 AND 22 THEN 'Turno 2'
        ELSE 'Turno 3'
    END AS shift
FROM GENERATE_SERIES(0, 23) AS h
CROSS JOIN GENERATE_SERIES(0, 59) AS m;

-- -----------------------------------------------------
-- 2.3 Dimension: dim_vehicle (SCD Type 2)
-- Purpose: Vehicle dimension with historical tracking
-- Type: Type 2 (tracks changes over time)
-- -----------------------------------------------------
CREATE OR REPLACE TABLE dim_vehicle (
    vehicle_key INT PRIMARY KEY AUTOINCREMENT,
    vehicle_id INT NOT NULL,
    license_plate VARCHAR(20),
    vehicle_type VARCHAR(50),
    capacity_kg DECIMAL(10,2),
    fuel_type VARCHAR(20),
    acquisition_date DATE,
    age_months INT,
    status VARCHAR(20),
    last_maintenance_date DATE,
    valid_from DATE,
    valid_to DATE,
    is_current BOOLEAN
);

-- -----------------------------------------------------
-- 2.4 Dimension: dim_driver (SCD Type 2)
-- Purpose: Driver dimension with historical tracking
-- Type: Type 2 (tracks changes over time)
-- -----------------------------------------------------
CREATE OR REPLACE TABLE dim_driver (
    driver_key INT PRIMARY KEY AUTOINCREMENT,
    driver_id INT NOT NULL,
    employee_code VARCHAR(20),
    full_name VARCHAR(200),
    license_number VARCHAR(50),
    license_expiry DATE,
    phone VARCHAR(20),
    hire_date DATE,
    experience_months INT,
    status VARCHAR(20),
    performance_category VARCHAR(20),
    valid_from DATE,
    valid_to DATE,
    is_current BOOLEAN
);

-- -----------------------------------------------------
-- 2.5 Dimension: dim_route (SCD Type 1)
-- Purpose: Route dimension (mostly static)
-- Type: Type 1 (overwrites on changes)
-- -----------------------------------------------------
CREATE OR REPLACE TABLE dim_route (
    route_key INT PRIMARY KEY AUTOINCREMENT,
    route_id INT NOT NULL,
    route_code VARCHAR(20),
    origin_city VARCHAR(100),
    destination_city VARCHAR(100),
    distance_km DECIMAL(10,2),
    estimated_duration_hours DECIMAL(5,2),
    toll_cost DECIMAL(10,2),
    difficulty_level VARCHAR(20),
    route_type VARCHAR(20),
    region VARCHAR(50)
);

-- -----------------------------------------------------
-- 2.6 Dimension: dim_customer (SCD Type 2)
-- Purpose: Customer dimension with category tracking
-- Type: Type 2 (tracks changes over time)
-- -----------------------------------------------------
CREATE OR REPLACE TABLE dim_customer (
    customer_key INT PRIMARY KEY AUTOINCREMENT,
    customer_id INT NOT NULL,
    customer_name VARCHAR(200),
    customer_type VARCHAR(50),
    city VARCHAR(100),
    first_delivery_date DATE,
    total_deliveries INT,
    customer_category VARCHAR(20),
    valid_from DATE,
    valid_to DATE,
    is_current BOOLEAN
);

-- =====================================================
-- 3. FACT TABLE
-- =====================================================

-- -----------------------------------------------------
-- 3.1 Fact Table: fact_deliveries
-- Purpose: Central fact table for delivery metrics
-- Grain: One row per delivery
-- -----------------------------------------------------
CREATE OR REPLACE TABLE fact_deliveries (
    delivery_key INT PRIMARY KEY AUTOINCREMENT,
    
    -- Dimension Keys
    date_key INT REFERENCES dim_date(date_key),
    scheduled_time_key INT REFERENCES dim_time(time_key),
    delivered_time_key INT REFERENCES dim_time(time_key),
    vehicle_key INT REFERENCES dim_vehicle(vehicle_key),
    driver_key INT REFERENCES dim_driver(driver_key),
    route_key INT REFERENCES dim_route(route_key),
    customer_key INT REFERENCES dim_customer(customer_key),
    
    -- Degenerate Dimensions (direct attributes from source)
    delivery_id INT NOT NULL,
    trip_id INT NOT NULL,
    tracking_number VARCHAR(50),
    
    -- Metrics
    package_weight_kg DECIMAL(10,2),
    distance_km DECIMAL(10,2),
    fuel_consumed_liters DECIMAL(10,2),
    delivery_time_minutes INT,
    delay_minutes INT,
    
    -- Calculated Metrics
    deliveries_per_hour DECIMAL(10,2),
    fuel_efficiency_km_per_liter DECIMAL(10,2),
    cost_per_delivery DECIMAL(10,2),
    revenue_per_delivery DECIMAL(10,2),
    
    -- Indicators
    is_on_time BOOLEAN,
    is_damaged BOOLEAN,
    has_signature BOOLEAN,
    delivery_status VARCHAR(20),
    
    -- Audit Fields
    etl_batch_id INT,
    etl_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================
-- 4. VIEWS FOR BUSINESS LOGIC
-- =====================================================

-- -----------------------------------------------------
-- View: v_delivery_summary
-- Purpose: Aggregated delivery metrics by date
-- -----------------------------------------------------
CREATE OR REPLACE VIEW v_delivery_summary AS
SELECT 
    d.full_date,
    d.year,
    d.quarter,
    d.month_name,
    COUNT(f.delivery_id) AS total_deliveries,
    COUNT(CASE WHEN f.is_on_time THEN 1 END) AS on_time_deliveries,
    ROUND(100.0 * COUNT(CASE WHEN f.is_on_time THEN 1 END) / COUNT(f.delivery_id), 2) AS on_time_rate,
    SUM(f.package_weight_kg) AS total_weight_kg,
    ROUND(AVG(f.delivery_time_minutes), 2) AS avg_delivery_time_minutes,
    SUM(f.revenue_per_delivery) AS total_revenue,
    SUM(f.cost_per_delivery) AS total_cost,
    SUM(f.revenue_per_delivery) - SUM(f.cost_per_delivery) AS profit
FROM fact_deliveries f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.full_date, d.year, d.quarter, d.month_name;

-- -----------------------------------------------------
-- View: v_vehicle_performance
-- Purpose: Vehicle performance metrics
-- -----------------------------------------------------
CREATE OR REPLACE VIEW v_vehicle_performance AS
SELECT 
    v.vehicle_type,
    v.license_plate,
    COUNT(f.delivery_id) AS total_deliveries,
    SUM(f.fuel_consumed_liters) AS total_fuel,
    ROUND(AVG(f.fuel_efficiency_km_per_liter), 2) AS avg_efficiency,
    COUNT(CASE WHEN f.is_on_time THEN 1 END) AS on_time_deliveries,
    ROUND(100.0 * COUNT(CASE WHEN f.is_on_time THEN 1 END) / COUNT(f.delivery_id), 2) AS on_time_rate
FROM fact_deliveries f
JOIN dim_vehicle v ON f.vehicle_key = v.vehicle_key
WHERE v.is_current = TRUE
GROUP BY v.vehicle_type, v.license_plate;

-- -----------------------------------------------------
-- View: v_driver_performance
-- Purpose: Driver performance metrics
-- -----------------------------------------------------
CREATE OR REPLACE VIEW v_driver_performance AS
SELECT 
    d.full_name,
    d.employee_code,
    d.performance_category,
    COUNT(f.delivery_id) AS total_deliveries,
    SUM(f.package_weight_kg) AS total_weight_delivered,
    ROUND(AVG(f.delivery_time_minutes), 2) AS avg_delivery_time,
    COUNT(CASE WHEN f.is_on_time THEN 1 END) AS on_time_deliveries,
    ROUND(100.0 * COUNT(CASE WHEN f.is_on_time THEN 1 END) / COUNT(f.delivery_id), 2) AS on_time_rate
FROM fact_deliveries f
JOIN dim_driver d ON f.driver_key = d.driver_key
WHERE d.is_current = TRUE
GROUP BY d.full_name, d.employee_code, d.performance_category;

-- =====================================================
-- 5. STORED PROCEDURES FOR ETL
-- =====================================================

-- -----------------------------------------------------
-- Procedure: sp_load_dim_date
-- Purpose: Populate dim_date with calendar data
-- -----------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_load_dim_date(start_year INT, end_year INT)
LANGUAGE PYTHON
RUNTIME = 'PYTHON 3.10'
AS $$
import snowflake.connector
from datetime import date, timedelta

conn = snowflake.connector.connect(
    user='YOUR_USER',
    password='YOUR_PASSWORD',
    account='YOUR_ACCOUNT'
)

cursor = conn.cursor()

# Generate date range
start_date = date(start_year, 1, 1)
end_date = date(end_year, 12, 31)

current_date = start_date
while current_date <= end_date:
    date_key = current_date.year * 10000 + current_date.month * 100 + current_date.day
    day_of_week = current_date.weekday()
    day_name = current_date.strftime('%A')
    
    cursor.execute("""
        INSERT INTO dim_date VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        date_key, current_date, day_of_week, day_name,
        current_date.day, current_date.timetuple().tm_yday,
        current_date.isocalendar()[1], current_date.month,
        current_date.strftime('%B'), current_date.month,
        current_date.year, day_of_week in (5, 6),
        False, None, (current_date.month - 1) // 3 + 1,
        current_date.year
    ))
    current_date += timedelta(days=1)

conn.commit()
cursor.close()
conn.close()
$$;

-- =====================================================
-- 6. MATERIALIZED VIEWS FOR PERFORMANCE
-- =====================================================

-- -----------------------------------------------------
-- Materialized View: mv_daily_deliveries
-- Purpose: Daily aggregated metrics for fast dashboards
-- -----------------------------------------------------
CREATE OR REPLACE MATERIALIZED VIEW mv_daily_deliveries AS
SELECT 
    d.date_key,
    d.full_date,
    d.day_name,
    d.month_name,
    d.year,
    COUNT(f.delivery_id) AS delivery_count,
    COUNT(CASE WHEN f.is_on_time THEN 1 END) AS on_time_count,
    ROUND(100.0 * COUNT(CASE WHEN f.is_on_time THEN 1 END) / COUNT(f.delivery_id), 2) AS on_time_rate,
    SUM(f.package_weight_kg) AS total_weight,
    SUM(f.revenue_per_delivery) AS total_revenue,
    SUM(f.cost_per_delivery) AS total_cost
FROM fact_deliveries f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.date_key, d.full_date, d.day_name, d.month_name, d.year;

-- =====================================================
-- 7. ROW ACCESS POLICY ( SECURITY )
-- =====================================================

-- -----------------------------------------------------
-- Row Access Policy: Restrict data by role
-- Purpose: Security policy for multi-tenant access
-- -----------------------------------------------------
CREATE OR REPLACE ROW ACCESS POLICY rap_fleet_access
AS (user_role VARCHAR) RETURNS BOOLEAN
FOR SELECT TO
USING (
    -- Admins can see all data
    user_role = 'FLEET_ADMIN'
    OR
    -- Managers see their region
    (user_role = 'FLEET_MANAGER' AND dim_route.region IN ('BOGOTA', 'MEDELLIN'))
    OR
    -- Drivers see only their deliveries
    (user_role = 'DRIVER' AND dim_driver.driver_id = CURRENT_USER())
);

-- =====================================================
-- 8. DATA MASKING POLICIES
-- =====================================================

-- -----------------------------------------------------
-- Dynamic Data Masking: Protect sensitive fields
-- Purpose: Mask PII data for non-privileged users
-- -----------------------------------------------------
CREATE OR REPLACE MASKING POLICY mask_phone_number
AS (val VARCHAR) RETURNS VARCHAR
CASE 
    WHEN CURRENT_ROLE() IN ('FLEET_ADMIN', 'FLEET_MANAGER') THEN val
    ELSE CONCAT('***-***-', RIGHT(val, 4))
END;

-- Apply masking to sensitive columns
ALTER TABLE dim_driver MODIFY COLUMN phone
SET MASKING POLICY mask_phone_number;

-- =====================================================
-- 9. CLONE FOR DEV/TEST ENVIRONMENTS
-- =====================================================

-- Clone production database to development
-- CREATE OR REPLACE TABLE FLEETLOGIX_DW.ANALYTICS.fact_deliveries_dev
-- CLONE FLEETLOGIX_DW.ANALYTICS.fact_deliveries;

-- =====================================================
-- 10. SHOW TABLES IN WAREHOUSE
-- =====================================================
SHOW TABLES;
