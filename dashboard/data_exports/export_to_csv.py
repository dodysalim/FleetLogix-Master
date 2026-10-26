"""
====================================================================
FleetLogix · Exportador de vistas analíticas a CSV
====================================================================
Genera un archivo CSV por cada vista del dashboard en `dashboard/data_exports/`.
Útil cuando se quiere armar el dashboard sin conexión directa a PostgreSQL
(ej. demo offline en laptop sin Docker, snapshot para análisis con Excel,
data dump para entrega de tarea, etc.).

USO:
    cd dashboard/data_exports
    python export_to_csv.py                  # exporta todas las vistas
    python export_to_csv.py --only v_kpi_executive
    python export_to_csv.py --format parquet # también soporta parquet
====================================================================
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

# --- Configuración ---------------------------------------------------------

DEFAULT_DSN = {
    "host":     os.getenv("PG_HOST",     "localhost"),
    "port":     int(os.getenv("PG_PORT", 5432)),
    "dbname":   os.getenv("PG_DB",       "fleetlogix_db"),
    "user":     os.getenv("PG_USER",     "postgres"),
    "password": os.getenv("PG_PASS",     "your_password"),
}

VIEWS = [
    "v_kpi_executive",
    "v_deliveries_timeseries",
    "v_vehicle_performance",
    "v_driver_performance",
    "v_route_traffic",
    "v_maintenance_alerts",
    "v_fuel_efficiency",
    "v_dim_date",
]

OUTPUT_DIR = Path(__file__).parent.resolve()


# --- Utilidades ------------------------------------------------------------

def log(msg: str, kind: str = "info") -> None:
    """Logger minimalista con colores ANSI."""
    colors = {"info": "\033[36m", "ok": "\033[32m", "warn": "\033[33m", "err": "\033[31m"}
    reset  = "\033[0m"
    prefix = {"info": "ℹ", "ok": "✔", "warn": "!", "err": "✘"}[kind]
    print(f"{colors[kind]}{prefix} {msg}{reset}", flush=True)


def export_view(conn, view: str, fmt: str = "csv") -> Path | None:
    """Exporta una vista al formato indicado y devuelve la ruta de salida."""
    out_path = OUTPUT_DIR / f"{view}.{fmt}"
    try:
        t0 = time.time()
        df = pd.read_sql_query(f'SELECT * FROM "{view}"', conn)

        if fmt == "csv":
            df.to_csv(out_path, index=False, encoding="utf-8-sig")
        elif fmt == "parquet":
            df.to_parquet(out_path, index=False, engine="pyarrow")
        else:
            log(f"Formato no soportado: {fmt}", "err")
            return None

        elapsed = time.time() - t0
        size_mb = out_path.stat().st_size / 1024 / 1024
        log(
            f"{view:30s} → {out_path.name:40s} "
            f"{len(df):>8} filas · {size_mb:6.2f} MB · {elapsed:5.2f}s",
            "ok",
        )
        return out_path
    except Exception as exc:
        log(f"Error exportando {view}: {exc}", "err")
        return None


# --- Main ------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exporta las vistas analíticas de FleetLogix a archivos planos.",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        default=None,
        help="Subconjunto de vistas a exportar (default: todas)",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "parquet"],
        default="csv",
        help="Formato de salida (default: csv)",
    )
    args = parser.parse_args()

    targets = args.only if args.only else VIEWS
    invalid = [t for t in targets if t not in VIEWS]
    if invalid:
        log(f"Vistas desconocidas: {invalid}. Disponibles: {VIEWS}", "err")
        return 1

    log("Conectando a PostgreSQL ...", "info")
    try:
        conn = psycopg2.connect(**DEFAULT_DSN)
    except psycopg2.OperationalError as exc:
        log(f"No se pudo conectar: {exc}", "err")
        log("¿Está corriendo Docker? ¿El setup script terminó OK?", "warn")
        return 2
    log(f"Conectado a {DEFAULT_DSN['dbname']}@{DEFAULT_DSN['host']}:{DEFAULT_DSN['port']}", "ok")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log(f"Carpeta de salida: {OUTPUT_DIR}", "info")
    log(f"Formato: {args.format} · Vistas: {len(targets)}\n", "info")

    exported: list[Path] = []
    for view in targets:
        result = export_view(conn, view, args.format)
        if result:
            exported.append(result)

    conn.close()

    print()
    log(f"Exportadas {len(exported)}/{len(targets)} vistas en {OUTPUT_DIR}", "ok")
    if len(exported) < len(targets):
        log("Algunas vistas fallaron. Revisa los mensajes arriba.", "warn")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
