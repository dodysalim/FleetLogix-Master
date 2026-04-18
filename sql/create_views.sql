-- ======================================================================
-- FleetLogix - Creación de VISTAS para el Dashboard Streamlit
-- ======================================================================
-- Autor: Dody Dueñas · Henry M2
-- Ejecutar con: psql -U postgres -d fleetlogix_db -f create_views.sql
-- ======================================================================

-- ── Vista 1: KPIs ejecutivos (una sola fila) ──────────────────────────
CREATE OR REPLACE VIEW v_kpi_executive AS
SELECT
    -- Flota
    (SELECT COUNT(*) FROM vehicles WHERE status = 'active')                             AS active_vehicles,
    -- Conductores
    (SELECT COUNT(*) FROM drivers  WHERE status = 'active')                             AS active_drivers,
    -- Viajes
    (SELECT COUNT(*) FROM trips    WHERE status = 'completed')                          AS completed_trips,
    -- Entregas
    (SELECT COUNT(*) FROM deliveries WHERE delivery_status = 'delivered')               AS delivered,
    (SELECT COUNT(*) FROM deliveries WHERE delivery_status = 'pending')                 AS pending_deliveries,
    (SELECT COUNT(*) FROM deliveries WHERE delivery_status = 'failed')                  AS failed_deliveries,
    -- On-time rate
    (SELECT ROUND(
        100.0 * COUNT(CASE WHEN delivered_datetime <= scheduled_datetime + INTERVAL '30 minutes' THEN 1 END)
        / NULLIF(COUNT(*), 0), 1)
     FROM deliveries
     WHERE delivery_status = 'delivered'
       AND delivered_datetime IS NOT NULL
       AND scheduled_datetime IS NOT NULL)                                               AS on_time_rate_pct,
    -- Peso total (toneladas)
    (SELECT ROUND(SUM(package_weight_kg)::NUMERIC / 1000, 1)
     FROM deliveries WHERE delivery_status = 'delivered')                               AS total_tons,
    -- Mantenimiento próximo 30 días
    (SELECT COUNT(DISTINCT vehicle_id)
     FROM maintenance
     WHERE next_maintenance_date <= CURRENT_DATE + INTERVAL '30 days')                 AS vehicles_maintenance_30d,
    -- Costo total de mantenimiento
    (SELECT COALESCE(SUM(cost), 0) FROM maintenance)                                    AS total_maintenance_cost;


-- ── Vista 2: Serie temporal de entregas ──────────────────────────────
CREATE OR REPLACE VIEW v_deliveries_timeseries AS
SELECT
    DATE(scheduled_datetime)                                                   AS fecha,
    COUNT(*)                                                                   AS total_deliveries,
    COUNT(CASE WHEN delivery_status = 'delivered' THEN 1 END)                 AS delivered,
    COUNT(CASE WHEN delivery_status = 'pending'   THEN 1 END)                 AS pending,
    COUNT(CASE WHEN delivery_status = 'failed'    THEN 1 END)                 AS failed,
    COALESCE(SUM(package_weight_kg), 0)                                       AS total_weight_kg
FROM deliveries
WHERE scheduled_datetime IS NOT NULL
GROUP BY DATE(scheduled_datetime)
ORDER BY fecha;


-- ── Vista 3: Rendimiento de vehículos ────────────────────────────────
CREATE OR REPLACE VIEW v_vehicle_performance AS
SELECT
    v.vehicle_id,
    v.license_plate,
    v.vehicle_type,
    v.capacity_kg,
    v.fuel_type,
    v.status                                                                  AS vehicle_status,
    COUNT(t.trip_id)                                                          AS total_trips,
    COUNT(CASE WHEN t.status = 'completed' THEN 1 END)                       AS completed_trips,
    COALESCE(SUM(t.fuel_consumed_liters), 0)                                  AS total_fuel_liters,
    COALESCE(AVG(t.fuel_consumed_liters), 0)                                  AS avg_fuel_per_trip,
    COALESCE(SUM(t.total_weight_kg), 0)                                       AS total_weight_kg,
    -- Utilización de capacidad (% promedio)
    ROUND(
        COALESCE(AVG(
            CASE WHEN v.capacity_kg > 0
                 THEN t.total_weight_kg / v.capacity_kg * 100
            END
        ), 0)::NUMERIC, 1)                                                   AS avg_capacity_utilization_pct,
    -- Eficiencia: litros por 100 km
    ROUND(
        COALESCE(
            SUM(t.fuel_consumed_liters) / NULLIF(SUM(r.distance_km), 0) * 100,
            0
        )::NUMERIC, 2)                                                        AS fuel_efficiency_l_per_100km
FROM vehicles v
LEFT JOIN trips t       ON v.vehicle_id = t.vehicle_id
LEFT JOIN routes r      ON t.route_id   = r.route_id
GROUP BY
    v.vehicle_id, v.license_plate, v.vehicle_type,
    v.capacity_kg, v.fuel_type, v.status;


