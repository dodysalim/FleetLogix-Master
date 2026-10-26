# 🛠️ Guía de Instalación y Despliegue
## FleetLogix Master — Setup Completo en 10 Minutos

---

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Snowflake](https://img.shields.io/badge/Snowflake-Cloud-brightgreen?logo=snowflake)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

**Tiempo estimado:** 10–15 minutos (con Docker)  
**Dificultad:** Intermedia  
**Entornos soportados:** macOS, Linux, Windows (WSL2)

---

## 📋 Tabla Rápida de Contenidos

1. [Prerrequisitos](#1-prerrequisitos)
2. [Configuración Inicial](#2-configuración-inicial)
3. [Despliegue con Docker](#3-despliegue-con-docker-compose)
4. [Generación de Datos](#4-generación-de-datos-sintéticos)
5. [Verificación](#5-verificación-final)
6. [Solución de Problemas](#6-troubleshooting)

---

## 1. Prerrequisitos

### 1.1 Software Mínimo Requerido

```bash
# Verificar versiones instaladas
python --version       # ≥ 3.11
docker --version       # ≥ 24.0
docker compose version # ≥ 2.0
git --version          # ≥ 2.30
```

**Si falta algo:**
- [Python 3.11+](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/downloads/)

### 1.2 Recursos de Sistema

| Recurso | Mínimo | Recomendado | Libre Recomendado |
|---------|--------|-------------|------------------|
| **RAM** | 8 GB | 16 GB | ≥ 4 GB libres |
| **CPU** | 4 núcleos | 8 núcleos | ≥ 2 núcleos libres |
| **Disco** | 20 GB SSD | 50 GB SSD | ≥ 10 GB libres |
| **Red** | Estable | Banda ancha | — |

> **💡 Sugerencia:** Cerrar VS Code, navegadores y otras apps pesadas durante instalación.

---

## 2. Configuración Inicial

### Paso 2.1 — Clonar Repositorio

```bash
# 1. Clonar proyecto
git clone https://github.com/dodyduenas/fleetlogix-master.git

# 2. Entrar al directorio
cd fleetlogix-master

# 3. Verificar estructura
tree -L 2 -I 'node_modules|.git'  # Linux/Mac
# o
dir /S /B | findstr /V "node_modules .git"  # Windows
```

### Paso 2.2 — Variables de Entorno

```bash
# 1. Copiar ejemplo
cp .env.example .env

# 2. Editar con editor
code .env        # VS Code
# o
nano .env        # Terminal
```

**Configuración mínima:**
```bash
# PostgreSQL —valores por defecto (no cambiar)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fleetlogix
POSTGRES_USER=admin_dody
POSTGRES_PASSWORD=ChangeMe_2026!  # ← CAMBIAR ESTO

# JWT para API
PGRST_JWT_SECRET=un_secreto_muy_largo_y_seguro_de_32_caracteres_aqui_minimo

# (Opcional) Snowflake —para producción
# SNOWFLAKE_ACCOUNT=tcucrelq-xxxx
# SNOWFLAKE_USER=dody_duenas
# SNOWFLAKE_PASSWORD=xxxxx
# SNOWFLAKE_WAREHOUSE=COMPUTE_WH
# SNOWFLAKE_DATABASE=FLEETLOGIX_DW
# SNOWFLAKE_SCHEMA=ANALYTICS

# (Opcional) AWS —para Lambda local
# AWS_ACCESS_KEY_ID=xxxxx
# AWS_SECRET_ACCESS_KEY=xxxxx
# AWS_REGION=us-east-1
```

> **🔒 Seguridad:**  
> - `.env` **nunca** se sube a Git (está en `.gitignore`)  
> - En producción usar **AWS Secrets Manager** o **HashiCorp Vault**

---

## 3. Despliegue con Docker Compose

### Paso 3.1 — Levantar Infraestructura

```bash
# 1. Verificar que Docker esté corriendo
docker ps

# 2. Levantar todos los servicios
docker compose up -d

# 3. Verificar estado
docker compose ps
```

**Esperado output:**
```
NAME                      IMAGE                 STATE           PORTS
postgres_fleetlogix       postgres:15-alpine    Up (healthy)    0.0.0.0:5432->5432/tcp
postgrest_api            postgrest/postgrest   Up (healthy)    0.0.0.0:3000->3000/tcp
streamlit_dashboard      streamlit-base        Up              0.0.0.0:8501->8501/tcp
pgadmin                  dpage/pgadmin4        Up              0.0.0.0:5050->80/tcp
```

### Paso 3.2 — Salud de Servicios

```bash
# 1. PostgreSQL
docker compose exec postgres pg_isready -U admin_dody
# Output: /var/run/postgresql:5432 - accepting connections

# 2. API PostgREST
curl -s http://localhost:3000/ | jq '.'
# Output: {"image":"postgrest/postgrest",...}

# 3. Streamlit Dashboard
curl -s http://localhost:8501 | grep -o '<title>[^<]*</title>'
# Output: <title>FleetLogix Analytics</title>
```

**Accesos locales:**
| Servicio | URL | Credenciales |
|----------|-----|-------------|
| PostgreSQL | `localhost:5432` | admin_dody / ChangeMe_2026! |
| PostgREST API | `http://localhost:3000` | Sin auth (anon) |
| Streamlit Dashboard | `http://localhost:8501` | Sin auth |
| pgAdmin | `http://localhost:5050` | admin@fleetlogix.com / admin |

---

## 4. Generación de Datos Sintéticos

### Paso 4.1 — Crear Dataset Completo

```bash
# Navegar a scripts
cd scripts

# Generar 500,000+ registros realistas
python generate_synthetic_data.py --records 500000 --output ../data/ --seed 42
```

**Progreso esperado:**
```
[INFO] Iniciando generador de datos sintéticos...
[INFO] Generando vehículos (200 registros)... ✅
[INFO] Generando conductores (400 registros)... ✅
[INFO] Generando rutas (50 registros)... ✅
[INFO] Generando viajes (100,000 registros)... ✅
[INFO] Generando entregas (400,000 registros)... ✅
[INFO] Generando mantenimientos (5,000 registros)... ✅
[INFO] Total: 505,650 registros generados en 124.5s
```

### Paso 4.2 — Cargar a PostgreSQL

```bash
# Método automático (recomendado)
python load_to_postgres.py --file data/fleetlogix_full_2026-04-18.csv

# Método manual (si falla)
psql -U admin_dody -d fleetlogix -c "\copy vehicles FROM 'data/vehicles.csv' CSV HEADER"
psql -U admin_dody -d fleetlogix -c "\copy drivers FROM 'data/drivers.csv' CSV HEADER"
psql -U admin_dody -d fleetlogix -c "\copy routes FROM 'data/routes.csv' CSV HEADER"
psql -U admin_dody -d fleetlogix -c "\copy trips FROM 'data/trips.csv' CSV HEADER"
psql -U admin_doby -d fleetlogix -c "\copy deliveries FROM 'data/deliveries.csv' CSV HEADER"
```

### Paso 4.3 — Verificar Carga

```bash
# Conectarse a base de datos
psql -U admin_dody -d fleetlogix

# Ejecutar query de verificación
SELECT 
    'vehicles'   as tabla, COUNT(*) as registros FROM vehicles
UNION ALL
SELECT 'drivers',    COUNT(*) FROM drivers
UNION ALL
SELECT 'routes',     COUNT(*) FROM routes
UNION ALL
SELECT 'trips',      COUNT(*) FROM trips
UNION ALL
SELECT 'deliveries', COUNT(*) FROM deliveries
UNION ALL
SELECT 'maintenance',COUNT(*) FROM maintenance
ORDER BY registros DESC;
```

**Esperado:**
```
 tabla     | registros
-----------+-----------
 deliveries |   400000
 trips      |   100000
 vehicles   |      200
 drivers    |      400
 routes     |       50
 maintenance|     5000
(6 rows)
```

---

## 5. Verificación Final

### 5.1 Test de Integración Completo

```bash
#!/bin/bash
# save as: test_integration.sh
# run: bash test_integration.sh

echo "=== FLEETLOGIX INTEGRATION TEST ==="
echo ""

# Test 1: PostgreSQL connection
echo "1. Testing PostgreSQL connection..."
psql -U admin_dody -d fleetlogix -c "SELECT '✅ PostgreSQL OK' as status;" 2>/dev/null || echo "❌ PostgreSQL FAIL"

# Test 2: API response
echo ""
echo "2. Testing PostgREST API..."
curl -s http://localhost:3000/vehicles?limit=1 | jq -e '. | length > 0' && echo "✅ API OK" || echo "❌ API FAIL"

# Test 3: Dashboard
echo ""
echo "3. Testing Streamlit Dashboard..."
curl -s http://localhost:8501 | grep -q "Streamlit" && echo "✅ Dashboard OK" || echo "❌ Dashboard FAIL"

# Test 4: Data integrity
echo ""
echo "4. Testing data integrity..."
result=$(psql -U admin_dody -d fleetlogix -t -c "SELECT COUNT(*) FROM deliveries WHERE delivery_status = 'delivered';")
if [ "$result" -gt 100000 ]; then
    echo "✅ Data integrity OK ($result delivered)"
else
    echo "❌ Data integrity FAIL"
fi

# Test 5: Analytics query
echo ""
echo "5. Testing analytical query..."
psql -U admin_dody -d fleetlogix -c "
SELECT ROUND(AVG(delay_minutes), 2) as avg_delay_min
FROM fact_deliveries
WHERE delivery_status = 'delivered';
" 2>/dev/null | tail -n 2 | head -n 1

echo ""
echo "=== ALL TESTS COMPLETE ==="
```

### 5.2 Métricas de Rendimiento

| Métrica | Esperado | Cómo Verificar |
|---------|----------|----------------|
| **Tiempo startup Docker** | < 30s | `time docker compose up -d` |
| **Psql connection** | < 1s | `time psql -c "SELECT 1"` |
| **API latency** | < 100ms | `curl -w '%{time_total}' -o /dev/null http://localhost:3000/vehicles` |
| **Dashboard load** | < 2s | Abrir Chrome DevTools → Network |

### 5.3 Checklist Quick

```markdown
- [ ] Docker Desktop corriendo
- [ ] `docker compose up -d` completado sin errores
- [ ] `psql -c "SELECT COUNT(*) FROM vehicles"` devuelve ≥ 200
- [ ] `curl http://localhost:3000/vehicles` retorna JSON válido
- [ ] Dashboard en http://localhost:8501 se ve correctamente
- [ ] No hay errores en `docker compose logs` (solo warnings)
```

---

## 6. Troubleshooting

### Problema 1 — `docker compose up` falla

```bash
# Diagnóstico
docker compose config  # Validar YAML syntax
docker version        # Verificar Docker Engine
docker info           # Verificar resources

# Solución común: reiniciar Docker Desktop
# En Windows: clic derecho托盘 icon → Restart

# Si persiste: aumentar memoria
# Docker Desktop → Settings → Resources → Memory: 8 GB+
```

### Problema 2 — Puerto 5432 ocupado

```bash
# Linux/Mac: encontrar proceso
sudo lsof -i :5432
sudo kill -9 <PID>

# Windows PowerShell:
netstat -ano | findstr :5432
taskkill /PID <PID> /F

# O cambiar puerto en docker-compose.yml:
# postgres:
#   ports:
#     - "5433:5432"  # ← Cambiar a puerto libre
```

### Problema 3 — `FATAL: password authentication failed`

```bash
# Causa: contraseña .env ≠ contraseña BD

# Solución 1: Resetear contraseña PostgreSQL
docker compose exec postgres psql -U postgres -c "ALTER USER admin_dody PASSWORD 'ChangeMe_2026!';"

# Solución 2: Recrear contenedor (PERDE DATOS)
docker compose down -v  # ⚠️ Borra volúmenes
docker compose up -d
```

### Problema 4 — Error memoria al generar datos

```bash
# Reducir batch size
python generate_synthetic_data.py --records 500000 --chunk-size 50000

# O aumentar swap en Docker
# Docker Desktop → Settings → Resources → Swap: 2 GB
```

### Problema 5 — Dashboard en blanco

```bash
# Ver logs Streamlit
docker compose logs streamlit --tail 50

# Si: "Session manager failed to start"
# Solución: limpiar cache de Streamlit
docker compose exec streamlit rm -rf ~/.streamlit/

# Si: "ModuleNotFoundError"
# Solución: reconstruir imagen
docker compose build --no-cache streamlit
docker compose up -d streamlit
```

---

## 🚀 Despliegue en Producción

### Opción 1 — AWS (Recomendado)

```bash
# 1. Snowflake
snowsql -a tcucrelq-kb28178 -d FLEETLOGIX_DW -s ANALYTICS -f sql/snowflake_schema.sql

# 2. ETL
python scripts/etl_to_snowflake.py --env production

# 3. Lambda
cd lambda_functions
sam build && sam deploy --config-env production --region us-east-1

# 4. API en EC2
# Ver: docs/DEPLOY_PRODUCTION.md
```

### Opción 2 — Railway/Render

```bash
# Railway
railway login
railway link
railway up

# Configurar variables en dashboard Railway
```

---

## 📁 Estructura Final

```
fleetlogix-master/
├── 📂 scripts/                    # ✅ Generadores + ETL
│   ├── generate_synthetic_data.py # ← 500K+ registros
│   ├── load_to_postgres.py        # ← Cargar a PG
│   └── etl_to_snowflake.py        # ← Opcional: Snowflake
├── 📂 data/                       # ✅ Datos generados
│   ├── vehicles.csv
│   ├── drivers.csv
│   ├── routes.csv
│   ├── trips.csv
│   └── deliveries.csv
├── 📂 docker/                     # ✅ Contenedores
├── 📂 dashboard/                  # ✅ Streamlit app
├── 📂 docs/                       # ✅ Documentación
├── 📄 docker-compose.yml          # ✅ Orquestación
├── 📄 .env                        # ✅ Configurado
└── ✅ Sistema listo para usar
```

---

## 🎯 Próximos Pasos

1. **Abrir Dashboard:** http://localhost:8501
2. **Probar API:** `curl http://localhost:3000/vehicles | jq .`
3. **Ejecutar query SQL:** Ver [Manual de Consultas](../docs/manual_consultas_sql.md)
4. **Leer arquitectura:** Ver [Documentación Técnica](../docs/PI_M2_DOCUMENTATION_DODY.md)
5. **Desplegar en cloud:** Seguir [Guía AWS](arquitectura_tecnica.md)

---

## 📚 Documentación Relacionada

| Tema | Documento |
|------|-----------|
| Arquitectura técnica | [PI_M2_DOCUMENTATION_DODY.md](PI_M2_DOCUMENTATION_DODY.md) |
| Modelo de datos | [MODELO_DATOS.md](../dashboard/MODELO_DATOS.md) |
| KPIs | [KPIs.md](../dashboard/KPIs.md) |
| SQL Queries | [manual_consultas_sql.md](manual_consultas_sql.md) |
| AWS Setup | [aws_local_simulation.md](aws_local_simulation.md) |

---

**🔗 Enlaces Útiles:**
- 🐙 [Repositorio GitHub](https://github.com/dodyduenas/fleetlogix-master)
- 📖 [Documentación Principal](../docs/INDEX.md)
- 🐛 [Reportar Bug](https://github.com/dodyduenas/fleetlogix-master/issues)

---

*Guía validada en: macOS Sonoma 14, Ubuntu 22.04 LTS, Windows 11 (WSL2)*  
*Última actualización: Abril 2026*

---

⬅️ [Volver al Índice de Docs](../docs/INDEX.md)  
⬇️ [Documentación Técnica Completa →](PI_M2_DOCUMENTATION_DODY.md)
