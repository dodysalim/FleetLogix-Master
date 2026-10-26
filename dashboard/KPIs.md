# Catálogo de KPIs — FleetLogix Dashboard (Streamlit)

**Proyecto Integrador M2 — Henry Data Science**

Este catálogo documenta los **15 KPIs** que alimentan el dashboard. Cada KPI incluye: definición de negocio, fórmula SQL, unidad, frecuencia, target y visual recomendado.

---

## Código de semáforos

- 🟢 **Verde** — objetivo cumplido / saludable
- 🟡 **Amarillo** — en riesgo / requiere atención
- 🔴 **Rojo** — crítico / acción inmediata

---

## KPI 01 · Vehículos Activos

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Categoría**   | Operaciones / Flota                                                   |
| **Definición**  | Número de vehículos en estado operativo (`active`) en la flota.       |
| **SQL**         | `SELECT COUNT(*) FROM vehicles WHERE status = 'active';`              |
| **Vista**       | `v_kpi_executive.active_vehicles`                                     |
| **Unidad**      | Unidades (vehículos)                                                  |
| **Frecuencia**  | Tiempo real                                                           |
| **Target**      | N/A (monitoreo)                                                       |
| **Visual**      | KPI card con icono 🚛                                                 |
| **Página**      | 1 · Resumen Ejecutivo                                                 |

---

## KPI 02 · Conductores Activos

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | Conductores actualmente disponibles para operación.                   |
| **SQL**         | `SELECT COUNT(*) FROM drivers WHERE status = 'active';`               |
| **Vista**       | `v_kpi_executive.active_drivers`                                      |
| **Visual**      | KPI card con icono 👨‍✈️                                              |
| **Página**      | 1 · Resumen · 3 · Conductores                                         |

---

## KPI 03 · Viajes Completados

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | Viajes con estado `completed`.                                        |
| **SQL**         | `SELECT COUNT(*) FROM trips WHERE status='completed';`                |
| **Vista**       | `v_kpi_executive.completed_trips`                                     |
| **Target**      | ↑ Tendencia mensual creciente                                         |
| **Visual**      | KPI card + tendencia mensual en página Combustible                    |
| **Página**      | 1 · Resumen Ejecutivo                                                 |

---

## KPI 04 · Entregas Realizadas

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | Entregas con estado `delivered`.                                      |
| **SQL**         | `SELECT COUNT(*) FROM deliveries WHERE delivery_status='delivered';`  |
| **Vista**       | `v_kpi_executive.delivered`                                           |
| **Target**      | ↑                                                                     |
| **Visual**      | KPI card + serie temporal en tab "Tendencia diaria"                   |
| **Página**      | 1 · Resumen                                                           |

---

## KPI 05 · On-Time Delivery Rate ⭐ (métrica clave)

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | % de entregas que llegaron dentro de los 30 minutos del horario agendado. |
| **Fórmula**     | `100 × delivered_on_time / total_delivered`                           |
| **SQL**         | Ver `sql/02_queries_kpi.sql` bloque KPI 05.                           |
| **Vista**       | `v_kpi_executive.on_time_rate_pct`                                    |
| **Target**      | 🟢 ≥ 90 % · 🟡 70-90 % · 🔴 < 70 %                                    |
| **Visual**      | KPI card con color condicional (semáforo dinámico)                    |
| **Página**      | 1 · Resumen Ejecutivo                                                 |

---

## KPI 06 · Consumo promedio por viaje

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | Litros consumidos en promedio por cada viaje.                         |
| **SQL**         | `SELECT AVG(fuel_consumed_liters) FROM trips;`                        |
| **Vista**       | `v_kpi_executive.avg_fuel_per_trip` · `v_vehicle_performance.avg_fuel_per_trip` |
| **Unidad**      | Litros                                                                |
| **Target**      | ↓ Tendencia descendente (optimización)                                |
| **Visual**      | Card + comparación por tipo de vehículo                               |
| **Página**      | 5 · Combustible                                                       |

---

## KPI 07 · Eficiencia L/100km

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | Litros consumidos por cada 100 km recorridos (menor = mejor).         |
| **Fórmula**     | `100 × SUM(fuel) / SUM(distance)`                                     |
| **Vista**       | `v_fuel_efficiency.fuel_efficiency_l_per_100km`                       |
| **Target**      | 🟢 < 25 · 🟡 25-35 · 🔴 > 35 (camiones medianos)                      |
| **Visual**      | Bar chart por tipo + scatter en página Flota                          |
| **Página**      | 5 · Combustible · 2 · Flota                                           |

---

## KPI 08 · Tasa de fallos de entrega

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | % de entregas con estado `failed` sobre el total.                     |
| **SQL**         | `SELECT 100.0 * SUM(CASE WHEN delivery_status='failed' THEN 1 END) / COUNT(*) FROM deliveries;` |
| **Vista**       | Calculado a partir de `v_kpi_executive.failed_deliveries`             |
| **Target**      | 🟢 ≤ 2 % · 🟡 2-5 % · 🔴 > 5 %                                         |
| **Visual**      | KPI card con color condicional + serie temporal                       |
| **Página**      | 1 · Resumen                                                           |

