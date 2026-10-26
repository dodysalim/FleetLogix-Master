-- =====================================================
-- FLEETLOGIX - ÍNDICES DE OPTIMIZACIÓN
-- Proyecto Integrador M2 - Henry Data Science
-- =====================================================

-- =====================================================
-- ANÁLISIS DE RENDIMIENTO ANTES DE ÍNDICES
-- =====================================================

-- Ejecutar estas queries con EXPLAIN ANALYZE para ver el plan de ejecución
-- y medir el tiempo antes de crear los índices

-- =====================================================
-- ÍNDICE 1: Optimización para JOINs frecuentes en trips
-- =====================================================
-- Justificación: Las queries 4-12 hacen JOIN intensivo entre trips y otras tablas
-- Queries beneficiadas: 4, 5, 6, 7, 9, 10, 11
CREATE INDEX IF NOT EXISTS idx_trips_composite_joins 
ON trips(vehicle_id, driver_id, route_id, departure_datetime)
WHERE status = 'completed';

-- =====================================================
-- ÍNDICE 2: Optimización para análisis temporal de deliveries
-- =====================================================
-- Justificación: Queries 8, 12 filtran y agrupan por scheduled_datetime
-- Queries beneficiadas: 4, 8, 12
CREATE INDEX IF NOT EXISTS idx_deliveries_scheduled_datetime 
ON deliveries(scheduled_datetime, delivery_status)
WHERE delivery_status = 'delivered';

-- =====================================================
-- ÍNDICE 3: Optimización para mantenimiento por vehículo
-- =====================================================
-- Justificación: Query 9 necesita acceso rápido a mantenimientos por vehículo
-- Queries beneficiadas: 9
CREATE INDEX IF NOT EXISTS idx_maintenance_vehicle_cost 
ON maintenance(vehicle_id, cost);

-- =====================================================
-- ÍNDICE 4: Optimización para análisis de conductores
-- =====================================================
-- Justificación: Queries 5, 6, 10 filtran por conductores activos
-- Queries beneficiadas: 2, 5, 6, 10
CREATE INDEX IF NOT EXISTS idx_drivers_status_license 
ON drivers(status, license_expiry)
WHERE status = 'active';

-- =====================================================
-- ÍNDICE 5: Optimización para métricas de rutas
-- =====================================================
-- Justificación: Query 7 calcula consumo por ruta
-- Queries beneficiadas: 4, 7, 9, 10
CREATE INDEX IF NOT EXISTS idx_routes_metrics 
ON routes(route_id, distance_km, destination_city);

-- =====================================================
-- ÍNDICE 6: Covering Index para deliveries
-- =====================================================
-- Justificación: Evitar lectura de la tabla completa
CREATE INDEX IF NOT EXISTS idx_deliveries_covering 
ON deliveries(trip_id, delivery_status)
INCLUDE (package_weight_kg, scheduled_datetime, delivered_datetime);

-- =====================================================
-- ÍNDICE 7: BRIN Index para series temporales
-- =====================================================
-- Justificación: Optimización para datos tipo time-series
CREATE INDEX IF NOT EXISTS idx_trips_departure_brin 
ON trips USING BRIN(departure_datetime);

-- =====================================================
-- ÍNDICE 8: Índice parcial para estados específicos
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_trips_completed 
ON trips(departure_datetime)
WHERE status = 'completed';

CREATE INDEX IF NOT EXISTS idx_deliveries_pending 
ON deliveries(scheduled_datetime)
WHERE delivery_status = 'pending';

-- =====================================================
-- ÍNDICE 9: Índice para búsqueda de conductores por licencia
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_drivers_license_expiry 
ON drivers(license_expiry);

-- =====================================================
-- ÍNDICE 10: Índice compuesto para análisis de flotas
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_vehicles_type_status 
ON vehicles(vehicle_type, status);

-- =====================================================
-- ANALYZE PARA ACTUALIZAR ESTADÍSTICAS DEL PLANIFICADOR
-- =====================================================
ANALYZE vehicles;
ANALYZE drivers;
ANALYZE routes;
ANALYZE trips;
ANALYZE deliveries;
ANALYZE maintenance;

-- =====================================================
-- CONSULTAS DE VERIFICACIÓN
-- =====================================================

-- Verificar índices creados
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_indexes
WHERE schemaname = 'public'
    AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- Verificar uso de índices
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Análisis de fragmentación de índices
SELECT 
    indexrelname,
    idx_blks_hit,
    idx_blks_read,
    ROUND(100.0 * idx_blks_hit / NULLIF(idx_blks_hit + idx_blks_read, 0), 2) as hit_ratio
FROM pg_stat_user_indexes
WHERE idx_blks_read > 0
ORDER BY idx_blks_read DESC;

-- =====================================================
-- MANTENIMIENTO DE ÍNDICES
-- =====================================================

-- Reindexar índices fragmentationados
REINDEX INDEX IF EXISTS idx_trips_composite_joins;
REINDEX INDEX IF EXISTS idx_deliveries_scheduled_datetime;
REINDEX INDEX IF EXISTS idx_maintenance_vehicle_cost;

-- Vacuum con analyze para actualizar estadísticas
VACUUM ANALYZE vehicles;
VACUUM ANALYZE drivers;
VACUUM ANALYZE routes;
VACUUM ANALYZE trips;
VACUUM ANALYZE deliveries;
VACUUM ANALYZE maintenance;

-- =====================================================
-- MONITOREO DE RENDIMIENTO
-- =====================================================

-- Tablas sin índices
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan
FROM pg_stat_user_tables
WHERE seq_scan > 0 AND idx_scan = 0
ORDER BY seq_scan DESC;
