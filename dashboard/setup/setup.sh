#!/usr/bin/env bash
# ===========================================================================
# FleetLogix · Setup completo (Bash · Linux / macOS / WSL / Git-Bash)
# ===========================================================================
# Monta TODO lo necesario para alimentar el dashboard Streamlit:
#   1. Detecta PostgreSQL local (modo por defecto) o Docker (--use-docker)
#   2. Crea la base "fleetlogix_db" si no existe
#   3. Espera a que la base sea healthy
#   4. Ejecuta schema.sql (tablas)
#   5. Genera datos sintéticos (Faker · ~535k registros)
#   6. Crea la dimensión de fechas (dim_date)
#   7. Crea las 8 vistas analíticas del dashboard
#   8. Valida recuentos en cada vista
#
# CREDENCIALES POR DEFECTO (PostgreSQL LOCAL):
#   Servidor : localhost
#   Puerto   : 5432
#   Base     : fleetlogix_db
#   Usuario  : postgres
#   Password : Dody2003
#
# USO:
#   bash dashboard/setup/setup.sh                # local Postgres (default)
#   bash dashboard/setup/setup.sh --use-docker   # docker-compose
#   bash dashboard/setup/setup.sh --skip-data    # sin regenerar datos
#   bash dashboard/setup/setup.sh --force        # DROP DB y recrea
# ===========================================================================

set -euo pipefail

SKIP_DATA=0
FORCE=0
USE_DOCKER=0
PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5432}"
PG_USER="${PG_USER:-postgres}"
PG_PASS="${PG_PASS:-Dody2003}"
PG_DB="${PG_DB:-fleetlogix_db}"

for arg in "$@"; do
    case "$arg" in
        --skip-data)  SKIP_DATA=1 ;;
        --force)      FORCE=1 ;;
        --use-docker) USE_DOCKER=1 ;;
        -h|--help)    grep '^#' "$0" | sed 's/^#//'; exit 0 ;;
    esac
done

# Si va con docker, sobrescribir credenciales para que coincidan con compose
if [[ "$USE_DOCKER" -eq 1 ]]; then
    [[ "$PG_USER" == "postgres" ]]      && PG_USER="admin_dody"
    [[ "$PG_PASS" == "Dody2003" ]]      && PG_PASS="secret_password_123"
    [[ "$PG_DB"   == "fleetlogix_db" ]] && PG_DB="fleetlogix"
fi

export PGPASSWORD="$PG_PASS"

C_CYAN='\033[36m'; C_GREEN='\033[32m'; C_YELLOW='\033[33m'; C_RED='\033[31m'
C_MAG='\033[35m';  C_RESET='\033[0m'
step()  { echo -e "\n${C_CYAN}==> $*${C_RESET}"; }
ok()    { echo -e "    ${C_GREEN}[OK] $*${C_RESET}"; }
warn()  { echo -e "    ${C_YELLOW}[!!] $*${C_RESET}"; }
err()   { echo -e "    ${C_RED}[ERR] $*${C_RESET}"; }

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo ""
echo -e "${C_MAG}============================================================${C_RESET}"
echo -e "${C_MAG} FleetLogix · Setup automático de base de datos + vistas${C_RESET}"
echo -e "${C_MAG}============================================================${C_RESET}"
echo " Proyecto       : $PROJECT_ROOT"
echo " Modo           : $([[ $USE_DOCKER -eq 1 ]] && echo Docker || echo 'PostgreSQL local')"
echo " Host PostgreSQL: ${PG_HOST}:${PG_PORT}"
echo " Base           : $PG_DB"
echo " Usuario        : $PG_USER"

# ---------------------------------------------------------------------------
# Helpers SQL
# ---------------------------------------------------------------------------
exec_psql_inline() {
    local sql="$1"
    local db="${2:-$PG_DB}"
    if [[ "$USE_DOCKER" -eq 1 ]]; then
        docker exec -i -e PGPASSWORD="$PG_PASS" fleetlogix_postgres \
            psql -U "$PG_USER" -d "$db" -t -A -c "$sql"
    else
        psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$db" -t -A -c "$sql"
    fi
}