---

## KPI 09 · Costo total de mantenimiento

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | Suma de costos de todas las operaciones de mantenimiento.             |
| **SQL**         | `SELECT SUM(cost) FROM maintenance;`                                  |
| **Vista**       | `v_kpi_executive.total_maintenance_cost`                              |
| **Unidad**      | Moneda                                                                |
| **Visual**      | KPI card · Tabla de alertas en Flota                                  |
| **Página**      | 1 · Resumen · 2 · Flota                                               |

---

## KPI 10 · Costo por viaje

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | Costo promedio de mantenimiento asignable a cada viaje completado.    |
| **SQL**         | `SELECT SUM(m.cost) / NULLIF(COUNT(t.trip_id), 0) FROM maintenance m JOIN trips t ON …;` |
| **Target**      | ↓                                                                     |
| **Visual**      | Card + bar chart por tipo de vehículo                                 |
| **Página**      | 2 · Flota                                                             |

---

## KPI 11 · Vehículos con mantenimiento próximo (30 días)

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | Vehículos cuyo próximo mantenimiento ocurre en los próximos 30 días.  |
| **Vista**       | `v_kpi_executive.vehicles_maintenance_30d` · `v_maintenance_alerts`   |
| **Acción**      | Trigger para alerta operativa (planificar taller).                    |
| **Visual**      | KPI card de alerta + tabla detallada con semáforo de niveles          |
| **Página**      | 1 · Resumen · 2 · Flota                                               |

---

## KPI 12 · Toneladas transportadas

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | Toneladas métricas totales entregadas.                                |
| **SQL**         | `SELECT SUM(package_weight_kg)/1000 FROM deliveries;`                 |
| **Vista**       | `v_kpi_executive.total_tons`                                          |
| **Visual**      | Card + área temporal en tab "Volumen vs Peso"                         |
| **Página**      | 1 · Resumen                                                           |

---

## KPI 13 · Utilización de capacidad

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | % promedio de capacidad aprovechada por viaje (`weight / capacity`).  |
| **Vista**       | `v_vehicle_performance.avg_capacity_utilization_pct`                  |
| **Target**      | 🟢 60–85 % · 🟡 < 60 % (subutilización) · 🔴 > 85 % (sobrecarga)      |
| **Visual**      | Scatter en Flota · KPI card promedio                                  |
| **Página**      | 2 · Flota                                                             |

---

## KPI 14 · Tasa de éxito por conductor

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | % de entregas exitosas sobre las asignadas a cada conductor.          |
| **SQL**         | `100 × SUM(CASE WHEN delivery_status='delivered' THEN 1 END) / COUNT(*)` |
| **Vista**       | `v_driver_performance.success_rate_pct`                               |
| **Target**      | 🟢 ≥ 85 % · 🟡 70-85 % · 🔴 < 70 %                                    |
| **Visual**      | Bar chart top-N coloreado por % éxito                                 |
| **Página**      | 3 · Conductores                                                       |

---

## KPI 15 · Licencias por vencer (30 días)

| Atributo        | Valor                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Definición**  | Conductores activos cuya licencia vence en los próximos 30 días.      |
| **Vista**       | `v_driver_performance.license_status` con valores `VENCIDA / POR VENCER / VIGENTE` |
| **Acción**      | Trigger para RRHH (renovación).                                       |
| **Visual**      | KPI card de alerta + donut + tabla detalle filtrada                   |
| **Página**      | 3 · Conductores                                                       |

---

## Resumen de targets

| KPI                    | 🟢 Verde      | 🟡 Amarillo  | 🔴 Rojo     |
|------------------------|---------------|--------------|-------------|
| On-Time Rate           | ≥ 90 %        | 70-90 %      | < 70 %      |
| Failure Rate           | ≤ 2 %         | 2-5 %        | > 5 %       |
| Driver Success Rate    | ≥ 85 %        | 70-85 %      | < 70 %      |
| Capacity Utilization   | 60-85 %       | 45-60 %      | < 45 % / > 85 % |
| Fuel Efficiency L/100km| < 25          | 25-35        | > 35        |

---

## Dónde se calcula cada KPI

Todos los KPIs se calculan en las **8 vistas SQL** definidas en `sql/01_vistas_analiticas.sql`. La app Streamlit (`dashboard_streamlit/`) consume directamente esas vistas via `utils/db.py` con caché de 5 minutos.

| Vista | KPIs que alimenta |
|-------|------------------|
| `v_kpi_executive` | 1, 2, 3, 4, 5, 6, 8, 9, 11, 12 |
| `v_vehicle_performance` | 6, 7, 10, 13 |
| `v_driver_performance` | 14, 15 |
| `v_fuel_efficiency` | 7 |
| `v_maintenance_alerts` | 11 |

---

*Dody Dueñas — Henry Data Science M2 — Abril 2026*
