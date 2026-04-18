"""
Conexión a PostgreSQL + helpers de lectura con caché de Streamlit.
Se usa SQLAlchemy para pool de conexiones y compatibilidad con pandas.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


# -----------------------------------------------------------------------------
# Carga de configuración
# -----------------------------------------------------------------------------
# Intenta leer .env del proyecto (sube dos niveles desde dashboard_streamlit/utils/)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


def _get_cfg() -> dict:
    """Obtiene credenciales desde st.secrets o variables de entorno."""
    try:
        secrets = st.secrets.get("postgres", {})  # type: ignore[attr-defined]
    except Exception:
        secrets = {}

    return {
        "host":     secrets.get("host",     os.getenv("DB_HOST", "localhost")),
        "port":     secrets.get("port",     os.getenv("DB_PORT", "5432")),
        "user":     secrets.get("user",     os.getenv("DB_USER", "postgres")),
        "password": secrets.get("password", os.getenv("DB_PASSWORD", "Dody2003")),
        "dbname":   secrets.get("dbname",   os.getenv("DB_NAME", "fleetlogix_db")),
    }


@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    """Engine SQLAlchemy cacheado. Una sola conexión pool para toda la app."""
    cfg = _get_cfg()
    url = (
        f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
    )
    return create_engine(url, pool_pre_ping=True, pool_recycle=1800)


# -----------------------------------------------------------------------------
# Helpers de query con caché
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def run_query(sql: str, params: tuple | None = None) -> pd.DataFrame:
    """Ejecuta un SELECT y devuelve DataFrame. Cacheado 5 minutos.

    Convierte automáticamente columnas Decimal (PostgreSQL NUMERIC) a float
    para evitar TypeError en operaciones pandas (nlargest, sort, etc.).
    """
    eng = get_engine()
    with eng.connect() as conn:
        if params:
            df = pd.read_sql(text(sql), conn, params=dict(params))
        else:
            df = pd.read_sql(text(sql), conn)

    # Coerción automática: Decimal / object-numeric → float
    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = pd.to_numeric(df[col], errors="ignore")
            except Exception:
                pass

    return df


@st.cache_data(ttl=300, show_spinner=False)
def scalar(sql: str) -> float | int | str | None:
    """Ejecuta una query que retorna un único valor."""
    eng = get_engine()
    with eng.connect() as conn:
        res = conn.execute(text(sql)).scalar()
        return res


def health_check() -> tuple[bool, str]:
    """Testea la conexión. Útil para mostrar estado en el sidebar."""
    try:
        eng = get_engine()
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Conectado"
    except Exception as exc:
        return False, str(exc)[:120]


# -----------------------------------------------------------------------------
# Queries reutilizables de vistas
# -----------------------------------------------------------------------------
def kpis_executive() -> pd.Series:
    df = run_query("SELECT * FROM v_kpi_executive LIMIT 1")
    return df.iloc[0] if len(df) else pd.Series(dtype="object")


def deliveries_timeseries(start=None, end=None) -> pd.DataFrame:
    where = []
    params = {}
    if start:
        where.append("fecha >= :start")
        params["start"] = start
    if end:
        where.append("fecha <= :end")
        params["end"] = end
    clause = "WHERE " + " AND ".join(where) if where else ""
    sql = f"SELECT * FROM v_deliveries_timeseries {clause} ORDER BY fecha"
    eng = get_engine()
    with eng.connect() as conn:
        df = pd.read_sql(text(sql), conn, params=params)
    # Coerción numérica
    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = pd.to_numeric(df[col], errors="ignore")
            except Exception:
                pass
    return df


def vehicle_performance() -> pd.DataFrame:
    return run_query("SELECT * FROM v_vehicle_performance ORDER BY total_trips DESC")


def driver_performance() -> pd.DataFrame:
    return run_query("SELECT * FROM v_driver_performance ORDER BY total_trips DESC")


def route_traffic() -> pd.DataFrame:
    return run_query("SELECT * FROM v_route_traffic ORDER BY trip_count DESC")


def maintenance_alerts() -> pd.DataFrame:
    return run_query("""
        SELECT * FROM v_maintenance_alerts
        ORDER BY
          CASE alert_level
            WHEN 'VENCIDO'     THEN 0
            WHEN 'ESTA SEMANA' THEN 1
            WHEN 'ESTE MES'    THEN 2
            ELSE 3
          END,
          next_maintenance_date
    """)


def fuel_efficiency() -> pd.DataFrame:
    return run_query("SELECT * FROM v_fuel_efficiency ORDER BY month, vehicle_type")


def delivery_status_breakdown() -> pd.DataFrame:
    """Distribución de estados de entregas (agregado global)."""
    return run_query("""
        SELECT delivery_status AS estado,
               COUNT(*)        AS total
        FROM deliveries
        GROUP BY delivery_status
        ORDER BY total DESC
    """)
