-- =====================================================
-- FLEETLOGIX - 12 ANALYTICAL QUERIES
-- Proyecto Integrador M2 - Henry Data Science
-- =====================================================

-- =====================================================
-- QUERY 1: Listar todos los vehículos activos
-- =====================================================
-- Objetivo: Obtener lista de vehículos con estado activo
-- Tablas involucradas: vehicles
-- Complejidad: BÁSICA
SELECT 
    vehicle_id,
    license_plate,
    vehicle_type,
    capacity_kg,
    fuel_type,
    acquisition_date,
    status
FROM vehicles
WHERE status = 'active'
ORDER BY vehicle_type, license_plate;

-- =====================================================
-- QUERY 2: Conteo de vehículos por tipo
-- =====================================================
-- Objetivo: Agrupar vehículos por tipo y contar
-- Tablas involucradas: vehicles
-- Complejidad: BÁSICA
SELECT 
    vehicle_type,
    COUNT(*) AS total_vehicles,
    ROUND(AVG(capacity_kg), 2) AS avg_capacity_kg
FROM vehicles
GROUP BY vehicle_type
ORDER BY total_vehicles DESC;

-- =====================================================
-- QUERY 3: Top 5 rutas más largas
-- =====================================================
-- Objetivo: Identificar rutas con mayor distancia
-- Tablas involucradas: routes
-- Complejidad: BÁSICA
SELECT 
    route_code,
    origin_city,
    destination_city,
    distance_km,
    estimated_duration_hours,
    toll_cost
FROM routes
WHERE distance_km > 500
ORDER BY distance_km DESC
LIMIT 5;

-- =====================================================
-- QUERY 4: Viajes con información completa (JOIN triple)
-- =====================================================
-- Objetivo: Obtener viajes con datos de vehículo, conductor y ruta
-- Tablas involucradas: trips, vehicles, drivers, routes
-- Complejidad: INTERMEDIA
SELECT 
    t.trip_id,
    v.license_plate AS vehicle_plate,
    d.first_name || ' ' || d.last_name AS driver_name,
    r.route_code,
    r.origin_city || ' -> ' || r.destination_city AS route,
    t.departure_datetime,
    t.arrival_datetime,
    t.fuel_consumed_liters,
    t.total_weight_kg,
    t.status
FROM trips t
JOIN vehicles v ON t.vehicle_id = v.vehicle_id
JOIN drivers d ON t.driver_id = d.driver_id
JOIN routes r ON t.route_id = r.route_id
WHERE t.status = 'completed'
ORDER BY t.departure_datetime DESC
LIMIT 100;

-- =====================================================
-- QUERY 5: Rendimiento de conductores
-- =====================================================
-- Objetivo: Calcular métricas de rendimiento por conductor
-- Tablas involucradas: drivers, trips, deliveries
-- Complejidad: INTERMEDIA
SELECT 
    d.driver_id,
    d.first_name,
    d.last_name,
    d.license_expiry,
    COUNT(t.trip_id) AS total_trips,
    SUM(t.fuel_consumed_liters) AS total_fuel_consumed,
    ROUND(AVG(t.fuel_consumed_liters), 2) AS avg_fuel_per_trip,
    COUNT(del.delivery_id) AS total_deliveries
FROM drivers d
LEFT JOIN trips t ON d.driver_id = t.driver_id
LEFT JOIN deliveries del ON t.trip_id = del.trip_id
WHERE d.status = 'active'
GROUP BY d.driver_id, d.first_name, d.last_name, d.license_expiry
HAVING COUNT(t.trip_id) > 10
ORDER BY total_trips DESC
LIMIT 20;

-- =====================================================
-- QUERY 6: Análisis de entregas por ciudad
-- =====================================================
-- Objetivo: Calcular métricas de entregas por ciudad destino
-- Tablas involucradas: deliveries, trips, routes
-- Complejidad: INTERMEDIA
SELECT 
    r.destination_city,
    COUNT(del.delivery_id) AS total_deliveries,
    COUNT(CASE WHEN del.delivery_status = 'delivered' THEN 1 END) AS delivered,
    COUNT(CASE WHEN del.delivery_status = 'failed' THEN 1 END) AS failed,
    ROUND(100.0 * COUNT(CASE WHEN del.delivery_status = 'delivered' THEN 1 END) / 
          COUNT(del.delivery_id), 2) AS delivery_success_rate,
    ROUND(AVG(del.package_weight_kg), 2) AS avg_package_weight
FROM deliveries del
JOIN trips t ON del.trip_id = t.trip_id
JOIN routes r ON t.route_id = r.route_id
GROUP BY r.destination_city
ORDER BY total_deliveries DESC;

