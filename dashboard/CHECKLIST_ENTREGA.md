# ✅ Checklist de Entrega · FleetLogix Dashboard (Streamlit)

Lista exhaustiva para verificar que el proyecto esté listo para entregarse al jurado / cliente final.

---

## 1. Infraestructura local

- [ ] PostgreSQL 15 corriendo en `localhost:5432`
- [ ] (Opcional) Docker Desktop con `docker compose up -d` levanta `fleetlogix_postgres`, `fleetlogix_postgrest`, `fleetlogix_swagger`
- [ ] `localhost:5432` responde (PostgreSQL)
- [ ] (Opcional) `http://localhost:3000` responde (PostgREST)
- [ ] (Opcional) `http://localhost:8080` muestra Swagger UI

## 2. Base de datos

- [ ] Las 6 tablas existen: `vehicles`, `drivers`, `routes`, `trips`, `deliveries`, `maintenance`
- [ ] La tabla calendario `dim_date` existe y cubre 2024‑2027
- [ ] Las 8 vistas existen: `v_kpi_executive`, `v_deliveries_timeseries`, `v_vehicle_performance`, `v_driver_performance`, `v_route_traffic`, `v_maintenance_alerts`, `v_fuel_efficiency`, `v_dim_date`
- [ ] Los 11 índices están aplicados (`scripts/init_db.py` o `sql/03_optimization_indexes.sql`)
- [ ] `SELECT COUNT(*) FROM trips` ≥ 100.000 filas
- [ ] `SELECT COUNT(*) FROM deliveries` ≥ 300.000 filas

## 3. Dashboard Streamlit · Setup

- [ ] La carpeta `dashboard_streamlit/` existe con `streamlit_app.py` + `pages/` + `utils/`
- [ ] `pip install -r dashboard_streamlit/requirements.txt` se completa sin errores
- [ ] `streamlit run streamlit_app.py` abre `http://localhost:8501` sin trazas rojas
- [ ] El sidebar muestra "✅ Conectado" en el health-check
- [ ] El selector de fechas modifica la serie temporal del Resumen Ejecutivo

## 4. Dashboard Streamlit · Páginas

- [ ] Las 5 páginas son accesibles desde el sidebar:
  - [ ] 📊 **Resumen Ejecutivo** (entry point)
  - [ ] 🚚 **Flota**
  - [ ] 👨‍✈️ **Conductores**
  - [ ] 🛣️ **Rutas**
  - [ ] ⛽ **Combustible**
- [ ] Cada página tiene su `page_header` con título, subtítulo y badge
- [ ] Las 10 KPIs del Resumen Ejecutivo muestran números (no "—")
- [ ] La tarjeta "On-Time Rate" muestra un valor entre 70% y 95%
- [ ] El gráfico de timeseries muestra datos para todo el período
- [ ] El donut de estados de entrega renderiza con colores corporativos
- [ ] El scatter de Flota muestra al menos 50 puntos (vehículos)
- [ ] Los botones "⬇️ Descargar CSV" generan archivos válidos

## 5. Documentación

- [ ] `dashboard/README.md` actualizado (referencias a Streamlit, no Power BI)
- [ ] `dashboard/MODELO_DATOS.md` con diagrama estrella
- [ ] `dashboard/KPIs.md` con los 15 KPIs y sus fórmulas SQL
- [ ] `dashboard/setup/README.md` con instrucciones de los scripts
- [ ] `dashboard/docs/GUIA_VISUAL.md` con descripción página por página
- [ ] `dashboard/docs/TROUBLESHOOTING.md` con FAQs
- [ ] `dashboard_streamlit/README.md` con guía de la app

## 6. Notebooks

- [ ] `notebooks/Avance_1_DataGeneration.ipynb` ejecuta de principio a fin
- [ ] `notebooks/Avance_2_SQLAnalysis.ipynb` ejecuta y muestra los 12 análisis
- [ ] `notebooks/Avance_3_DataWarehouse.ipynb` describe el modelo Snowflake
- [ ] `notebooks/Avance_4_CloudArchitecture.ipynb` describe la arquitectura AWS
- [ ] Todos los notebooks tienen secciones (markdown), código limpio y conclusiones

## 7. Repositorio / Versionado

- [ ] `.gitignore` raíz excluye `.env`, `__pycache__`, `node_modules`, `.venv/`
- [ ] `dashboard_streamlit/.gitignore` excluye `.streamlit/secrets.toml` y `.venv/`
- [ ] Los archivos de credenciales NO están en el repo
- [ ] `LICENSE` presente en la raíz
- [ ] Mensajes de commit limpios, en español

## 8. Capturas de pantalla (entregable)

- [ ] `dashboard/screenshots/01_resumen_ejecutivo.png`
- [ ] `dashboard/screenshots/02_flota.png`
- [ ] `dashboard/screenshots/03_conductores.png`
- [ ] `dashboard/screenshots/04_rutas.png`
- [ ] `dashboard/screenshots/05_combustible.png`
- [ ] `dashboard/screenshots/00_modelo.png` (diagrama del modelo)

## 9. Pruebas

- [ ] `python -m pytest tests/` pasa sin errores
- [ ] Los queries de `dashboard/sql/02_queries_kpi.sql` retornan resultados consistentes
- [ ] Validación cruzada: la suma de `total_deliveries` en `v_deliveries_timeseries` ≈ `v_kpi_executive.delivered + pending + failed + ...`

## 10. Demo final

- [ ] Video grabado de 3‑5 min mostrando navegación por las 5 páginas
- [ ] Subido a YouTube / Drive con permiso "anyone with link"
- [ ] Link agregado al `README.md` raíz
- [ ] Presentación PPTX con: contexto, modelo, KPIs, arquitectura cloud, conclusiones

## 11. Cumplimiento Henry M2 (4 Avances)

- [ ] **Avance 1 · Generación de datos sintéticos** — ≥ 500.000 registros (Faker + Python)
- [ ] **Avance 2 · Queries analíticas + optimización** — `dashboard/sql/02_queries_kpi.sql` + `sql/03_optimization_indexes.sql`
- [ ] **Avance 3 · Modelo dimensional** — Star Schema documentado en `MODELO_DATOS.md` + `sql/snowflake_schema.sql`
- [ ] **Avance 4 · Arquitectura cloud** — AWS Serverless documentada en `notebooks/Avance_4_CloudArchitecture.ipynb`
- [ ] **Bonus · Dashboard interactivo** — App Streamlit corriendo en `localhost:8501`
- [ ] **Bonus · API REST** — PostgREST en `localhost:3000` (vía docker-compose)
- [ ] **Bonus · IoT layer** — MongoDB para telemetría (mencionado en `docs/PI_M2_DOCUMENTATION_DODY.md`)
