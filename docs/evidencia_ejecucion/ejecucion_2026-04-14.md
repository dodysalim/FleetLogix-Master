# FleetLogix - Evidencia de Ejecucion Real
## Proyecto Integrador M2 - Henry Data Science
## Fecha de Ejecucion: 2026-04-14 17:19:00

================================================================================
FASE 1: REGENERACION DE ESQUEMA
================================================================================

[OK] Tablas eliminadas
[OK] Esquema recreado

================================================================================
FASE 2: GENERACION DE DATOS
================================================================================

============================================================
FleetLogix - Data Generation Pipeline
Author: Dody Dueñas
Project: Henry M2 - FleetLogix Enterprise
============================================================

============================================================
Pipeline Execution Summary:
Status: success
Duration: 101.36 seconds

Records Generated:
  vehicles: 200
  drivers: 400
  routes: 50
  trips: 100,000
  deliveries: 399,924
  maintenance: 4,908
============================================================

================================================================================
VERIFICACION DE REGISTROS GENERADOS
================================================================================

vehicles: 200
drivers: 400
routes: 48
maintenance: 4,908
trips: 100,000
deliveries: 399,924

================================================================================
FASE 3: EJECUCION DE CONSULTAS SQL (12 QUERIES)
================================================================================

============================================================
QUERY 1: Active Vehicles
============================================================
Total: 184 vehicles

============================================================
QUERY 2: Vehicle Count by Type
============================================================
  ('Motocicleta', 58, Decimal('50.00'))
  ('Van', 51, Decimal('1500.00'))
  ('Camión Grande', 47, Decimal('5000.00'))
  ('Camión Mediano', 44, Decimal('3000.00'))

============================================================
QUERY 3: Top 5 Longest Routes
============================================================
  ('R010', 'Bogotá', 'Cartagena', Decimal('1080.94'))
  ('R011', 'Bogotá', 'Cartagena', Decimal('1080.58'))
  ('R029', 'Cali', 'Cartagena', Decimal('1067.11'))
  ('R030', 'Cali', 'Cartagena', Decimal('1066.34'))
  ('R046', 'Cartagena', 'Cali', Decimal('1060.96'))

============================================================
QUERY 4: Trips with Complete Info
============================================================
  (99993, 'MTO641', 'Francisco', 'R013', 'completed')
  (99981, 'RJW229', 'Gloria', 'R026', 'completed')
  (99995, 'RJV206', 'Ángel', 'R042', 'completed')
  (99987, 'OLJ940', 'Carlos', 'R025', 'completed')
  (99982, 'KIG785', 'Eduardo', 'R036', 'completed')

============================================================
QUERY 5: Driver Performance
============================================================
  ('Jaime', 'Ospina', 311, Decimal('19702.32'))
  ('Santiago', 'Ramírez', 310, Decimal('21122.64'))
  ('Andrés', 'Guerrero', 309, Decimal('21306.25'))
  ('Dayana', 'Escobar', 308, Decimal('20451.99'))
  ('Sandra', 'Flórez', 306, Decimal('20599.77'))

============================================================
QUERY 6: Delivery Analysis by City
============================================================
  ('Bogotá', 99668, 99668)
  ('Barranquilla', 75755, 75755)
  ('Cartagena', 75302, 75302)
  ('Cali', 74928, 74928)
  ('Medellín', 74271, 74271)

============================================================
QUERY 7: Fuel Consumption by Route
============================================================
  ('R011', 2118, Decimal('263679.88'))
  ('R029', 2119, Decimal('260077.25'))
  ('R010', 2094, Decimal('259519.43'))
  ('R045', 2094, Decimal('256484.55'))
  ('R041', 2100, Decimal('255396.64'))

============================================================
QUERY 8: Monthly Delivery Analysis (CTE)
============================================================
  ('2026-03', Decimal('5389'), Decimal('0'))
  ('2026-02', Decimal('16079'), Decimal('0'))
  ('2026-01', Decimal('17881'), Decimal('0'))
  ('2025-12', Decimal('17823'), Decimal('0'))
  ('2025-11', Decimal('17412'), Decimal('0'))

============================================================
QUERY 9: Maintenance Cost by Vehicle (CTE)
============================================================
  ('Motocicleta', 58, Decimal('1478'), Decimal('455195180.88'))
  ('Van', 51, Decimal('1162'), Decimal('367485645.16'))
  ('Camión Mediano', 44, Decimal('1121'), Decimal('353233702.07'))
  ('Camión Grande', 47, Decimal('1147'), Decimal('351156030.33'))

============================================================
QUERY 10: Vehicle Performance (WINDOW)
============================================================
  ('CFA518', 'Camión Grande', 610, Decimal('40626.11'), 1)
  ('ZRV836', 'Camión Grande', 591, Decimal('38797.71'), 2)
  ('PPG985', 'Camión Grande', 590, Decimal('38511.47'), 3)
  ('IKD891', 'Camión Grande', 582, Decimal('38966.31'), 4)
  ('MTO641', 'Camión Grande', 570, Decimal('36893.13'), 5)
  ('ASJ580', 'Camión Grande', 567, Decimal('36525.04'), 6)
  ('GKD860', 'Camión Grande', 565, Decimal('37087.30'), 7)
  ('OHC553', 'Camión Grande', 565, Decimal('37571.00'), 7)
  ('HMD683', 'Camión Grande', 565, Decimal('37845.24'), 7)
  ('GTQ864', 'Camión Grande', 563, Decimal('37993.81'), 10)