exec_psql_file() {
    local rel="$1"
    local full="$PROJECT_ROOT/$rel"
    if [[ ! -f "$full" ]]; then warn "Archivo SQL no encontrado: $rel"; return; fi
    echo -e "    Ejecutando $rel ..."
    if [[ "$USE_DOCKER" -eq 1 ]]; then
        docker exec -i -e PGPASSWORD="$PG_PASS" fleetlogix_postgres \
            psql -U "$PG_USER" -d "$PG_DB" -q -v ON_ERROR_STOP=1 < "$full" >/dev/null \
            && ok "Aplicado $rel" || warn "Advertencias al ejecutar $rel"
    else
        psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" \
            -q -v ON_ERROR_STOP=1 -f "$full" >/dev/null \
            && ok "Aplicado $rel" || warn "Advertencias al ejecutar $rel"
    fi
}

# ---------------------------------------------------------------------------
# 1. Prerequisitos
# ---------------------------------------------------------------------------
step "1/8 · Verificando prerequisitos"

if [[ "$USE_DOCKER" -eq 1 ]]; then
    command -v docker >/dev/null || { err "Docker no instalado"; exit 1; }
    docker info >/dev/null 2>&1 || { err "Docker daemon no activo"; exit 1; }
    ok "Docker disponible y activo"
else
    command -v psql >/dev/null || { err "psql no está en PATH (necesitas PostgreSQL client)"; exit 1; }
    ok "psql disponible"
fi

if command -v python3 >/dev/null; then PY=python3
elif command -v python >/dev/null; then PY=python
else PY=""; warn "Python no encontrado - se omitirá la generación de datos"
fi
[[ -n "$PY" ]] && ok "Python disponible ($PY)"

# ---------------------------------------------------------------------------
# 2. Servicio PostgreSQL
# ---------------------------------------------------------------------------
step "2/8 · Preparando servicio PostgreSQL"

if [[ "$USE_DOCKER" -eq 1 ]]; then
    cd "$PROJECT_ROOT"
    if [[ "$FORCE" -eq 1 ]]; then
        warn "Modo --force: eliminando volúmenes previos"
        docker compose down -v >/dev/null 2>&1 || true
    fi
    docker compose up -d >/dev/null
    ok "docker compose up -d ejecutado"
else
    ok "Usando PostgreSQL local en ${PG_HOST}:${PG_PORT}"
fi

# ---------------------------------------------------------------------------
# 3. Esperar healthy + crear DB si no existe
# ---------------------------------------------------------------------------
step "3/8 · Esperando a PostgreSQL (max 60s) y validando base $PG_DB"

READY=0
for i in $(seq 1 30); do
    sleep 2
    if [[ "$USE_DOCKER" -eq 1 ]]; then
        docker exec fleetlogix_postgres pg_isready -U "$PG_USER" >/dev/null 2>&1 && { READY=1; break; }
    else
        psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "postgres" -c "SELECT 1" >/dev/null 2>&1 && { READY=1; break; }
    fi
done
[[ "$READY" -eq 1 ]] && ok "PostgreSQL responde" || { err "PostgreSQL no respondió en 60s"; exit 1; }

if [[ "$FORCE" -eq 1 ]]; then
    warn "Modo --force: drop database $PG_DB"
    exec_psql_inline "DROP DATABASE IF EXISTS $PG_DB;" "postgres" >/dev/null
fi
EXISTS=$(exec_psql_inline "SELECT 1 FROM pg_database WHERE datname='$PG_DB';" "postgres" | tr -d '[:space:]')
if [[ "$EXISTS" != "1" ]]; then
    echo "    Creando base $PG_DB ..."
    exec_psql_inline "CREATE DATABASE $PG_DB;" "postgres" >/dev/null
    ok "Base $PG_DB creada"
else
    ok "Base $PG_DB ya existe"
fi