-- =====================================================
-- QUERY 7: Consumos de combustible por ruta
-- =====================================================
-- Objetivo: Analizar consumo de combustible por ruta
-- Tablas involucradas: trips, routes
-- Complejidad: INTERMEDIA
SELECT 
    r.route_code,
    r.origin_city,
    r.destination_city,
    r.distance_km,
    COUNT(t.trip_id) AS total_trips,
    SUM(t.fuel_consumed_liters) AS total_fuel,
    ROUND(AVG(t.fuel_consumed_liters), 2) AS avg_fuel,
    ROUND(SUM(t.fuel_consumed_liters) / SUM(r.distance_km) * 100, 2) AS fuel_efficiency_l_per_100km
FROM trips t
JOIN routes r ON t.route_id = r.route_id
WHERE t.status = 'completed'
GROUP BY r.route_id, r.origin_city, r.destination_city, r.distance_km
ORDER BY total_fuel DESC
LIMIT 10;

-- =====================================================
-- QUERY 8: Análisis temporal de entregas (CON CTE)
-- =====================================================
-- Objetivo: Analizar tendencias de entregas por mes usando CTE
-- Tablas involucradas: deliveries
-- Complejidad: AVANZADA (CTE)
WITH monthly_deliveries AS (
    SELECT 
        TO_CHAR(scheduled_datetime, 'YYYY-MM') AS month,
        delivery_status,
        COUNT(*) AS count
    FROM deliveries
    WHERE scheduled_datetime IS NOT NULL
    GROUP BY TO_CHAR(scheduled_datetime, 'YYYY-MM'), delivery_status
)
SELECT 
    month,
    SUM(CASE WHEN delivery_status = 'delivered' THEN count ELSE 0 END) AS delivered,
    SUM(CASE WHEN delivery_status = 'pending' THEN count ELSE 0 END) AS pending,
    SUM(CASE WHEN delivery_status = 'failed' THEN count ELSE 0 END) AS failed,
    SUM(CASE WHEN delivery_status = 'cancelled' THEN count ELSE 0 END) AS cancelled,
    SUM(count) AS total
FROM monthly_deliveries
GROUP BY month
ORDER BY month DESC
LIMIT 12;

-- =====================================================
-- QUERY 9: Costo de mantenimiento por vehículo (CON CTE)
-- =====================================================
-- Objetivo: Calcular costos de mantenimiento por vehículo
-- Tablas involucradas: vehicles, maintenance
-- Complejidad: AVANZADA (CTE)
WITH vehicle_maintenance_cost AS (
    SELECT 
        v.vehicle_id,
        v.license_plate,
        v.vehicle_type,
        COUNT(m.maintenance_id) AS maintenance_count,
        SUM(m.cost) AS total_maintenance_cost,
        ROUND(AVG(m.cost), 2) AS avg_maintenance_cost,
        MAX(m.maintenance_date) AS last_maintenance_date
    FROM vehicles v
    LEFT JOIN maintenance m ON v.vehicle_id = m.vehicle_id
    GROUP BY v.vehicle_id, v.license_plate, v.vehicle_type
)
SELECT 
    vehicle_type,
    COUNT(*) AS total_vehicles,
    SUM(maintenance_count) AS total_maintenances,
    ROUND(SUM(total_maintenance_cost), 2) AS total_cost,
    ROUND(AVG(total_maintenance_cost), 2) AS avg_cost_per_vehicle
FROM vehicle_maintenance_cost
GROUP BY vehicle_type
ORDER BY total_cost DESC;

-- =====================================================
-- QUERY 10: Rendimiento por tipo de vehículo (WINDOW FUNCTION)
-- =====================================================
-- Objetivo: Ranking de vehículos por eficiencia usando Window Functions
-- Tablas involucradas: vehicles, trips
-- Complejidad: AVANZADA (Window Function)
SELECT 
    v.vehicle_id,
    v.license_plate,
    v.vehicle_type,
    COUNT(t.trip_id) AS trip_count,
    SUM(t.fuel_consumed_liters) AS total_fuel,
    ROUND(AVG(t.fuel_consumed_liters), 2) AS avg_fuel,
    SUM(t.total_weight_kg) AS total_weight,
    RANK() OVER (PARTITION BY v.vehicle_type ORDER BY COUNT(t.trip_id) DESC) AS rank_in_type
FROM vehicles v
LEFT JOIN trips t ON v.vehicle_id = t.vehicle_id
WHERE t.status = 'completed'
GROUP BY v.vehicle_id, v.license_plate, v.vehicle_type
HAVING COUNT(t.trip_id) > 0
ORDER BY v.vehicle_type, trip_count DESC
LIMIT 20;

