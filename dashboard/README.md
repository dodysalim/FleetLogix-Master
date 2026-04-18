# FleetLogix · Dashboard Analítico

**Proyecto Integrador M2 · Henry Data Science**
**Autor:** Dody Dueñas
**Fecha:** Abril 2026
**Stack:** PostgreSQL 15 · Python 3.10 · Streamlit 1.36 · Plotly · SQLAlchemy

---

## 1. Propósito

Este directorio contiene todos los artefactos de **datos y modelado** que alimentan el dashboard ejecutivo de FleetLogix. La aplicación final se encuentra en la carpeta hermana **`../dashboard_streamlit/`** y se conecta directamente a la base de datos transaccional PostgreSQL (`fleetlogix_db`).

El dashboard cubre cinco dominios de análisis:

1. **Resumen Ejecutivo** — KPIs globales (flota, conductores, viajes, entregas).
2. **Flota** — Rendimiento por vehículo, utilización y mantenimiento.
3. **Conductores** — Ranking, tasa de éxito y alertas de licencia.
4. **Rutas** — Tráfico, distancia, consumo y eficiencia por corredor.
5. **Combustible** — Consumo mensual, eficiencia por tipo, sostenibilidad.

---

## 2. Estructura del directorio

```
dashboard/
├── README.md                       ← este archivo
├── MODELO_DATOS.md                 ← modelo estrella, relaciones, cardinalidades
├── KPIs.md                         ← catálogo de 15 KPIs (definición + fórmula SQL)
├── CHECKLIST_ENTREGA.md            ← lista de verificación pre-entrega
│
├── sql/
│   ├── 01_vistas_analiticas.sql    ← 8 vistas que consume Streamlit
│   ├── 02_queries_kpi.sql          ← queries parametrizables por KPI
│   ├── 03_dim_date.sql             ← generación de dimensión calendario
│   └── 04_export_csv.sql           ← comandos COPY para exportar tablas
│
├── data_exports/                   ← snapshots CSV (backup, uso offline)
├── docs/                           ← guía visual, troubleshooting
├── screenshots/                    ← capturas del dashboard
└── setup/                          ← scripts setup.ps1 / setup.sh + inspect_schema.py
```

La aplicación Streamlit vive en `../dashboard_streamlit/` (no en esta carpeta).

---

## 3. Inicio rápido

### 3.1 Levantar la base de datos

```powershell
# Windows (PowerShell)
PowerShell -ExecutionPolicy Bypass -File .\setup\setup.ps1
```

```bash
# Linux / Mac / WSL
bash setup/setup.sh
```

El script crea `fleetlogix_db`, carga los datos sintéticos y ejecuta las 8 vistas.

### 3.2 Lanzar el dashboard

```powershell
cd ..\dashboard_streamlit
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Abre `http://localhost:8501` — las 4 páginas extra están en el sidebar izquierdo.

---

## 4. Vistas analíticas (fuente de verdad)

| Vista | Filas aprox. | Propósito |
|-------|-------------:|-----------|
| `v_kpi_executive` | 1 | 12 KPIs globales (cards del Resumen) |
| `v_deliveries_timeseries` | ≈900 | Serie temporal diaria de entregas |
| `v_vehicle_performance` | ≈100 | Una fila por vehículo con métricas agregadas |
| `v_driver_performance` | ≈200 | Ranking conductores + licencias |
| `v_route_traffic` | ≈50 | Tráfico y consumo por ruta |
| `v_maintenance_alerts` | variable | Alertas con semaforización |
| `v_fuel_efficiency` | variable | Eficiencia mensual por tipo |
| `v_dim_date` | 1461 | Calendario 2024–2027 |

Ver `MODELO_DATOS.md` y `KPIs.md` para el detalle de columnas y fórmulas.

---

## 5. Credenciales por defecto

| Entorno | Usuario | Password | DB |
|---------|---------|----------|----|
| PostgreSQL local | `postgres` | `Dody2003` | `fleetlogix_db` |
| Docker compose | `admin_dody` | `secret_password_123` | `fleetlogix` |

Ajustar en `.env` de la raíz del proyecto.

---

## 6. Documentación extendida

- [`MODELO_DATOS.md`](MODELO_DATOS.md) · Modelo estrella y relaciones
- [`KPIs.md`](KPIs.md) · 15 KPIs con fórmula SQL
- [`docs/GUIA_VISUAL.md`](docs/GUIA_VISUAL.md) · Recorrido página por página
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) · FAQ y soluciones
- [`CHECKLIST_ENTREGA.md`](CHECKLIST_ENTREGA.md) · Checklist final de entrega
- [`../dashboard_streamlit/README.md`](../dashboard_streamlit/README.md) · Guía de la app Streamlit

---

**Nivel:** Senior · **Curso:** Full Stack Data Science M2 · **Institución:** Henry