# ---------------------------------------------------------------------------
# 4. Schema
# ---------------------------------------------------------------------------
step "4/8 · Aplicando schema.sql (tablas y constraints)"
exec_psql_file "sql/schema.sql"

# ---------------------------------------------------------------------------
# 5. Datos sintéticos
# ---------------------------------------------------------------------------
step "5/8 · Generando datos sintéticos"
if [[ "$SKIP_DATA" -eq 1 ]]; then
    warn "Flag --skip-data activo, se omite."
else
    COUNT=$(exec_psql_inline "SELECT COUNT(*) FROM vehicles" 2>/dev/null | tr -d '[:space:]')
    if [[ "$COUNT" =~ ^[0-9]+$ && "$COUNT" -gt 0 ]]; then
        warn "Ya hay $COUNT vehículos en la BD. Se omite. Usa --force para resetear."
    else
        SCRIPT="$PROJECT_ROOT/scripts/01_data_generation.py"
        if [[ -f "$SCRIPT" && -n "$PY" ]]; then
            echo "    Lanzando scripts/01_data_generation.py (puede tardar 2-5 min)..."
            (cd "$PROJECT_ROOT" && \
                DB_HOST="$PG_HOST" DB_PORT="$PG_PORT" DB_NAME="$PG_DB" \
                DB_USER="$PG_USER" DB_PASSWORD="$PG_PASS" \
                "$PY" "$SCRIPT") && ok "Datos sintéticos insertados" || warn "El script terminó con advertencias"
        else
            warn "No se ejecuta el script de generación (faltan archivo o python)"
        fi
    fi
fi

# ---------------------------------------------------------------------------
# 6. dim_date
# ---------------------------------------------------------------------------
step "6/8 · Creando dimensión de fechas (dim_date)"
exec_psql_file "dashboard/sql/03_dim_date.sql"

# ---------------------------------------------------------------------------
# 7. Vistas
# ---------------------------------------------------------------------------
step "7/8 · Creando vistas analíticas para Streamlit"
exec_psql_file "dashboard/sql/01_vistas_analiticas.sql"

# ---------------------------------------------------------------------------
# 8. Validación
# ---------------------------------------------------------------------------
step "8/8 · Validando objetos creados"

OBJECTS=(
    vehicles drivers routes trips deliveries maintenance dim_date
    v_kpi_executive v_deliveries_timeseries v_vehicle_performance
    v_driver_performance v_route_traffic v_maintenance_alerts
    v_fuel_efficiency v_dim_date
)

echo ""
printf "    %-35s %10s\n" "TABLA / VISTA" "FILAS"
printf "    %-35s %10s\n" "-----------------------------------" "----------"
for obj in "${OBJECTS[@]}"; do
    n=$(exec_psql_inline "SELECT COUNT(*) FROM $obj" 2>/dev/null | tr -d '[:space:]')
    printf "    %-35s %10s\n" "$obj" "${n:-N/A}"
done

# ---------------------------------------------------------------------------
# Resumen final
# ---------------------------------------------------------------------------
echo ""
echo -e "${C_GREEN}============================================================${C_RESET}"
echo -e "${C_GREEN} SETUP COMPLETO${C_RESET}"
echo -e "${C_GREEN}============================================================${C_RESET}"
echo ""
echo -e "${C_CYAN} Siguientes pasos para lanzar el dashboard Streamlit:${C_RESET}"
echo "  1. cd dashboard_streamlit"
echo "  2. python -m venv .venv && source .venv/bin/activate"
echo "  3. pip install -r requirements.txt"
echo "  4. streamlit run streamlit_app.py"
echo ""
echo -e "${C_CYAN} Credenciales PostgreSQL utilizadas:${C_RESET}"
echo "       Servidor : $PG_HOST"
echo "       Base     : $PG_DB"
echo "       Usuario  : $PG_USER"
echo "       Password : $PG_PASS"
echo ""
echo " Navega a http://localhost:8501 y explora las 5 páginas."
echo ""