============================================================
QUERY 11: Drivers with License Expiring
============================================================
  (113, 'EMP00113', 'Karen', 'Vásquez', datetime.date(2026, 4, 13), 0)
  (6, 'EMP00006', 'Marina', 'Fernández', datetime.date(2026, 4, 23), 0)
  (73, 'EMP00073', 'Edinson', 'Rubio', datetime.date(2026, 4, 27), 0)
  (29, 'EMP00029', 'Tatiana', 'Cortés', datetime.date(2026, 4, 30), 0)
  (181, 'EMP00181', 'Lorena', 'Díaz', datetime.date(2026, 5, 4), 0)
  (219, 'EMP00219', 'Camilo', 'Álvarez', datetime.date(2026, 5, 4), 0)
  (57, 'EMP00057', 'Jesús', 'Ríos', datetime.date(2026, 5, 5), 0)
  (393, 'EMP00393', 'David', 'Espitia', datetime.date(2026, 5, 12), 0)

============================================================
QUERY 12: EXECUTIVE SUMMARY (MULTI-CTE)
============================================================
  (200, 184, 400, 375, 100000, 100000, 399924, 399924, Decimal('100.00'), Decimal('1527070558.44'))

[OK] All queries executed successfully

================================================================================
FASE 4: INDICES DE OPTIMIZACION
================================================================================

============================================================
CREATING OPTIMIZATION INDEXES
============================================================

[OK] idx_trips_composite_joins
[OK] idx_deliveries_scheduled_datetime
[OK] idx_maintenance_vehicle_cost
[OK] idx_drivers_status_license
[OK] idx_routes_metrics
[OK] idx_deliveries_covering
[OK] idx_trips_departure_brin
[OK] idx_trips_completed
[OK] idx_deliveries_pending
[OK] idx_drivers_license_expiry
[OK] idx_vehicles_type_status
[OK] ANALYZE tables

============================================================
INDEXES VERIFICATION
============================================================
  idx_deliveries_covering: scans=0, reads=0, fetched=0
  idx_deliveries_pending: scans=0, reads=0, fetched=0
  idx_deliveries_scheduled_datetime: scans=0, reads=0, fetched=0
  idx_drivers_license_expiry: scans=0, reads=0, fetched=0
  idx_drivers_status_license: scans=0, reads=0, fetched=0
  idx_maintenance_vehicle_cost: scans=0, reads=0, fetched=0
  idx_routes_metrics: scans=0, reads=0, fetched=0
  idx_trips_completed: scans=0, reads=0, fetched=0
  idx_trips_composite_joins: scans=0, reads=0, fetched=0
  idx_trips_departure_brin: scans=0, reads=0, fetched=0
  idx_vehicles_type_status: scans=0, reads=0, fetched=0

[OK] 11 indexes created successfully

================================================================================
FASE 5: ETL PIPELINE
================================================================================

============================================================
ETL PIPELINE - EXTRACTION PHASE
============================================================

[OK] Connecting to PostgreSQL
[OK] Extracting data from vehicles...
    Extracted: 200 records
[OK] Extracting data from drivers...
    Extracted: 400 records
[OK] Extracting data from routes...
    Extracted: 48 records
[OK] Extracting data from trips...
    Extracted: 10000 records
[OK] Extracting data from deliveries...
    Extracted: 10000 records
[OK] Extracting data from maintenance...
    Extracted: 4908 records

============================================================
ETL PIPELINE - TRANSFORMATION PHASE
============================================================

[OK] Transforming vehicles dimension...
    Transformed: 200 records
[OK] Transforming drivers dimension...
    Transformed: 400 records
[OK] Transforming routes dimension...
    Transformed: 48 records
[OK] Transforming trips fact table...
    Transracted: 10000 records
[OK] Transforming deliveries fact table...
    Transformed: 10000 records
[OK] Transforming maintenance fact table...
    Transformed: 4908 records

============================================================
ETL PIPELINE - SUMMARY
============================================================

Vehicles dimension: 200 records
Drivers dimension: 400 records
Routes dimension: 48 records
Trips fact: 10000 records
Deliveries fact: 10000 records
Maintenance fact: 4908 records

[OK] ETL Pipeline completed (Extract + Transform phases)
NOTE: Load phase requires Snowflake connection

================================================================================
RESUMEN EJECUTIVO
================================================================================

Total de registros en PostgreSQL:
  - vehicles: 200
  - drivers: 400
  - routes: 48
  - trips: 100,000
  - deliveries: 399,924
  - maintenance: 4,908
  =================
  TOTAL: 505,580 registros

Consultas SQL ejecutadas: 12
Indices de optimizacion creados: 11

ETL Pipeline: Extract + Transform completado
(Carga a Snowflake requiere credenciales de Snowflake)

================================================================================
FIN DE EVIDENCIA DE EJECUCION
================================================================================