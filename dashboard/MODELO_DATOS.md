# Modelo de Datos — Dashboard FleetLogix

**Proyecto Integrador M2 — Henry Data Science**

Este documento describe el **modelo lógico** que usa el dashboard Streamlit, derivado del esquema relacional (3NF) de PostgreSQL.

---

## 1. Visión general

El modelo combina:

- **6 tablas transaccionales** (base PostgreSQL, 3NF).
- **8 vistas analíticas** (`v_*`) optimizadas para consumo desde Streamlit.
- **1 dimensión calendario** (`dim_date`) para análisis de series temporales.

| Modo | Fuente | Ventaja |
|------|--------|---------|
| **Vistas** (recomendado) | `v_kpi_executive`, `v_vehicle_performance`, etc. | Menos filas · agregaciones listas · refresh < 100 ms con cache de Streamlit |
| **Tablas crudas**        | `vehicles`, `drivers`, `trips`, etc. | Granularidad fina (drill-down hasta el viaje individual) |

La app Streamlit usa **vistas exclusivamente** — mantiene la lógica de negocio en SQL (PostgreSQL) y la lógica de presentación en Python (Plotly).

---

## 2. Esquema estrella (tablas crudas)

```
                      ┌──────────────────┐
                      │    dim_date      │
                      │  (2024 - 2027)   │
                      └────────┬─────────┘
                               │ 1:N
                               ▼
┌────────────┐ 1:N    ┌────────────┐     1:N   ┌───────────┐
│   routes   ├───────►│   trips    │◄──────────┤ vehicles  │
└────────────┘        │ (fact)     │           └─────┬─────┘
                      └─────┬──────┘                 │ 1:N
                            │ 1:N                     ▼
                            ▼                  ┌─────────────┐
                      ┌──────────────┐         │ maintenance │
                      │ deliveries   │         └─────────────┘
                      │   (fact)     │
                      └──────────────┘
                            ▲ 1:N
                            │
                      ┌─────┴──────┐
                      │   drivers  │
                      └────────────┘
```

---

## 3. Relaciones

| # | From (Many) | Column | To (One) | Column |
|---|-------------|--------|----------|--------|
| 1 | `trips` | `vehicle_id` | `vehicles` | `vehicle_id` |
| 2 | `trips` | `driver_id` | `drivers` | `driver_id` |
| 3 | `trips` | `route_id` | `routes` | `route_id` |
| 4 | `deliveries` | `trip_id` | `trips` | `trip_id` |
| 5 | `maintenance` | `vehicle_id` | `vehicles` | `vehicle_id` |
| 6 | `trips.departure_date` | (calculada de `departure_datetime`) | `dim_date` | `date` |
| 7 | `deliveries.scheduled_date` | (calculada de `scheduled_datetime`) | `dim_date` | `date` |

---

## 4. Cardinalidades esperadas

| Tabla         | Tipo       | Filas aprox. | Granularidad             |
|---------------|------------|--------------|--------------------------|
| `vehicles`    | Dimension  | 1.000        | 1 fila / vehículo        |
| `drivers`     | Dimension  | 5.000        | 1 fila / conductor       |
| `routes`      | Dimension  | 500          | 1 fila / ruta            |
| `trips`       | Fact       | 130.000      | 1 fila / viaje           |
| `deliveries`  | Fact       | 400.000      | 1 fila / entrega         |
| `maintenance` | Fact       | 5.000        | 1 fila / mantenimiento   |
| `dim_date`    | Dimension  | 1.461        | 1 fila / día 2024-2027   |

---

## 5. Vistas analíticas (capa de servicio)

