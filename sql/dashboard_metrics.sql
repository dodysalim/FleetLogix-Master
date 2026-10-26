-- =====================================================
-- DASHBOARD QUERIES
-- FleetLogix - Métricas para Dashboard Ejecutivo (Streamlit)
-- =====================================================

-- =====================================================
-- KPI 1: Resumen Ejecutivo (Métricas Principales)
-- =====================================================
-- vehicles, drivers, trips, deliveries
SELECT 
    (SELECT COUNT(*) FROM vehicles WHERE status = 'active') AS active_vehicles,
    (SELECT COUNT(*) FROM drivers WHERE status = 'active') AS active_drivers,
    (SELECT COUNT(*) FROM trips WHERE status = 'completed') AS completed_trips,
    (SELECT COUNT(*) FROM deliveries WHERE delivery_status = 'delivered') AS delivered,
    (SELECT COUNT(*) FROM deliveries WHERE delivery_status = 'pending') AS pending_deliveries,
    (SELECT ROUND(AVG(fuel_consumed_liters), 2) FROM trips WHERE fuel_consumed_liters IS NOT NULL) AS avg_fuel_per_trip,
    (SELECT COUNT(*) FROM vehicles WHERE next_maintenance_date <= CURRENT_DATE + INTERVAL '30 days') AS vehicles_needing_maintenance;

-- =====================================================
-- KPI 2: Flota Activa por Tipo
-- =====================================================
SELECT 
    vehicle_type,
    COUNT(*) AS total_count,
    ROUND(AVG(capacity_kg), 2) AS avg_capacity_kg
FROM vehicles
WHERE status = 'active'
GROUP BY vehicle_type
ORDER BY total_count DESC;

-- =====================================================
-- KPI 3: Entregas a Tiempo (On-Time Rate)
-- =====================================================
SELECT 
    COUNT(CASE WHEN delivered_datetime <= scheduled_datetime + INTERVAL '30 minutes' THEN 1 END) AS on_time,
    COUNT(*) AS total,
    ROUND(100.0 * COUNT(CASE WHEN delivered_datetime <= scheduled_datetime + INTERVAL '30 minutes' THEN 1 END) / COUNT(*), 2) AS on_time_percentage
FROM deliveries
WHERE delivery_status = 'delivered'
AND delivered_datetime IS NOT NULL
AND scheduled_datetime IS NOT NULL;

-- =====================================================
-- KPI 4: Estado de Entregas
-- =====================================================
SELECT 
    delivery_status,
    COUNT(*) AS count
FROM deliveries
GROUP BY delivery_status
ORDER BY count DESC;

-- =====================================================
-- KPI 5: Rendimiento de Combustible por Vehículo
-- =====================================================
SELECT 
    v.license_plate,
    v.vehicle_type,
    COUNT(t.trip_id) AS total_trips,
    SUM(t.fuel_consumed_liters) AS total_fuel,
    ROUND(AVG(t.fuel_consumed_liters), 2) AS avg_fuel,
    ROUND(SUM(t.fuel_consumed_liters) / NULLIF(SUM(r.distance_km), 0) * 100, 2) AS fuel_efficiency_per_100km
FROM vehicles v
JOIN trips t ON v.vehicle_id = t.vehicle_id
JOIN routes r ON t.route_id = r.route_id
WHERE t.status = 'completed'
GROUP BY v.vehicle_id, v.license_plate, v.vehicle_type
ORDER BY total_fuel DESC
LIMIT 20;

-- =====================================================
-- KPI 6: Top 10 Conductores por Entregas
-- =====================================================
SELECT 
    d.driver_id,
    d.first_name,
    d.last_name,
    COUNT(del.delivery_id) AS total_deliveries,
    COUNT(CASE WHEN del.delivery_status = 'delivered' THEN 1 END) AS delivered_count,
    ROUND(100.0 * COUNT(CASE WHEN del.delivery_status = 'delivered' THEN 1 END) / COUNT(del.delivery_id), 2) AS success_rate
