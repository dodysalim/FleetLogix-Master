-- =====================================================================
-- FLEETLOGIX · EXPORTACIÓN A CSV
-- ---------------------------------------------------------------------
-- Ejecutar con \i desde psql, o copiar bloque a bloque.
-- Genera los CSVs necesarios para análisis offline (Excel, Streamlit
-- standalone, notebooks, etc.) sin necesidad de PostgreSQL en vivo.
-- =====================================================================

-- Ajustar la ruta de destino según tu SO.
-- Windows (ejemplo):
--   \copy vehicles TO 'C:/Users/DODY DUEÑAS/Documents/.../dashboard/data_exports/vehicles.csv' CSV HEADER;

-- Linux / macOS:
--   \copy vehicles TO '/ruta/dashboard/data_exports/vehicles.csv' CSV HEADER;

\echo 'Exportando tablas crudas...'
\copy vehicles    TO 'dashboard/data_exports/vehicles.csv'    WITH (FORMAT CSV, HEADER, DELIMITER ',')
\copy drivers     TO 'dashboard/data_exports/drivers.csv'     WITH (FORMAT CSV, HEADER, DELIMITER ',')
\copy routes      TO 'dashboard/data_exports/routes.csv'      WITH (FORMAT CSV, HEADER, DELIMITER ',')
\copy trips       TO 'dashboard/data_exports/trips.csv'       WITH (FORMAT CSV, HEADER, DELIMITER ',')
\copy deliveries  TO 'dashboard/data_exports/deliveries.csv'  WITH (FORMAT CSV, HEADER, DELIMITER ',')
\copy maintenance TO 'dashboard/data_exports/maintenance.csv' WITH (FORMAT CSV, HEADER, DELIMITER ',')

\echo 'Exportando vistas analíticas...'
\copy (SELECT * FROM v_kpi_executive)          TO 'dashboard/data_exports/v_kpi_executive.csv'          WITH (FORMAT CSV, HEADER)
\copy (SELECT * FROM v_deliveries_timeseries)  TO 'dashboard/data_exports/v_deliveries_timeseries.csv'  WITH (FORMAT CSV, HEADER)
\copy (SELECT * FROM v_vehicle_performance)    TO 'dashboard/data_exports/v_vehicle_performance.csv'    WITH (FORMAT CSV, HEADER)
\copy (SELECT * FROM v_driver_performance)     TO 'dashboard/data_exports/v_driver_performance.csv'     WITH (FORMAT CSV, HEADER)
\copy (SELECT * FROM v_route_traffic)          TO 'dashboard/data_exports/v_route_traffic.csv'          WITH (FORMAT CSV, HEADER)
\copy (SELECT * FROM v_maintenance_alerts)     TO 'dashboard/data_exports/v_maintenance_alerts.csv'     WITH (FORMAT CSV, HEADER)
\copy (SELECT * FROM v_fuel_efficiency)        TO 'dashboard/data_exports/v_fuel_efficiency.csv'        WITH (FORMAT CSV, HEADER)
\copy (SELECT * FROM dim_date)                 TO 'dashboard/data_exports/dim_date.csv'                 WITH (FORMAT CSV, HEADER)

\echo 'Listo. CSVs disponibles en dashboard/data_exports/.'
