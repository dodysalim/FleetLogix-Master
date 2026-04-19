# 🚛 FleetLogix Analytics · Dashboard Streamlit

> Dashboard corporativo multipágina, nivel empresarial, conectado a PostgreSQL.
> Stack 100 % Python: Streamlit 1.36 + Plotly 5.22 + SQLAlchemy 2.0.

---

## ✨ Qué incluye

| Página | Icono | Contenido |
|--------|-------|-----------|
| **Resumen Ejecutivo** | 📊 | 10 KPIs · Serie temporal · Donut de estados · Volumen vs peso |
| **Flota** | 🚚 | KPIs · Top vehículos · Scatter eficiencia · Alertas de mantenimiento |
| **Conductores** | 👨‍✈️ | Ranking · Tasa éxito · Alertas de licencia · Detalle |
| **Rutas** | 🛣️ | Top corredores · Eficiencia por ruta · Detalle |
| **Combustible** | ⛽ | Tendencia mensual · Eficiencia por tipo · Composición · Detalle |

Características: tema oscuro corporativo, Plotly interactivo, caché 5 min, descarga CSV, filtros por página, health-check de BD, refresh manual.

---

## 🚀 Inicio rápido (Windows)

Asumimos que PostgreSQL ya tiene la base `fleetlogix_db` cargada con las 8 vistas (`v_kpi_executive`, `v_deliveries_timeseries`, `v_vehicle_performance`, `v_driver_performance`, `v_route_traffic`, `v_maintenance_alerts`, `v_fuel_efficiency`, `v_dim_date`).

### 1. Crear entorno virtual e instalar dependencias

```powershell
cd C:\Users\DODY DUEÑAS\Documents\Poryecto2Henry\Proyecto2Dody\dashboard_streamlit
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configurar conexión

La app lee credenciales del archivo `.env` **raíz del proyecto** (ya existe):

```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=fleetlogix_db
```

Si prefieres, puedes crear `dashboard_streamlit/.streamlit/secrets.toml`:

```toml
[postgres]
host     = "localhost"
port     = "5432"
user     = "postgres"
password = "your_password"
dbname   = "fleetlogix_db"
```

### 3. Lanzar la app

```powershell
streamlit run streamlit_app.py
```

Se abrirá `http://localhost:8501` con el dashboard completo. Las 4 páginas restantes aparecen en la barra lateral izquierda.

---

## 📁 Estructura

```
dashboard_streamlit/
├── streamlit_app.py              # Página 1: Resumen Ejecutivo (entry point)
├── pages/
│   ├── 2_🚚_Flota.py
│   ├── 3_👨‍✈️_Conductores.py
│   ├── 4_🛣️_Rutas.py
│   └── 5_⛽_Combustible.py
├── utils/
│   ├── __init__.py
│   ├── db.py                     # Engine SQLAlchemy + helpers cacheados
│   └── styling.py                # Tema, paleta, componentes UI
├── .streamlit/
│   └── config.toml               # Tema oscuro corporativo
├── requirements.txt
└── README.md
```

---

## 🎨 Tema corporativo

- **Paleta:** cyan (#4CC9F0) · teal (#00D4AA) · ámbar (#F8B400) · rojo (#EF4444)
- **Fondo:** #0E1117 (dark) · tarjetas #1A1F2E
- **Tipografía:** Inter / system-ui

Toda la paleta se aplica tanto a CSS custom como a los gráficos Plotly.

---

## 🧪 Validación rápida

Desde `psql`:

```sql
SELECT * FROM v_kpi_executive;
SELECT COUNT(*) FROM v_deliveries_timeseries;
SELECT COUNT(*) FROM v_vehicle_performance;
SELECT COUNT(*) FROM v_driver_performance;
SELECT COUNT(*) FROM v_route_traffic;
SELECT COUNT(*) FROM v_maintenance_alerts;
SELECT COUNT(*) FROM v_fuel_efficiency;
```

Las 7 queries deben devolver filas (la primera: 1 fila con 12 columnas).

---

## 🆘 Problemas comunes

| Síntoma | Solución |
|---------|----------|
| `OperationalError: could not connect to server` | Verifica que PostgreSQL 15 esté corriendo y credenciales en `.env` |
| `relation "v_kpi_executive" does not exist` | Ejecuta `dashboard/sql/01_vistas_analiticas.sql` en `fleetlogix_db` |
| Tarjetas vacías / en blanco | Click en "🔄 Refrescar datos" en el sidebar |
| Plotly no renderiza | `pip install --upgrade plotly` dentro del venv |
| Puerto 8501 ocupado | `streamlit run streamlit_app.py --server.port 8502` |

---

## 📦 Dependencias

- streamlit 1.36 · pandas 2.2 · sqlalchemy 2.0
- psycopg2-binary · plotly 5.22 · python-dotenv

---

**Autor:** Dody Dueñas · **Proyecto Integrador M2** · Henry Data Science · 2026