FROM drivers d
JOIN trips t ON d.driver_id = t.driver_id
JOIN deliveries del ON t.trip_id = del.trip_id
GROUP BY d.driver_id, d.first_name, d.last_name
ORDER BY total_deliveries DESC
LIMIT 10;

-- =====================================================
-- KPI 7: Rutas con Mayor Tráfico
-- =====================================================
SELECT 
    r.route_code,
    r.origin_city,
    r.destination_city,
    r.distance_km,
    COUNT(t.trip_id) AS trip_count,
    SUM(t.fuel_consumed_liters) AS total_fuel
FROM routes r
JOIN trips t ON r.route_id = t.route_id
GROUP BY r.route_id, r.route_code, r.origin_city, r.destination_city, r.distance_km
ORDER BY trip_count DESC
LIMIT 15;

-- =====================================================
-- KPI 8: Evolución de Entregas por Día
-- =====================================================
SELECT 
    DATE(scheduled_datetime) AS delivery_date,
    COUNT(*) AS total_deliveries,
    COUNT(CASE WHEN delivery_status = 'delivered' THEN 1 END) AS delivered,
    COUNT(CASE WHEN delivery_status = 'pending' THEN 1 END) AS pending,
    ROUND(AVG(package_weight_kg), 2) AS avg_weight
FROM deliveries
WHERE scheduled_datetime >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(scheduled_datetime)
ORDER BY delivery_date;

-- =====================================================
-- KPI 9: Distribución Geográfica de Entregas
-- =====================================================
SELECT 
    r.destination_city,
    COUNT(del.delivery_id) AS delivery_count,
    ROUND(AVG(r.distance_km), 2) AS avg_distance
FROM deliveries del
JOIN trips t ON del.trip_id = t.trip_id
JOIN routes r ON t.route_id = r.route_id
GROUP BY r.destination_city
ORDER BY delivery_count DESC
LIMIT 20;

-- =====================================================
-- KPI 10: Mantenimientos Recientes
-- =====================================================
SELECT 
    v.license_plate,
    v.vehicle_type,
    m.maintenance_date,
    m.maintenance_type,
    m.description,
    m.cost,
    m.next_maintenance_date,
    CASE 
        WHEN m.next_maintenance_date <= CURRENT_DATE THEN 'OVERDUE'
        WHEN m.next_maintenance_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'NEXT WEEK'
        WHEN m.next_maintenance_date <= CURRENT_DATE + INTERVAL '30 days' THEN 'THIS MONTH'
        ELSE 'OK'
    END AS maintenance_status
FROM maintenance m
JOIN vehicles v ON m.vehicle_id = v.vehicle_id
ORDER BY m.next_maintenance_date
LIMIT 20;

-- =====================================================
-- KPI 11: Consumo de Combustible por Mes
-- =====================================================
SELECT 
    DATE_TRUNC('month', departure_datetime) AS month,
    SUM(fuel_consumed_liters) AS total_fuel,
    COUNT(trip_id) AS trip_count,
    ROUND(AVG(fuel_consumed_liters), 2) AS avg_fuel_per_trip
FROM trips
WHERE status = 'completed'
GROUP DATE_TRUNC('month', departure_datetime)
ORDER BY month;

-- =====================================================
-- KPI 12: Alertas de Mantenimiento
-- =====================================================
SELECT 
    v.license_plate,
    v.vehicle_type,
    v.status AS vehicle_status,
    m.next_maintenance_date,
    DATEDIFF(day, CURRENT_DATE, m.next_maintenance_date) AS days_until_maintenance
FROM vehicles v
LEFT JOIN maintenance m ON v.vehicle_id = m.vehicle_id
WHERE v.status = 'active'
AND (m.next_maintenance_date <= CURRENT_DATE + INTERVAL '30 days' OR m.next_maintenance_date IS NULL)
ORDER BY m.next_maintenance_date;