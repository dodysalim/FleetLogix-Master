-- =====================================================================
-- FLEETLOGIX · QUERIES PARAMETRIZABLES POR KPI
-- ---------------------------------------------------------------------
-- Estas queries pueden pegarse directamente en el dashboard Streamlit
-- (ver dashboard_streamlit/utils/db.py → run_query) o ejecutarse desde
-- psql / DBeaver para validación manual. Cada bloque corresponde a un
-- KPI del catálogo (ver dashboard/KPIs.md).
-- =====================================================================

-- ---------------------------------------------------------------------
-- KPI 01 — Vehículos Activos
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS active_vehicles
FROM vehicles
WHERE status = 'active';


-- ---------------------------------------------------------------------
-- KPI 02 — Conductores Activos
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS active_drivers
FROM drivers
WHERE status = 'active';


-- ---------------------------------------------------------------------
-- KPI 03 — Viajes Completados (con tendencia mensual)
-- ---------------------------------------------------------------------
SELECT
    DATE_TRUNC('month', departure_datetime)::date AS month,
    COUNT(*)                                       AS completed_trips
FROM trips
WHERE status = 'completed'
GROUP BY DATE_TRUNC('month', departure_datetime)
ORDER BY month;


-- ---------------------------------------------------------------------
-- KPI 04 — Entregas Realizadas por día (últimos 90 días)
-- ---------------------------------------------------------------------
SELECT
    DATE(scheduled_datetime) AS fecha,
    COUNT(*)                 AS total_deliveries,
    COUNT(*) FILTER (WHERE delivery_status = 'delivered') AS delivered,
    COUNT(*) FILTER (WHERE delivery_status = 'pending')   AS pending,
    COUNT(*) FILTER (WHERE delivery_status = 'failed')    AS failed
FROM deliveries
WHERE scheduled_datetime >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(scheduled_datetime)
ORDER BY fecha;


-- ---------------------------------------------------------------------
-- KPI 05 — On-Time Delivery Rate (tolerancia 30 min)
-- ---------------------------------------------------------------------
SELECT
    COUNT(*) FILTER (WHERE delivered_datetime <= scheduled_datetime + INTERVAL '30 minutes') AS on_time,
    COUNT(*)                                                                                  AS total,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE delivered_datetime <= scheduled_datetime + INTERVAL '30 minutes')
        / NULLIF(COUNT(*), 0)
      , 2)                                                                                    AS on_time_rate_pct
FROM deliveries
WHERE delivery_status     = 'delivered'
  AND delivered_datetime IS NOT NULL
  AND scheduled_datetime IS NOT NULL;


-- ---------------------------------------------------------------------
-- KPI 06 — Consumo promedio por viaje
-- ---------------------------------------------------------------------
SELECT
    ROUND(AVG(fuel_consumed_liters)::numeric, 2) AS avg_fuel_per_trip
FROM trips
WHERE fuel_consumed_liters IS NOT NULL;


-- ---------------------------------------------------------------------
-- KPI 07 — Eficiencia L/100km (global + por tipo de vehículo)
-- ---------------------------------------------------------------------
SELECT
    v.vehicle_type,
    ROUND(SUM(t.fuel_consumed_liters)::numeric, 2)                              AS total_fuel,
    ROUND(SUM(r.distance_km)::numeric, 2)                                       AS total_distance_km,
    ROUND(
        SUM(t.fuel_consumed_liters)::numeric
        / NULLIF(SUM(r.distance_km), 0) * 100
      , 2)                                                                      AS fuel_efficiency_l_per_100km
FROM trips    t
JOIN vehicles v ON t.vehicle_id = v.vehicle_id
JOIN routes   r ON t.route_id   = r.route_id
WHERE t.status = 'completed'
GROUP BY v.vehicle_type
ORDER BY fuel_efficiency_l_per_100km;


