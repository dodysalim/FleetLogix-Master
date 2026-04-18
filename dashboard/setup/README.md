# 🛠️ Setup automático · FleetLogix

Esta carpeta contiene los scripts que **montan toda la infraestructura** que el dashboard Streamlit necesita para funcionar:

- PostgreSQL 15 (transaccional) — local o en Docker
- PostgREST (API REST) en Docker (opcional)
- Swagger UI en Docker (opcional)
- Esquema de tablas (`schema.sql`)
- Datos sintéticos (~535.000 filas)
- Dimensión de fechas `dim_date`
- 8 vistas analíticas listas para Streamlit

---

## 📦 Pre‑requisitos

| Software | Versión mínima | Verificación |
|----------|---------------|--------------|
| Docker Desktop | 24.x (opcional) | `docker --version` |
| PostgreSQL 15 | (si no usas Docker) | `psql --version` |
| Python | 3.10 | `python --version` |
| Streamlit | 1.36 | `pip install -r dashboard_streamlit/requirements.txt` |

> En Windows ejecuta los comandos desde **PowerShell**. En macOS/Linux/WSL/Git‑Bash, usa la versión `.sh`.

---

## 🚀 Uso rápido

### Windows (PowerShell)

```powershell
cd "C:\Users\DODY DUEÑAS\Documents\Poryecto2Henry\Proyecto2Dody"
PowerShell -ExecutionPolicy Bypass -File .\dashboard\setup\setup.ps1
```

### macOS / Linux / WSL

```bash
cd /ruta/al/proyecto/Proyecto2Dody
bash dashboard/setup/setup.sh
```

---

## ⚙️ Parámetros

| Parámetro PowerShell | Equivalente Bash | Descripción |
|----------------------|------------------|-------------|
| `-SkipData` | `--skip-data` | No regenera los 535k registros sintéticos |
| `-Force` | `--force` | `docker compose down -v` antes de arrancar (resetea la BD) |
| `-PgUser` | `PG_USER=...` | Override del usuario (default `postgres`) |
| `-PgPass` | `PG_PASS=...` | Override del password (default `Dody2003`) |
| `-PgDb`   | `PG_DB=...`   | Override del nombre de base (default `fleetlogix_db`) |
| `-PgPort` | `PG_PORT=...` | Override del puerto (default `5432`) |
| `-UseDocker` | `--use-docker` | Levanta `docker compose` en lugar de usar postgres local |

> **PostgreSQL local (default)**: usa las credenciales arriba.
> **Modo Docker (`-UseDocker`)**: cambia automáticamente a `admin_dody` / `secret_password_123` / `fleetlogix` (las del compose file).

### Ejemplos

```powershell
# Setup limpio (resetea volumen y regenera datos)
PowerShell -ExecutionPolicy Bypass -File .\dashboard\setup\setup.ps1 -Force

# Solo reaplica vistas, sin tocar datos
PowerShell -ExecutionPolicy Bypass -File .\dashboard\setup\setup.ps1 -SkipData
```

```bash
# Linux/Mac con credenciales personalizadas
PG_USER=fleet_admin PG_PASS='MiPassFuerte!' bash dashboard/setup/setup.sh --force
```

---

## 🔁 Pasos que ejecuta el script

```
1/8 ▸ Verifica prerequisitos      → Docker y Python en PATH
2/8 ▸ docker compose up -d        → Postgres + PostgREST + Swagger
3/8 ▸ pg_isready (max 60s)        → Espera health-check
4/8 ▸ sql/schema.sql              → Crea las 6 tablas + constraints
5/8 ▸ scripts/01_data_generation  → Faker · 535k filas
6/8 ▸ dashboard/sql/03_dim_date   → Tabla calendario 2024-2027
7/8 ▸ dashboard/sql/01_vistas     → 8 vistas v_*
8/8 ▸ Validación                  → SELECT COUNT(*) por objeto
```

Al final imprime un resumen y los pasos para lanzar la app Streamlit (`streamlit run`).

---

## 🌐 Servicios disponibles tras el setup

| Servicio | URL | Notas |
|---------|-----|-------|
| PostgreSQL | `localhost:5432` | Conexión nativa para Streamlit (via SQLAlchemy) |
| Dashboard Streamlit | `http://localhost:8501` | `cd dashboard_streamlit && streamlit run streamlit_app.py` |
| PostgREST  | `http://localhost:3000` | API REST sobre las tablas |
| Swagger UI | `http://localhost:8080` | Documentación interactiva |

---

## 🐛 Resolución de problemas

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| `docker: command not found` | Docker Desktop no instalado o no en PATH | Reinstalar Docker Desktop, reiniciar terminal |
| `PostgreSQL no respondió en 60s` | Puerto 5432 ocupado | `netstat -ano \| findstr :5432`, cerrar proceso |
| `python: command not found` | Python no instalado | Instalar Python 3.10+ y reabrir terminal, o usar `-SkipData` |
| `Ya hay N vehículos en la BD` | Datos previos | Usa `-Force` para resetear, o `-SkipData` para omitir |
| `permission denied` al `chmod +x` | Filesystem montado sin exec | Ejecutar `bash dashboard/setup/setup.sh` directamente |

Para más detalles ver `dashboard/docs/TROUBLESHOOTING.md`.

---

## ✅ Verificación manual

```bash
# Con PostgreSQL local
psql -h localhost -U postgres -d fleetlogix_db -c "\dv v_*"
psql -h localhost -U postgres -d fleetlogix_db -c "SELECT * FROM v_kpi_executive;"

# Con Docker
docker exec -it fleetlogix_postgres psql -U admin_dody -d fleetlogix -c "\dv v_*"
```

Debes ver las 8 vistas y una fila con los KPIs ejecutivos.