| Vista | SELECT base | Granularidad | Consumida por |
|-------|-------------|--------------|---------------|
| `v_kpi_executive` | 12 sub-queries agregadas | 1 fila | Página 1 (10 KPI cards) |
| `v_deliveries_timeseries` | `GROUP BY DATE(scheduled_datetime)` | 1 fila / día | Página 1 (line + bar) |
| `v_vehicle_performance` | `vehicles JOIN trips JOIN routes` | 1 fila / vehículo | Página 2 (Flota) |
| `v_driver_performance` | `drivers JOIN trips JOIN deliveries` | 1 fila / conductor | Página 3 |
| `v_route_traffic` | `routes JOIN trips JOIN deliveries` | 1 fila / ruta | Página 4 |
| `v_maintenance_alerts` | `maintenance JOIN vehicles` | 1 fila / mantenimiento | Página 2 (alertas) |
| `v_fuel_efficiency` | `GROUP BY month, vehicle_type, fuel_type` | n filas | Página 5 |
| `v_dim_date` | `WITH RECURSIVE` 2024-2027 | 1.461 filas | Reutilizable |

---

## 6. Tipos de datos clave

| Tabla        | Columna                | Tipo PostgreSQL | Notas |
|--------------|------------------------|-----------------|-------|
| `vehicles`   | `vehicle_id`           | `serial`        | PK |
| `vehicles`   | `capacity_kg`          | `numeric`       | Para % utilización |
| `vehicles`   | `acquisition_date`     | `date`          | Antigüedad |
| `drivers`    | `license_expiry`       | `date`          | Alerta KPI 15 |
| `trips`      | `departure_datetime`   | `timestamp`     | Eje temporal |
| `trips`      | `arrival_datetime`     | `timestamp`     | Duración |
| `trips`      | `fuel_consumed_liters` | `numeric`       | KPI 06, 07 |
| `deliveries` | `scheduled_datetime`   | `timestamp`     | Eje temporal |
| `deliveries` | `delivered_datetime`   | `timestamp`     | KPI 05 |
| `deliveries` | `package_weight_kg`    | `numeric`       | KPI 12, 13 |
| `maintenance`| `cost`                 | `numeric`       | KPI 09 |
| `maintenance`| `next_maintenance_date`| `date`          | KPI 11 |
| `dim_date`   | `date`                 | `date` (PK)     | Calendario |

---

## 7. Índices de soporte (definidos en `sql/03_optimization_indexes.sql`)

Los índices más críticos para que las vistas refresquen rápido:

```sql
CREATE INDEX idx_trips_status            ON trips(status);
CREATE INDEX idx_trips_vehicle_id        ON trips(vehicle_id);
CREATE INDEX idx_trips_driver_id         ON trips(driver_id);
CREATE INDEX idx_trips_route_id          ON trips(route_id);
CREATE INDEX idx_trips_departure_date    ON trips(DATE(departure_datetime));
CREATE INDEX idx_deliveries_trip_id      ON deliveries(trip_id);
CREATE INDEX idx_deliveries_status       ON deliveries(delivery_status);
CREATE INDEX idx_deliveries_sched_date   ON deliveries(DATE(scheduled_datetime));
CREATE INDEX idx_maintenance_vehicle     ON maintenance(vehicle_id);
CREATE INDEX idx_maintenance_next_date   ON maintenance(next_maintenance_date);
CREATE INDEX idx_drivers_license_expiry  ON drivers(license_expiry);
```

---

## 8. Política de refresco

| Capa | Mecanismo | Frecuencia |
|------|-----------|------------|
| Tablas transaccionales | INSERTs directos | Tiempo real |
| Vistas `v_*` | Definidas como **VIEWs** (no materialized) → recalculan en cada SELECT | On-demand |
| Caché Streamlit | `@st.cache_data(ttl=300)` | 5 minutos |
| Botón manual | "🔄 Refrescar datos" en el sidebar | Bajo demanda |

Si el volumen creciera mucho (>10M filas), conviene migrar las vistas a `MATERIALIZED VIEW` con refresh programado (`pg_cron` o tarea Airflow).

---

*Dody Dueñas — Henry Data Science M2 — Abril 2026*
