# 🆘 Troubleshooting · FleetLogix Dashboard (Streamlit)

Compendio de problemas frecuentes y sus soluciones, en orden de aparición típico
(setup → datos → Streamlit).

---

## 1. Docker / contenedores (opcional)

> La app Streamlit funciona con PostgreSQL local sin Docker. Esta sección aplica si usas el stack completo (Postgres + PostgREST + Swagger).

### `docker: command not found`
- **Causa:** Docker Desktop no está instalado o el binario no está en el PATH.
- **Fix:** Instalar Docker Desktop (https://docs.docker.com/desktop/), reiniciar terminal.

### `Cannot connect to the Docker daemon`
- **Causa:** Docker Desktop está cerrado.
- **Fix (Windows/Mac):** Abrir Docker Desktop desde el menú Inicio. Esperar a que el ícono se ponga verde.
- **Fix (Linux):** `sudo systemctl start docker`.

### `port is already allocated` (5432, 3000, 8080)
- **Causa:** Otro PostgreSQL/servicio ocupa el puerto.
- **Diagnóstico (Windows):**
  ```powershell
  netstat -ano | findstr :5432
  taskkill /PID <PID> /F
  ```
- **Diagnóstico (Linux/Mac):**
  ```bash
  lsof -i :5432
  kill -9 <PID>
  ```
- **Alternativa:** Cambiar el mapeo de puertos en `docker-compose.yml` (`"5433:5432"` p.ej.) y ajustar `.env`.

### `fleetlogix_postgres exited with code 1`
- **Fix:** `docker compose down -v && docker compose up -d` (⚠ borra datos).

---

## 2. Generación de datos

### `ModuleNotFoundError: No module named 'faker'`
- **Fix:**
  ```bash
  pip install -r requirements.txt
  ```

### `psycopg2.OperationalError: FATAL: password authentication failed`
- **Causa:** Las credenciales no coinciden.
- **Fix (PostgreSQL local · default):**
  ```
  DB_HOST=localhost
  DB_PORT=5432
  DB_USER=postgres
  DB_PASSWORD=Dody2003
  DB_NAME=fleetlogix_db
  ```
- **Fix (Docker):** ver `docker-compose.yml`:
  ```
  DB_USER=admin_dody
  DB_PASSWORD=secret_password_123
  DB_NAME=fleetlogix
  ```

### El script tarda mucho (> 10 min)
- **Causa:** Inserciones row-by-row.
- **Fix:** Usar `executemany()` con batches de 5000, o `COPY FROM STDIN`.

### `ERROR: duplicate key value violates unique constraint`
- **Fix:**
  ```sql
  TRUNCATE deliveries, maintenance, trips, drivers, vehicles, routes RESTART IDENTITY CASCADE;
  ```

---

## 3. Vistas y SQL

### `relation "v_kpi_executive" does not exist`
- **Causa:** No se aplicó `dashboard/sql/01_vistas_analiticas.sql`.
- **Fix:**
  ```bash
  # PostgreSQL local
  psql -h localhost -U postgres -d fleetlogix_db -f dashboard/sql/01_vistas_analiticas.sql

  # Con Docker
  docker exec -i fleetlogix_postgres psql -U admin_dody -d fleetlogix < dashboard/sql/01_vistas_analiticas.sql
  ```

### `ERROR: transacción abortada` / `SQLSTATE 25P02`
- **Causa:** Una sentencia anterior falló dentro de una transacción `BEGIN;...COMMIT;`.
- **Fix:** `ROLLBACK;` antes de reintentar la ejecución.

### `column "departure_time" does not exist`
- **Causa:** Tabla `trips` con columnas distintas a las esperadas.
- **Fix:** Comparar con `sql/schema.sql` y reaplicar si difiere.

### Vistas vacías aunque hay datos
- **Causa:** Filtros temporales en las vistas.
- **Fix:** Verificar que las fechas en las tablas caigan dentro del rango esperado.

---

## 4. Streamlit · Arranque

### `streamlit: command not found`
- **Fix:** Activar el entorno virtual primero:
  ```powershell
  cd dashboard_streamlit
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

### `Port 8501 is already in use`
- **Fix:** `streamlit run streamlit_app.py --server.port 8502`

### `ImportError: cannot import name 'xxx' from 'utils'`
- **Causa:** Ejecutaste desde la carpeta incorrecta.
- **Fix:** Entra primero a `dashboard_streamlit/` y ejecuta `streamlit run streamlit_app.py` desde allí.

---

## 5. Streamlit · Conexión a datos

### Sidebar muestra "⚠️ ... could not connect"
- **Fix:** Verificar que PostgreSQL esté corriendo:
  ```powershell
  # Windows
  Get-Service postgresql-x64-15
  ```
- Comprobar credenciales en la raíz `.env` del proyecto.

### Tarjetas KPI muestran "—" (em-dash)
- **Causa:** Vistas aún no creadas o tablas vacías.
- **Fix:** Ejecutar `01_vistas_analiticas.sql` y refrescar con el botón "🔄 Refrescar datos" del sidebar.

### `psycopg2.ProgrammingError: relation ... does not exist`
- **Fix:** Idem que el caso anterior. Corroborar:
  ```sql
  SELECT viewname FROM pg_views WHERE schemaname='public' AND viewname LIKE 'v_%';
  ```
  Deben aparecer 8 vistas.

### Cache obsoleto
- **Fix:** Click en "🔄 Refrescar datos" del sidebar, o reiniciar Streamlit con Ctrl+C y relanzar.

---

## 6. Visualizaciones Plotly

### Gráficos no renderizan / quedan en blanco
- **Fix:**
  ```bash
  pip install --upgrade plotly
  ```
- Borrar caché del navegador (Ctrl+Shift+R en Chrome/Edge).

### Tooltips ilegibles sobre fondo oscuro
- **Fix:** Ya está configurado `hoverlabel=dict(bgcolor=...)` en `utils/styling.py`. Si sigue mal, revisar versión de Plotly.

### Slider de fechas rompe el gráfico
- **Fix:** Usa el botón "🔄 Refrescar datos" y vuelve a elegir el rango.

---

## 7. Performance

### La app va lenta
- **Causa típica:** Primera carga sin caché.
- **Fix:** Las queries están cacheadas 5 min (`@st.cache_data(ttl=300)`). A partir de la 2ª carga responde instantáneo.
- **Para tablas gigantes:** Revisar que los índices de `sql/03_optimization_indexes.sql` estén aplicados.

### "Session killed - memory limit"
- **Fix:** En `utils/db.py`, reducir el rango de datos retornados por `run_query` añadiendo `LIMIT` o agregación previa en la vista SQL.

---

## 8. Git / repositorio

### `.streamlit/secrets.toml` aparece en commits
- **Fix:** Ya está listado en `dashboard_streamlit/.gitignore`. Remover del tracking:
  ```bash
  git rm --cached dashboard_streamlit/.streamlit/secrets.toml
  ```

### `.venv/` pesa MB en el repo
- **Fix:** Agregar `.venv/` y `*.egg-info/` al `.gitignore` raíz.

---

## 📞 Soporte adicional

Si nada funciona:
1. Captura del error (pantalla completa)
2. Versión de Streamlit: `streamlit --version`
3. Versión de Python: `python --version`
4. Reportar issue en el repo del proyecto

**Email del owner del proyecto:** dodydurema67@gmail.com