-- =====================================================
-- QUERY 11: Conductores con licencia por vencer (SUBQUERY)
-- =====================================================
-- Objetivo: Identificar conductores con licencia próxima a vencer
-- Tablas involucradas: drivers, trips
-- Complejidad: AVANZADA (Subquery)
SELECT 
    driver_id,
    employee_code,
    first_name,
    last_name,
    license_expiry,
    phone,
    hire_date,
    (
        SELECT COUNT(*) 
        FROM trips t 
        WHERE t.driver_id = drivers.driver_id AND t.status = 'in_progress'
    ) AS active_trips
FROM drivers
WHERE license_expiry <= CURRENT_DATE + INTERVAL '30 days'
AND status = 'active'
ORDER BY license_expiry ASC;

-- =====================================================
-- QUERY 12: Informe ejecutivo consolidado (MULTI-CTE)
-- =====================================================
-- Objetivo: Generar informe ejecutivo con múltiples métricas
-- Tablas involucradas: vehicles, drivers, trips, deliveries, maintenance
-- Complejidad: MUY AVANZADA (Multiple CTEs)
WITH fleet_stats AS (
    SELECT 
        COUNT(*) AS total_vehicles,
        COUNT(CASE WHEN status = 'active' THEN 1 END) AS active_vehicles
    FROM vehicles
),
driver_stats AS (
    SELECT 
        COUNT(*) AS total_drivers,
        COUNT(CASE WHEN status = 'active' THEN 1 END) AS active_drivers
    FROM drivers
),
trip_stats AS (
    SELECT 
        COUNT(*) AS total_trips,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) AS completed_trips,
        SUM(fuel_consumed_liters) AS total_fuel
    FROM trips
),
delivery_stats AS (
    SELECT 
        COUNT(*) AS total_deliveries,
        COUNT(CASE WHEN delivery_status = 'delivered' THEN 1 END) AS delivered,
        SUM(package_weight_kg) AS total_weight
    FROM deliveries
),
maintenance_stats AS (
    SELECT 
        COUNT(*) AS total_maintenances,
        SUM(cost) AS total_maintenance_cost
    FROM maintenance
)
SELECT 
    'Executive Summary' AS report_type,
    fs.total_vehicles AS vehicles_total,
    fs.active_vehicles AS vehicles_active,
    ds.total_drivers AS drivers_total,
    ds.active_drivers AS drivers_active,
    ts.total_trips AS trips_total,
    ts.completed_trips AS trips_completed,
    ds.total_deliveries AS deliveries_total,
    dps.delivered AS deliveries_completed,
    ROUND(100.0 * dps.delivered / ds.total_deliveries, 2) AS on_time_rate,
    ROUND(dps.total_weight / 1000, 2) AS total_tons_delivered,
    ts.total_fuel AS total_fuel_liters,
    ms.total_maintenance_cost AS total_maintenance_cost,
    ROUND(ms.total_maintenance_cost / ts.completed_trips, 2) AS cost_per_trip
FROM fleet_stats fs, driver_stats ds, trip_stats ts, delivery_stats dps, maintenance_stats ms;

-- =====================================================
-- CONSULTAS DE VERIFICACIÓN DE CALIDAD DE DATOS
-- =====================================================

-- Verificar integridad referencial: Trips sin vehículo válido
SELECT COUNT(*) AS orphan_trips
FROM trips t
LEFT JOIN vehicles v ON t.vehicle_id = v.vehicle_id
WHERE v.vehicle_id IS NULL;

-- Verificar integridad referencial: Entregas sin trip válido
SELECT COUNT(*) AS orphan_deliveries
FROM deliveries d
LEFT JOIN trips t ON d.trip_id = t.trip_id
WHERE t.trip_id IS NULL;

-- Verificar consistencia temporal: arrival < departure
SELECT COUNT(*) AS temporal_inconsistencies
FROM trips
WHERE arrival_datetime IS NOT NULL 
AND arrival_datetime < departure_datetime;

-- Verificar peso excedido: trips excediendo capacidad del vehículo
SELECT COUNT(*) AS overweight_trips
FROM trips t
JOIN vehicles v ON t.vehicle_id = v.vehicle_id
WHERE t.total_weight_kg > v.capacity_kg;

-- =====================================================
-- CONSULTAS DE OPTIMIZACIÓN - EXPLAIN ANALYZE
-- =====================================================

-- Análisis de rendimiento Query 4
EXPLAIN ANALYZE
SELECT 
    t.trip_id,
    v.license_plate,
    d.first_name || ' ' || d.last_name AS driver_name,
    r.route_code
FROM trips t
JOIN vehicles v ON t.vehicle_id = v.vehicle_id
JOIN drivers d ON t.driver_id = d.driver_id
JOIN routes r ON t.route_id = r.route_id
WHERE t.status = 'completed'
ORDER BY t.departure_datetime DESC
LIMIT 100;
