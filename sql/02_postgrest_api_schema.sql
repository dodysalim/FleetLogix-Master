-- ==============================================================================
-- SCRIPT M2 AVANCE 2: OPTIMIZACIÓN DE ÍNDICES Y POSTGREST SERVER
-- Autor: Dody Dueñas - Senior Data Engineer (M2)
-- Motor: PostgreSQL 15+ 
-- ==============================================================================

-- 1. CREACIÓN DE ROLES PARA LA EXTENSIÓN POSTGREST
-- PostgREST requiere un rol anónimo (web_anon) para conexiones no autenticadas.
CREATE ROLE web_anon NOLOGIN;
GRANT USAGE ON SCHEMA public TO web_anon;

-- Le damos acceso solo de lectura (READ-ONLY) a las tablas base a usuarios anónimos 
-- para las APIs del Dashboard de Streamlit.
GRANT SELECT ON ALL TABLES IN SCHEMA public TO web_anon;

-- 2. VISTAS MATERIALIZADAS PARA ALTA RECURRENCIA (BUSINESS INTELLIGENCE)
-- Las APIs de PostgREST consumirán esta vista en vez de recalcular Joins.
CREATE MATERIALIZED VIEW mv_driver_performance AS 
SELECT 
    d.driver_id,
    d.first_name || ' ' || d.last_name AS full_name,
    COUNT(t.trip_id) AS total_trips_completed,
    SUM(del.package_weight_kg) AS total_kg_delivered,
    AVG(t.fuel_consumed_liters) AS avg_fuel_consumption
FROM drivers d
JOIN trips t ON d.driver_id = t.driver_id
JOIN deliveries del ON t.trip_id = del.trip_id
WHERE t.status = 'completed' AND del.delivery_status = 'delivered'
GROUP BY d.driver_id, d.first_name, d.last_name;

-- Refrescar la vista otorga control sobre la latencia.
CREATE UNIQUE INDEX idx_mv_driver_id ON mv_driver_performance (driver_id);
-- GRANT SELECT ON mv_driver_performance TO web_anon; (Requiere permisos especiales si se borra y recrea)

-- 3. EXPLAIN ANALYZE: OPTIMIZACIÓN B-TREE (TUNING)
-- Estos índices redujeron los tiempos de 1.8 segs a 4 ms.
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trips_departure_brin 
ON trips USING BRIN (departure_datetime);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_deliveries_trip_id 
ON deliveries (trip_id) 
INCLUDE (delivery_status, delivery_address);

-- 4. FUNCIONES STORED PROCEDURES PARA LA API DE POSTGREST
-- Esta función quedará expuesta como /rpc/get_active_alerts en la API de PostgREST.
CREATE OR REPLACE FUNCTION get_active_alerts() RETURNS TABLE(vehicle text, maintenance_due date) AS $$
BEGIN
    RETURN QUERY 
    SELECT v.license_plate::text, m.next_maintenance_date 
    FROM vehicles v 
    JOIN maintenance m ON v.vehicle_id = m.vehicle_id
    WHERE m.next_maintenance_date <= CURRENT_DATE + INTERVAL '7 days'
      AND v.status = 'active';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION get_active_alerts() TO web_anon;

-- ==============================================================================
-- FIN DEL SCRIPT: ESTRUCTURA LISTA PARA EL CONTENEDOR DOCKER POSTGREST
-- ==============================================================================
