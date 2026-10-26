"""
====================================================================
FleetLogix · Quick Fix
====================================================================
Ejecuta los SQL que faltan (dim_date + 8 vistas) contra tu PostgreSQL local
para que el dashboard pueda cargar sin errores.

Se puede correr desde CUALQUIER carpeta del proyecto.
Detecta automáticamente la raíz buscando los archivos SQL.

USO:
    python dashboard/setup/quick_fix.py
    # o
    python quick_fix.py
====================================================================
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("✘ Falta psycopg2. Instalalo con:  pip install psycopg2-binary")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
DSN = dict(
    host     = os.getenv("PG_HOST", "localhost"),
    port     = int(os.getenv("PG_PORT", 5432)),
    user     = os.getenv("PG_USER", "postgres"),
    password = os.getenv("PG_PASS", "your_password"),
    dbname   = os.getenv("PG_DB",   "fleetlogix_db"),
)

SQL_FILES = [
    ("dim_date",                "dashboard/sql/03_dim_date.sql"),
    ("vistas analíticas (v_*)", "dashboard/sql/01_vistas_analiticas.sql"),
]

# ---------------------------------------------------------------------------
# Localizar raíz del proyecto
# ---------------------------------------------------------------------------
def find_project_root() -> Path:
    """Busca hacia arriba hasta encontrar 'dashboard/sql/03_dim_date.sql'."""
    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "dashboard" / "sql" / "03_dim_date.sql").exists():
            return candidate
    # Fallback: ubicación de este script
    here = Path(__file__).resolve().parent
    if (here.parent.parent / "dashboard" / "sql" / "03_dim_date.sql").exists():
        return here.parent.parent
    raise FileNotFoundError(
        "No encontré la raíz del proyecto. Ejecuta este script desde dentro de Proyecto2Dody/"
    )

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    print()
    print("=" * 60)
    print(" FleetLogix · Quick Fix (dim_date + 8 vistas)")
    print("=" * 60)

    root = find_project_root()
    print(f" Raíz del proyecto : {root}")
    print(f" PostgreSQL        : {DSN['host']}:{DSN['port']}")
    print(f" Base              : {DSN['dbname']}")
    print(f" Usuario           : {DSN['user']}")
    print()

    try:
        conn = psycopg2.connect(**DSN)
    except psycopg2.OperationalError as exc:
        print(f"✘ No se pudo conectar a PostgreSQL:\n  {exc}")
        print("\n  Verifica:")
        print("  • PostgreSQL está corriendo (services.msc → postgresql-x64-*)")
        print("  • La base 'fleetlogix_db' existe (créala desde pgAdmin si no)")
        print("  • Las credenciales son correctas (postgres / your_password)")
        return 2

    conn.autocommit = True
    cur = conn.cursor()

    ok_count = 0
    for label, rel in SQL_FILES:
        sql_path = root / rel
        if not sql_path.exists():
            print(f"✘ No encontré {rel}")
            continue
        print(f"→ Ejecutando {rel} ({label}) ...", end=" ", flush=True)
        try:
            cur.execute(sql_path.read_text(encoding="utf-8"))
            print("✔ OK")
            ok_count += 1
        except psycopg2.Error as exc:
            print(f"✘ ERROR")
            print(f"   {exc}")

    # --- Validación ---
    print()
    print("Validando objetos creados ...")
    print(f"{'OBJETO':35s} {'FILAS':>10s}")
    print("-" * 46)
    targets = [
        "dim_date",
        "v_kpi_executive", "v_deliveries_timeseries", "v_vehicle_performance",
        "v_driver_performance", "v_route_traffic", "v_maintenance_alerts",
        "v_fuel_efficiency", "v_dim_date",
    ]
    missing = []
    for t in targets:
        try:
            cur.execute(f'SELECT COUNT(*) FROM "{t}"')
            n = cur.fetchone()[0]
            print(f"{t:35s} {n:>10,}")
        except psycopg2.Error:
            print(f"{t:35s} {'FALTA':>10s}")
            missing.append(t)
            conn.rollback()

    cur.close()
    conn.close()

    print()
    if missing:
        print(f"⚠ Quedaron sin crear: {', '.join(missing)}")
        return 3
    print("=" * 60)
    print(" ✔ TODO LISTO · Lanza:  streamlit run dashboard_streamlit/streamlit_app.py")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