-- ---------------------------------------------------------------------
-- KPI 08 — Tasa de fallos de entrega
-- ---------------------------------------------------------------------
SELECT
    COUNT(*) FILTER (WHERE delivery_status = 'failed')                                AS failed,
    COUNT(*)                                                                          AS total,
    ROUND(100.0 * COUNT(*) FILTER (WHERE delivery_status = 'failed') / NULLIF(COUNT(*),0), 2)
                                                                                      AS failure_rate_pct
FROM deliveries;


-- ---------------------------------------------------------------------
-- KPI 09 — Costo total de mantenimiento (YTD + histórico)
-- ---------------------------------------------------------------------
SELECT
    DATE_TRUNC('month', maintenance_date)::date AS month,
    COUNT(*)                                    AS maintenance_count,
    ROUND(SUM(cost)::numeric, 2)                AS total_cost,
    ROUND(AVG(cost)::numeric, 2)                AS avg_cost
FROM maintenance
GROUP BY DATE_TRUNC('month', maintenance_date)
ORDER BY month;


-- ---------------------------------------------------------------------
-- KPI 10 — Costo por viaje (eficiencia económica)
-- ---------------------------------------------------------------------
WITH mant AS (
    SELECT SUM(cost) AS total_maintenance_cost FROM maintenance
),
trp AS (
    SELECT COUNT(*) AS completed_trips FROM trips WHERE status = 'completed'
)
SELECT
    ROUND((mant.total_maintenance_cost / NULLIF(trp.completed_trips, 0))::numeric, 2) AS cost_per_trip,
    mant.total_maintenance_cost,
    trp.completed_trips
FROM mant, trp;


-- ---------------------------------------------------------------------
-- KPI 11 — Vehículos con mantenimiento próximo (30 días)
-- ---------------------------------------------------------------------
SELECT
    v.vehicle_id,
    v.license_plate,
    v.vehicle_type,
    m.next_maintenance_date,
    (m.next_maintenance_date - CURRENT_DATE) AS days_until
FROM maintenance m
JOIN vehicles    v ON m.vehicle_id = v.vehicle_id
WHERE m.next_maintenance_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
ORDER BY m.next_maintenance_date ASC;


-- ---------------------------------------------------------------------
-- KPI 12 — Toneladas transportadas (total + por mes)
-- ---------------------------------------------------------------------
SELECT
    DATE_TRUNC('month', scheduled_datetime)::date    AS month,
    ROUND(SUM(package_weight_kg)::numeric / 1000, 2) AS total_tons,
    COUNT(*)                                         AS delivery_count
FROM deliveries
WHERE scheduled_datetime IS NOT NULL
GROUP BY DATE_TRUNC('month', scheduled_datetime)
ORDER BY month;


-- ---------------------------------------------------------------------
-- KPI 13 — Utilización de capacidad (promedio por tipo de vehículo)
-- ---------------------------------------------------------------------
SELECT
    v.vehicle_type,
    ROUND(AVG(t.total_weight_kg / NULLIF(v.capacity_kg, 0) * 100)::numeric, 2)
                                                                          AS avg_capacity_utilization_pct,
    COUNT(t.trip_id)                                                      AS trip_count
FROM trips    t
JOIN vehicles v ON t.vehicle_id = v.vehicle_id
WHERE t.status = 'completed'
GROUP BY v.vehicle_type
ORDER BY avg_capacity_utilization_pct DESC;


-- ---------------------------------------------------------------------
-- KPI 14 — Trip Success Rate
-- ---------------------------------------------------------------------
SELECT
    COUNT(*) FILTER (WHERE status = 'completed')                                       AS completed,
    COUNT(*)                                                                            AS total,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'completed') / NULLIF(COUNT(*),0), 2) AS trip_success_rate_pct
FROM trips;


-- ---------------------------------------------------------------------
-- KPI 15 — Licencias por vencer en los próximos 30 días
-- ---------------------------------------------------------------------
SELECT
    driver_id,
    employee_code,
    first_name || ' ' || last_name AS full_name,
    license_expiry,
    (license_expiry - CURRENT_DATE)  AS days_until_expiry,
    phone
FROM drivers
WHERE status         = 'active'
  AND license_expiry BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
ORDER BY license_expiry ASC;