-- ── Vista 4: Rendimiento de conductores ─────────────────────────────
CREATE OR REPLACE VIEW v_driver_performance AS
SELECT
    d.driver_id,
    d.employee_code,
    d.first_name,
    d.last_name,
    d.first_name || ' ' || d.last_name                                       AS full_name,
    d.status                                                                  AS driver_status,
    d.license_expiry,
    -- Estado de licencia
    CASE
        WHEN d.license_expiry < CURRENT_DATE                        THEN 'VENCIDA'
        WHEN d.license_expiry < CURRENT_DATE + INTERVAL '30 days'  THEN 'POR VENCER'
        ELSE 'VIGENTE'
    END                                                                       AS license_status,
    d.hire_date,
    COUNT(t.trip_id)                                                          AS total_trips,
    COUNT(CASE WHEN t.status = 'completed' THEN 1 END)                       AS completed_trips,
    COUNT(del.delivery_id)                                                    AS total_deliveries,
    COUNT(CASE WHEN del.delivery_status = 'delivered' THEN 1 END)            AS successful_deliveries,
    ROUND(
        100.0 * COUNT(CASE WHEN del.delivery_status = 'delivered' THEN 1 END)
        / NULLIF(COUNT(del.delivery_id), 0)
    , 1)                                                                      AS success_rate_pct,
    COALESCE(SUM(t.fuel_consumed_liters), 0)                                  AS total_fuel_liters
FROM drivers d
LEFT JOIN trips     t   ON d.driver_id = t.driver_id
LEFT JOIN deliveries del ON t.trip_id  = del.trip_id
GROUP BY
    d.driver_id, d.employee_code, d.first_name, d.last_name,
    d.status, d.license_expiry, d.hire_date;


-- ── Vista 5: Tráfico de rutas ────────────────────────────────────────
CREATE OR REPLACE VIEW v_route_traffic AS
SELECT
    r.route_id,
    r.route_code,
    r.origin_city,
    r.destination_city,
    r.origin_city || ' → ' || r.destination_city                            AS route_label,
    r.distance_km,
    r.estimated_duration_hours,
    r.toll_cost,
    COUNT(t.trip_id)                                                          AS trip_count,
    COUNT(DISTINCT t.vehicle_id)                                              AS distinct_vehicles,
    COUNT(DISTINCT t.driver_id)                                               AS distinct_drivers,
    COUNT(del.delivery_id)                                                    AS total_deliveries,
    COALESCE(SUM(t.fuel_consumed_liters), 0)                                  AS total_fuel_liters,
    COALESCE(AVG(t.fuel_consumed_liters), 0)                                  AS avg_fuel_per_trip,
    ROUND(
        COALESCE(SUM(t.fuel_consumed_liters) / NULLIF(SUM(r.distance_km), 0) * 100, 0)::NUMERIC,
        2
    )                                                                         AS fuel_efficiency_l_per_100km
FROM routes r
LEFT JOIN trips      t   ON r.route_id  = t.route_id
LEFT JOIN deliveries del ON t.trip_id   = del.trip_id
GROUP BY
    r.route_id, r.route_code, r.origin_city, r.destination_city,
    r.distance_km, r.estimated_duration_hours, r.toll_cost;


-- ── Vista 6: Alertas de mantenimiento ───────────────────────────────
CREATE OR REPLACE VIEW v_maintenance_alerts AS
SELECT
    v.vehicle_id,
    v.license_plate,
    v.vehicle_type,
    v.status                                                                  AS vehicle_status,
    m.maintenance_id,
    m.maintenance_type,
    m.maintenance_date,
    m.description,
    m.cost,
    m.next_maintenance_date,
    m.performed_by,
    -- Días restantes
    (m.next_maintenance_date - CURRENT_DATE)                                  AS days_until_maintenance,
    -- Nivel de alerta
    CASE
        WHEN m.next_maintenance_date < CURRENT_DATE                          THEN 'VENCIDO'
        WHEN m.next_maintenance_date < CURRENT_DATE + INTERVAL '7 days'     THEN 'ESTA SEMANA'
        WHEN m.next_maintenance_date < CURRENT_DATE + INTERVAL '30 days'    THEN 'ESTE MES'
        ELSE 'OK'
    END                                                                       AS alert_level
FROM vehicles v
JOIN maintenance m ON v.vehicle_id = m.vehicle_id
WHERE v.status = 'active';


-- ── Vista 7: Eficiencia de combustible mensual ──────────────────────
CREATE OR REPLACE VIEW v_fuel_efficiency AS
SELECT
    DATE_TRUNC('month', t.departure_datetime)                                AS month,
    v.vehicle_type,
    v.fuel_type,
    COUNT(t.trip_id)                                                          AS trip_count,
    COALESCE(SUM(t.fuel_consumed_liters), 0)                                  AS total_fuel_liters,
    COALESCE(AVG(t.fuel_consumed_liters), 0)                                  AS avg_fuel_per_trip,
    COALESCE(SUM(r.distance_km), 0)                                           AS total_distance_km,
    ROUND(
        COALESCE(SUM(t.fuel_consumed_liters) / NULLIF(SUM(r.distance_km), 0) * 100, 0)::NUMERIC,
        2
    )                                                                         AS fuel_efficiency_l_per_100km
FROM trips t
JOIN vehicles v ON t.vehicle_id = v.vehicle_id
JOIN routes   r ON t.route_id   = r.route_id
WHERE t.status = 'completed'
  AND t.departure_datetime IS NOT NULL
GROUP BY
    DATE_TRUNC('month', t.departure_datetime),
    v.vehicle_type,
    v.fuel_type
ORDER BY month, v.vehicle_type;


-- ── Verificación final ───────────────────────────────────────────────
SELECT
    viewname,
    'OK' AS estado
FROM pg_views
WHERE schemaname = 'public'
  AND viewname IN (
      'v_kpi_executive',
      'v_deliveries_timeseries',
      'v_vehicle_performance',
      'v_driver_performance',
      'v_route_traffic',
      'v_maintenance_alerts',
      'v_fuel_efficiency'
  )
ORDER BY viewname;
