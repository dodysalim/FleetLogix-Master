# ===========================================================================
# FleetLogix · Setup completo (PowerShell · Windows)
# ===========================================================================
# Monta TODO lo necesario para alimentar el dashboard Streamlit:
#   1. Detecta PostgreSQL local (modo por defecto) o Docker (-UseDocker)
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
#   Password : your_password   (usa $env:PGPASSWORD para override)
#
# USO:
#   cd C:\Users\DODY DUEÑAS\Documents\Poryecto2Henry\Proyecto2Dody
#   PowerShell -ExecutionPolicy Bypass -File .\dashboard\setup\setup.ps1
# ===========================================================================

param(
    [switch]$SkipData,        # No regenera datos sintéticos
    [switch]$Force,           # DROP DATABASE y recrea desde cero
    [switch]$UseDocker,       # Levanta docker-compose en lugar de usar postgres local
    [string]$PgHost     = "localhost",
    [int]   $PgPort     = 5432,
    [string]$PgUser     = "postgres",
    [string]$PgPass     = "your_password",
    [string]$PgDb       = "fleetlogix_db"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# -- Override credenciales si va con Docker (compose usa otro user/db) --
if ($UseDocker) {
    if ($PgUser -eq "postgres") { $PgUser = "admin_dody" }
    if ($PgPass -eq "your_password") { $PgPass = "secret_password_123" }
    if ($PgDb   -eq "fleetlogix_db") { $PgDb = "fleetlogix" }
}

# -- Exportar PGPASSWORD para que psql no lo pida interactivo --
$env:PGPASSWORD = $PgPass

function Write-Step([string]$Msg) { Write-Host ""; Write-Host "==> $Msg" -ForegroundColor Cyan }
function Write-Ok([string]$Msg)   { Write-Host "    [OK] $Msg" -ForegroundColor Green }
function Write-Warn([string]$Msg) { Write-Host "    [!!] $Msg" -ForegroundColor Yellow }
function Write-Err([string]$Msg)  { Write-Host "    [ERR] $Msg" -ForegroundColor Red }

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host " FleetLogix · Setup automatico de base de datos + vistas" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host " Proyecto       : $ProjectRoot"
Write-Host " Modo           : $(if ($UseDocker) {'Docker'} else {'PostgreSQL local'})"
Write-Host " Host PostgreSQL: ${PgHost}:${PgPort}"
Write-Host " Base           : $PgDb"
Write-Host " Usuario        : $PgUser"

# ---------------------------------------------------------------------------
# Helpers SQL (admite tanto psql local como docker exec)
# ---------------------------------------------------------------------------
function Invoke-Psql([string]$ExtraArgs, [string]$DbOverride = $null) {
    $db = if ($DbOverride) { $DbOverride } else { $PgDb }
    if ($UseDocker) {
        $cmd = "docker exec -i -e PGPASSWORD=$PgPass fleetlogix_postgres psql -U $PgUser -d $db $ExtraArgs"
    } else {
        $cmd = "psql -h $PgHost -p $PgPort -U $PgUser -d $db $ExtraArgs"
    }
    return $cmd
}

function Exec-SqlFile([string]$RelPath) {
    $full = Join-Path $ProjectRoot $RelPath
    if (-not (Test-Path $full)) { Write-Warn "Archivo SQL no encontrado: $RelPath"; return }
    Write-Host "    Ejecutando $RelPath ..." -ForegroundColor Gray
    if ($UseDocker) {
        Get-Content $full -Raw | docker exec -i -e PGPASSWORD=$PgPass fleetlogix_postgres `
            psql -U $PgUser -d $PgDb -q -v ON_ERROR_STOP=1 2>&1 | Out-Null
    } else {
        psql -h $PgHost -p $PgPort -U $PgUser -d $PgDb -q -v ON_ERROR_STOP=1 -f $full 2>&1 | Out-Null
    }
    if ($LASTEXITCODE -ne 0) { Write-Warn "Advertencias al ejecutar $RelPath (exit=$LASTEXITCODE)" }
    else                     { Write-Ok  "Aplicado $RelPath" }
}

function Exec-SqlInline([string]$Sql, [string]$DbOverride = $null) {
    $db = if ($DbOverride) { $DbOverride } else { $PgDb }
    if ($UseDocker) {
        $result = $Sql | docker exec -i -e PGPASSWORD=$PgPass fleetlogix_postgres `
            psql -U $PgUser -d $db -t -A 2>&1
    } else {
        $result = psql -h $PgHost -p $PgPort -U $PgUser -d $db -t -A -c $Sql 2>&1
    }
    return $result
}

# ---------------------------------------------------------------------------
# 1. Verifica prerequisitos
# ---------------------------------------------------------------------------
Write-Step "1/8 · Verificando prerequisitos"

if ($UseDocker) {
    try   { docker --version | Out-Null; Write-Ok "Docker disponible" }
    catch { Write-Err "Docker no esta instalado o no se encuentra en PATH"; exit 1 }
    try   { docker info | Out-Null; Write-Ok "Docker Desktop corriendo" }
    catch { Write-Err "Docker Desktop no esta corriendo. Abrelo y vuelve a intentar."; exit 1 }
} else {
    try   { psql --version | Out-Null; Write-Ok "psql disponible" }
    catch { Write-Err "psql no esta en PATH. Instala PostgreSQL o agrega C:\Program Files\PostgreSQL\<ver>\bin al PATH"; exit 1 }
}

try   { python --version | Out-Null; Write-Ok "Python disponible" }
catch { Write-Warn "Python no se encontro - el paso de generacion de datos se omitira" }

# ---------------------------------------------------------------------------
# 2. Levantar contenedores (solo si -UseDocker) o validar postgres local
# ---------------------------------------------------------------------------
Write-Step "2/8 · Preparando servicio PostgreSQL"

if ($UseDocker) {
    Push-Location $ProjectRoot
    try {
        if ($Force) {
            Write-Warn "Modo -Force: eliminando volumenes previos"
            docker compose down -v 2>&1 | Out-Null
        }
        docker compose up -d 2>&1 | Out-Null
        Write-Ok "docker compose up -d ejecutado"
    } finally { Pop-Location }
} else {
    Write-Ok "Usando PostgreSQL local en ${PgHost}:${PgPort}"
}

# ---------------------------------------------------------------------------
# 3. Esperar a que PostgreSQL este healthy + crear DB si no existe
# ---------------------------------------------------------------------------
Write-Step "3/8 · Esperando a PostgreSQL (max 60s) y validando base $PgDb"

$ready = $false
for ($i = 1; $i -le 30; $i++) {
    Start-Sleep -Seconds 2
    if ($UseDocker) {
        docker exec fleetlogix_postgres pg_isready -U $PgUser 2>&1 | Out-Null
    } else {
        $env:PGPASSWORD = $PgPass
        psql -h $PgHost -p $PgPort -U $PgUser -d "postgres" -c "SELECT 1" 2>&1 | Out-Null
    }
    if ($LASTEXITCODE -eq 0) { $ready = $true; Write-Ok "PostgreSQL responde (intento $i)"; break }
}
if (-not $ready) { Write-Err "PostgreSQL no respondio en 60s"; exit 1 }

# Crear la base si no existe (conectado a postgres)
if ($Force) {
    Write-Warn "Modo -Force: drop database $PgDb"
    Exec-SqlInline "DROP DATABASE IF EXISTS $PgDb;" "postgres" | Out-Null
}
$exists = Exec-SqlInline "SELECT 1 FROM pg_database WHERE datname='$PgDb';" "postgres"
if ([string]::IsNullOrWhiteSpace($exists) -or $exists.Trim() -ne "1") {
    Write-Host "    Creando base $PgDb ..." -ForegroundColor Gray
    Exec-SqlInline "CREATE DATABASE $PgDb;" "postgres" | Out-Null
    Write-Ok "Base $PgDb creada"
} else {
    Write-Ok "Base $PgDb ya existe"
}

# ---------------------------------------------------------------------------
# 4. Schema principal
# ---------------------------------------------------------------------------
Write-Step "4/8 · Aplicando schema.sql (tablas y constraints)"
Exec-SqlFile "sql\schema.sql"

# ---------------------------------------------------------------------------
# 5. Generacion de datos sinteticos
# ---------------------------------------------------------------------------
Write-Step "5/8 · Generando datos sinteticos"
if ($SkipData) {
    Write-Warn "Parametro -SkipData activo, se omite."
} else {
    $count = (Exec-SqlInline "SELECT COUNT(*) FROM vehicles").Trim()
    if ($count -match "^\d+$" -and [int]$count -gt 0) {
        Write-Warn "Ya hay $count vehiculos en la BD. Se omite generacion. Usa -Force para resetear."
    } else {
        $script = Join-Path $ProjectRoot "scripts\01_data_generation.py"
        if (Test-Path $script) {
            Write-Host "    Lanzando scripts\01_data_generation.py (puede tardar 2-5 min)..." -ForegroundColor Gray
            Push-Location $ProjectRoot
            try {
                $env:DB_HOST     = $PgHost
                $env:DB_PORT     = $PgPort
                $env:DB_NAME     = $PgDb
                $env:DB_USER     = $PgUser
                $env:DB_PASSWORD = $PgPass
                python $script
                if ($LASTEXITCODE -eq 0) { Write-Ok "Datos sinteticos insertados" }
                else                     { Write-Warn "El script retorno codigo $LASTEXITCODE" }
            } finally { Pop-Location }
        } else {
            Write-Warn "No se encontro scripts\01_data_generation.py - omitiendo"
        }
    }
}

# ---------------------------------------------------------------------------
# 6. dim_date
# ---------------------------------------------------------------------------
Write-Step "6/8 · Creando dimension de fechas (dim_date)"
Exec-SqlFile "dashboard\sql\03_dim_date.sql"

# ---------------------------------------------------------------------------
# 7. Vistas analiticas
# ---------------------------------------------------------------------------
Write-Step "7/8 · Creando vistas analiticas para Streamlit"
Exec-SqlFile "dashboard\sql\01_vistas_analiticas.sql"

# ---------------------------------------------------------------------------
# 8. Validacion
# ---------------------------------------------------------------------------
Write-Step "8/8 · Validando objetos creados"

$objects = @(
    "vehicles","drivers","routes","trips","deliveries","maintenance","dim_date",
    "v_kpi_executive","v_deliveries_timeseries","v_vehicle_performance",
    "v_driver_performance","v_route_traffic","v_maintenance_alerts",
    "v_fuel_efficiency","v_dim_date"
)

Write-Host ""
Write-Host "    TABLA / VISTA                       FILAS" -ForegroundColor White
Write-Host "    --------------------------------- ----------" -ForegroundColor White
foreach ($t in $objects) {
    $c = (Exec-SqlInline "SELECT COUNT(*) FROM $t").Trim()
    "{0,-35} {1,10}" -f $t, $c | Write-Host
}

# ---------------------------------------------------------------------------
# Resumen final
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " SETUP COMPLETO" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host " Siguientes pasos para lanzar el dashboard Streamlit:" -ForegroundColor Cyan
Write-Host "  1. cd dashboard_streamlit"
Write-Host "  2. python -m venv .venv && .\.venv\Scripts\Activate.ps1"
Write-Host "  3. pip install -r requirements.txt"
Write-Host "  4. streamlit run streamlit_app.py"
Write-Host ""
Write-Host " Credenciales PostgreSQL utilizadas (se leen desde .env):" -ForegroundColor Cyan
Write-Host "       Servidor : $PgHost"
Write-Host "       Base     : $PgDb"
Write-Host "       Usuario  : $PgUser"
Write-Host "       Password : $PgPass"
Write-Host ""
Write-Host " Navega a http://localhost:8501 y explora las 5 paginas."
Write-Host ""
