-- =====================================================================
-- FLEETLOGIX · VISTAS ANALÍTICAS (capa de servicio del dashboard)
-- ---------------------------------------------------------------------
-- Archivo: dashboard/sql/01_vistas_analiticas.sql
-- Propósito: crear 8 vistas optimizadas que la app Streamlit consume
--            (dashboard_streamlit/streamlit_app.py + pages/) para
--            alimentar las 5 páginas del dashboard ejecutivo.
-- Ejecutar contra: fleetlogix_db (PostgreSQL 15)
-- Autor: Dody Dueñas — Proyecto Integrador M2 · Henry DS
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- VISTA 1 · v_kpi_executive
-- KPIs globales para las tarjetas del Resumen Ejecutivo
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS v_kpi_executive CASCADE;
CREATE VIEW v_kpi_executive AS
SELECT
    (SELECT COUNT(*) FROM vehicles  WHERE status = 'active')                       AS active_vehicles,
    (SELECT COUNT(*) FROM drivers   WHERE status = 'active')                       AS active_drivers,
    (SELECT COUNT(*) FROM trips     WHERE status = 'completed')                    AS completed_trips,
    (SELECT COUNT(*) FROM deliveries WHERE delivery_status = 'delivered')          AS delivered,
    (SELECT COUNT(*) FROM deliveries WHERE delivery_status = 'pending')            AS pending_deliveries,
    (SELECT COUNT(*) FROM deliveries WHERE delivery_status = 'failed')             AS failed_deliveries,
    (SELECT ROUND(AVG(fuel_consumed_liters)::numeric, 2)
       FROM trips WHERE fuel_consumed_liters IS NOT NULL)                          AS avg_fuel_per_trip,
    (SELECT ROUND(SUM(package_weight_kg)::numeric / 1000, 2) FROM deliveries)      AS total_tons,
    (SELECT ROUND(SUM(cost)::numeric, 2) FROM maintenance)                         AS total_maintenance_cost,
    (SELECT COUNT(*) FROM maintenance
       WHERE next_maintenance_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days')
                                                                                   AS vehicles_maintenance_30d,
    (SELECT ROUND(
             100.0 * COUNT(*) FILTER (
               WHERE delivered_datetime <= scheduled_datetime + INTERVAL '30 minutes')
             / NULLIF(COUNT(*) FILTER (WHERE delivery_status = 'delivered'), 0)
           , 2)
       FROM deliveries
       WHERE delivery_status = 'delivered' AND delivered_datetime IS NOT NULL)     AS on_time_rate_pct,
    CURRENT_TIMESTAMP                                                              AS last_refresh;

COMMENT ON VIEW v_kpi_executive IS 'KPIs globales para las tarjetas del Resumen Ejecutivo (dashboard Streamlit)';


-- ---------------------------------------------------------------------
-- VISTA 2 · v_deliveries_timeseries
-- Serie temporal de entregas por día (para line chart)
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS v_deliveries_timeseries CASCADE;
CREATE VIEW v_deliveries_timeseries AS
SELECT
    DATE(scheduled_datetime)                                            AS fecha,
    COUNT(*)                                                            AS total_deliveries,
    COUNT(*) FILTER (WHERE delivery_status = 'delivered')               AS delivered,
    COUNT(*) FILTER (WHERE delivery_status = 'pending')                 AS pending,
    COUNT(*) FILTER (WHERE delivery_status = 'failed')                  AS failed,
    COUNT(*) FILTER (WHERE delivery_status = 'cancelled')               AS cancelled,
    COUNT(*) FILTER (WHERE delivery_status = 'in_transit')              AS in_transit,
    ROUND(AVG(package_weight_kg)::numeric, 2)                           AS avg_package_weight_kg,
    ROUND(SUM(package_weight_kg)::numeric, 2)                           AS total_weight_kg
FROM deliveries
WHERE scheduled_datetime IS NOT NULL
GROUP BY DATE(scheduled_datetime);

COMMENT ON VIEW v_deliveries_timeseries IS 'Serie temporal diaria de entregas por estado para line/area charts';


-- ---------------------------------------------------------------------
-- VISTA 3 · v_vehicle_performance
-- Rendimiento por vehículo (para tabla + scatter)
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS v_vehicle_performance CASCADE;
CREATE VIEW v_vehicle_performance AS
SELECT
    v.vehicle_id,
    v.license_plate,
    v.vehicle_type,
    v.capacity_kg,
    v.fuel_type,
    v.status                                                            AS vehicle_status,
    COUNT(t.trip_id)                                                    AS total_trips,
    COUNT(t.trip_id) FILTER (WHERE t.status = 'completed')              AS completed_trips,
    ROUND(SUM(t.fuel_consumed_liters)::numeric, 2)                      AS total_fuel_liters,
    ROUND(AVG(t.fuel_consumed_liters)::numeric, 2)                      AS avg_fuel_per_trip,
    ROUND(SUM(t.total_weight_kg)::numeric, 2)                           AS total_weight_kg,
    ROUND(AVG(t.total_weight_kg / NULLIF(v.capacity_kg, 0) * 100)::numeric, 2)
                                                                         AS avg_capacity_utilization_pct,
    ROUND(
        SUM(t.fuel_consumed_liters)::numeric
        / NULLIF(SUM(r.distance_km), 0) * 100
      , 2)                                                              AS fuel_efficiency_l_per_100km
FROM vehicles v
LEFT JOIN trips  t ON v.vehicle_id = t.vehicle_id
LEFT JOIN routes r ON t.route_id    = r.route_id
GROUP BY v.vehicle_id, v.license_plate, v.vehicle_type, v.capacity_kg, v.fuel_type, v.status;

COMMENT ON VIEW v_vehicle_performance IS 'Métricas de rendimiento agregadas por vehículo (una fila por vehículo)';


-- ---------------------------------------------------------------------
-- VISTA 4 · v_driver_performance
-- Rendimiento por conductor (para bar chart top-N)
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS v_driver_performance CASCADE;
CREATE VIEW v_driver_performance AS
SELECT
    d.driver_id,
    d.employee_code,
    d.first_name,
    d.last_name,
    d.first_name || ' ' || d.last_name                                  AS full_name,
    d.license_expiry,
    d.hire_date,
    d.status                                                            AS driver_status,
    COUNT(t.trip_id)                                                    AS total_trips,
    COUNT(t.trip_id) FILTER (WHERE t.status = 'completed')              AS completed_trips,
    COUNT(del.delivery_id)                                              AS total_deliveries,
    COUNT(del.delivery_id) FILTER (WHERE del.delivery_status = 'delivered')
                                                                         AS successful_deliveries,
    ROUND(
        100.0 * COUNT(del.delivery_id) FILTER (WHERE del.delivery_status = 'delivered')
        / NULLIF(COUNT(del.delivery_id), 0)
      , 2)                                                              AS success_rate_pct,
    ROUND(SUM(t.fuel_consumed_liters)::numeric, 2)                      AS total_fuel_liters,
    CASE
        WHEN d.license_expiry <= CURRENT_DATE                 THEN 'VENCIDA'
        WHEN d.license_expiry <= CURRENT_DATE + INTERVAL '30 days' THEN 'POR VENCER'
        ELSE 'VIGENTE'
    END                                                                  AS license_status
FROM drivers d
LEFT JOIN trips      t   ON d.driver_id = t.driver_id
LEFT JOIN deliveries del ON t.trip_id   = del.trip_id
GROUP BY d.driver_id, d.employee_code, d.first_name, d.last_name, d.license_expiry, d.hire_date, d.status;

COMMENT ON VIEW v_driver_performance IS 'KPIs por conductor para ranking y alertas de licencia';


-- ---------------------------------------------------------------------
-- VISTA 5 · v_route_traffic
-- Tráfico por ruta (para mapa / tabla de rutas top)
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS v_route_traffic CASCADE;
CREATE VIEW v_route_traffic AS
SELECT
    r.route_id,
    r.route_code,
    r.origin_city,
    r.destination_city,
    r.origin_city || ' → ' || r.destination_city                        AS route_label,
    r.distance_km,
    r.estimated_duration_hours,
    r.toll_cost,
    COUNT(t.trip_id)                                                    AS trip_count,
    COUNT(DISTINCT t.vehicle_id)                                        AS distinct_vehicles,
    COUNT(DISTINCT t.driver_id)                                         AS distinct_drivers,
    COUNT(del.delivery_id)                                              AS total_deliveries,
    ROUND(SUM(t.fuel_consumed_liters)::numeric, 2)                      AS total_fuel_liters,
    ROUND(AVG(t.fuel_consumed_liters)::numeric, 2)                      AS avg_fuel_per_trip,
    ROUND(
        SUM(t.fuel_consumed_liters)::numeric
        / NULLIF(SUM(r.distance_km), 0) * 100
      , 2)                                                              AS fuel_efficiency_l_per_100km
FROM routes r
LEFT JOIN trips      t   ON r.route_id = t.route_id
LEFT JOIN deliveries del ON t.trip_id  = del.trip_id
GROUP BY r.route_id, r.route_code, r.origin_city, r.destination_city,
         r.distance_km, r.estimated_duration_hours, r.toll_cost;

COMMENT ON VIEW v_route_traffic IS 'Volumen de tráfico y consumo por ruta (una fila por ruta)';


-- ---------------------------------------------------------------------
-- VISTA 6 · v_maintenance_alerts
-- Alertas de mantenimiento (para tabla en página de Flota)
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS v_maintenance_alerts CASCADE;
CREATE VIEW v_maintenance_alerts AS
SELECT
    v.vehicle_id,
    v.license_plate,
    v.vehicle_type,
    v.status                                                            AS vehicle_status,
    m.maintenance_id,
    m.maintenance_date,
    m.maintenance_type,
    m.description,
    m.cost,
    m.next_maintenance_date,
    m.performed_by,
    (m.next_maintenance_date - CURRENT_DATE)                            AS days_until_maintenance,
    CASE
        WHEN m.next_maintenance_date <  CURRENT_DATE                       THEN 'VENCIDO'
        WHEN m.next_maintenance_date <= CURRENT_DATE + INTERVAL '7 days'   THEN 'ESTA SEMANA'
        WHEN m.next_maintenance_date <= CURRENT_DATE + INTERVAL '30 days'  THEN 'ESTE MES'
        ELSE 'OK'
    END                                                                  AS alert_level
FROM maintenance m
JOIN vehicles v ON m.vehicle_id = v.vehicle_id
WHERE m.next_maintenance_date IS NOT NULL;

COMMENT ON VIEW v_maintenance_alerts IS 'Alertas de próximos mantenimientos con semaforización';


-- ---------------------------------------------------------------------
-- VISTA 7 · v_fuel_efficiency
-- Eficiencia de combustible agregada por mes y tipo de vehículo
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS v_fuel_efficiency CASCADE;
CREATE VIEW v_fuel_efficiency AS
SELECT
    DATE_TRUNC('month', t.departure_datetime)::date                     AS month,
    v.vehicle_type,
    v.fuel_type,
    COUNT(t.trip_id)                                                    AS trip_count,
    ROUND(SUM(t.fuel_consumed_liters)::numeric, 2)                      AS total_fuel_liters,
    ROUND(AVG(t.fuel_consumed_liters)::numeric, 2)                      AS avg_fuel_per_trip,
    ROUND(SUM(r.distance_km)::numeric, 2)                               AS total_distance_km,
    ROUND(
        SUM(t.fuel_consumed_liters)::numeric
        / NULLIF(SUM(r.distance_km), 0) * 100
      , 2)                                                              AS fuel_efficiency_l_per_100km
FROM trips    t
JOIN vehicles v ON t.vehicle_id = v.vehicle_id
JOIN routes   r ON t.route_id   = r.route_id
WHERE t.status = 'completed'
GROUP BY DATE_TRUNC('month', t.departure_datetime), v.vehicle_type, v.fuel_type;

COMMENT ON VIEW v_fuel_efficiency IS 'Eficiencia de combustible mensual por tipo de vehículo y combustible';


-- ---------------------------------------------------------------------
-- VISTA 8 · v_dim_date
-- Dimensión calendario para análisis de series temporales en el dashboard
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS v_dim_date CASCADE;
CREATE VIEW v_dim_date AS
WITH RECURSIVE date_range AS (
    SELECT DATE '2024-01-01' AS d
    UNION ALL
    SELECT d + INTERVAL '1 day' FROM date_range WHERE d < DATE '2027-12-31'
)
SELECT
    d::date                                                             AS date,
    EXTRACT(YEAR    FROM d)::int                                        AS year,
    EXTRACT(QUARTER FROM d)::int                                        AS quarter,
    EXTRACT(MONTH   FROM d)::int                                        AS month,
    TO_CHAR(d, 'YYYY-MM')                                               AS year_month,
    TO_CHAR(d, 'TMMonth')                                               AS month_name,
    EXTRACT(WEEK    FROM d)::int                                        AS week_of_year,
    EXTRACT(DAY     FROM d)::int                                        AS day_of_month,
    EXTRACT(DOW     FROM d)::int                                        AS day_of_week,
    TO_CHAR(d, 'TMDay')                                                 AS day_name,
    CASE WHEN EXTRACT(DOW FROM d) IN (0,6) THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    CASE WHEN d = CURRENT_DATE THEN 1 ELSE 0 END                        AS is_today
FROM date_range;

COMMENT ON VIEW v_dim_date IS 'Dimensión calendario 2024-2027 para análisis de series temporales en Streamlit/Plotly';


-- ---------------------------------------------------------------------
-- VERIFICACIÓN
-- ---------------------------------------------------------------------
SELECT
    schemaname AS schema,
    viewname   AS view_name,
    definition IS NOT NULL AS defined
FROM pg_views
WHERE schemaname = 'public'
  AND viewname LIKE 'v_%'
ORDER BY viewname;

COMMIT;

-- =====================================================================
-- FIN · 8 vistas creadas. Probar con:
--   SELECT * FROM v_kpi_executive;
--   SELECT * FROM v_deliveries_timeseries ORDER BY fecha DESC LIMIT 30;
-- =====================================================================
