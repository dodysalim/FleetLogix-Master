"""
FleetLogix Analytics · Streamlit Dashboard
==========================================
Página principal: Resumen Ejecutivo

Ejecuta con:
    streamlit run streamlit_app.py
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import db
from utils.styling import (
    PALETTE, PLOTLY_LAYOUT, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING,
    COLOR_DANGER,
    fmt_int, fmt_float, fmt_pct, fmt_money,
    inject_css, page_header, kpi_card, section, footer,
)

# -----------------------------------------------------------------------------
# Configuración global de la página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="FleetLogix Analytics · Resumen Ejecutivo",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()


# -----------------------------------------------------------------------------
# Sidebar global (filtros + estado)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🚛 FleetLogix Analytics")
    st.caption("Plataforma corporativa de Business Intelligence")

    st.divider()

    st.markdown("#### 🗓 Rango de fechas")
    today = datetime.now().date()
    default_start = today - timedelta(days=180)
    rango = st.date_input(
        "Período",
        value=(default_start, today),
        max_value=today,
        label_visibility="collapsed",
    )
    if isinstance(rango, tuple) and len(rango) == 2:
        f_start, f_end = rango
    else:
        f_start, f_end = default_start, today

    st.divider()

    if st.button("🔄 Refrescar datos", width='stretch'):
        st.cache_data.clear()
        st.rerun()

    ok, msg = db.health_check()
    estado = f"✅ {msg}" if ok else f"⚠️ {msg}"
    st.markdown(
        f"<div class='fl-side-status'><b>Estado BD:</b><br/>{estado}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='fl-side-status'>"
        f"<b>Última actualización:</b><br/>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        f"</div>",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Header de página
# -----------------------------------------------------------------------------
page_header(
    title="📊 Resumen Ejecutivo",
    subtitle="Visión 360° de operaciones, flota, entregas y mantenimiento — actualizado en tiempo real",
    badge="LIVE · PostgreSQL",
)


# -----------------------------------------------------------------------------
# KPIs principales
# -----------------------------------------------------------------------------
section("📌 Indicadores clave de desempeño (KPIs)")

try:
    kpis = db.kpis_executive()
except Exception as exc:
    st.error(f"❌ No se pudieron cargar los KPIs: {exc}")
    st.stop()

# Fila 1: 6 KPIs operativos
r1 = st.columns(6)
with r1[0]:
    kpi_card("Vehículos activos", fmt_int(kpis.get("active_vehicles")),
             "Flota disponible", "info")
with r1[1]:
    kpi_card("Conductores activos", fmt_int(kpis.get("active_drivers")),
             "Operadores en servicio", "info")
with r1[2]:
    kpi_card("Viajes completados", fmt_int(kpis.get("completed_trips")),
             "Histórico total", "success")
with r1[3]:
    kpi_card("Entregas realizadas", fmt_int(kpis.get("delivered")),
             "Status: delivered", "success")
with r1[4]:
    on_time = kpis.get("on_time_rate_pct")
    variant = "success" if (on_time and on_time >= 85) else "warn" if (on_time and on_time >= 70) else "danger"
    kpi_card("On-Time Rate", fmt_pct(on_time, 1),
             "Entregas a tiempo (≤30 min)", variant)
with r1[5]:
    kpi_card("Total toneladas", fmt_float(kpis.get("total_tons"), 1) + " t",
             "Carga acumulada", "info")

st.write("")  # spacer

# Fila 2: 4 KPIs de operación / mantenimiento
r2 = st.columns(4)
with r2[0]:
    pend = kpis.get("pending_deliveries") or 0
    var = "warn" if pend > 0 else "success"
    kpi_card("Entregas pendientes", fmt_int(pend),
             "Por completar", var)
with r2[1]:
    fail = kpis.get("failed_deliveries") or 0
    var = "danger" if fail > 100 else "warn" if fail > 0 else "success"
    kpi_card("Entregas fallidas", fmt_int(fail),
             "Requieren revisión", var)
with r2[2]:
    maint = kpis.get("vehicles_maintenance_30d") or 0
    var = "warn" if maint > 0 else "success"
    kpi_card("Mantenimiento próximo (30d)", fmt_int(maint),
             "Vehículos a mantener", var)
with r2[3]:
    kpi_card("Costo de mantenimiento", fmt_money(kpis.get("total_maintenance_cost")),
             "Acumulado histórico", "info")


# -----------------------------------------------------------------------------
# Tabs analíticos
# -----------------------------------------------------------------------------
st.write("")
tab1, tab2, tab3 = st.tabs(["📈 Tendencia diaria", "🥧 Distribución de estados", "📊 Volumen vs Peso"])

with tab1:
    section("Evolución diaria de entregas")
    try:
        ts = db.deliveries_timeseries(start=f_start, end=f_end)
    except Exception as exc:
        st.error(f"Error cargando serie temporal: {exc}")
        ts = pd.DataFrame()

    if ts.empty:
        st.info("No hay datos para el rango seleccionado.")
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ts["fecha"], y=ts["delivered"],
            mode="lines", name="Entregadas",
            line=dict(color=COLOR_SUCCESS, width=2.5),
            fill="tozeroy", fillcolor="rgba(0,212,170,0.13)",
        ))
        fig.add_trace(go.Scatter(
            x=ts["fecha"], y=ts["pending"],
            mode="lines", name="Pendientes",
            line=dict(color=COLOR_WARNING, width=2),
        ))
        fig.add_trace(go.Scatter(
            x=ts["fecha"], y=ts["failed"],
            mode="lines", name="Fallidas",
            line=dict(color=COLOR_DANGER, width=2),
        ))
        fig.update_layout(
            **PLOTLY_LAYOUT,
            height=420,
            hovermode="x unified",
            yaxis_title="Cantidad de entregas",
            xaxis_title=None,
        )
        st.plotly_chart(fig, width='stretch')

        # Mini-stats del rango
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total entregas", fmt_int(ts["total_deliveries"].sum()))
        c2.metric("Entregadas", fmt_int(ts["delivered"].sum()))
        c3.metric("Pendientes", fmt_int(ts["pending"].sum()))
        c4.metric("Fallidas", fmt_int(ts["failed"].sum()))


with tab2:
    section("Composición por estado de entrega")
    try:
        breakdown = db.delivery_status_breakdown()
    except Exception as exc:
        st.error(f"Error: {exc}")
        breakdown = pd.DataFrame()

    if breakdown.empty:
        st.info("Sin datos.")
    else:
        col_d, col_t = st.columns([2, 1])
        with col_d:
            fig = px.pie(
                breakdown, names="estado", values="total",
                hole=0.55, color_discrete_sequence=PALETTE,
            )
            fig.update_traces(
                textposition="outside",
                textinfo="label+percent",
                marker=dict(line=dict(color="#0E1117", width=2)),
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=420, showlegend=True)
            st.plotly_chart(fig, width='stretch')
        with col_t:
            st.write("")
            st.dataframe(
                breakdown.rename(columns={"estado": "Estado", "total": "Total"})
                         .assign(**{"% del total": lambda d: (d["Total"] / d["Total"].sum() * 100).round(1)}),
                width='stretch', hide_index=True,
            )


with tab3:
    section("Volumen y peso transportado por día")
    try:
        ts2 = db.deliveries_timeseries(start=f_start, end=f_end)
    except Exception as exc:
        st.error(f"Error: {exc}")
        ts2 = pd.DataFrame()

    if ts2.empty:
        st.info("Sin datos.")
    else:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=ts2["fecha"], y=ts2["total_deliveries"],
            name="Entregas (cantidad)",
            marker_color=COLOR_PRIMARY, opacity=0.85,
        ))
        fig.add_trace(go.Scatter(
            x=ts2["fecha"], y=ts2["total_weight_kg"],
            name="Peso total (kg)",
            mode="lines", yaxis="y2",
            line=dict(color=COLOR_WARNING, width=2.5),
        ))
        layout = dict(PLOTLY_LAYOUT)
        layout.update(
            height=420,
            hovermode="x unified",
            yaxis=dict(title="Cantidad de entregas", **PLOTLY_LAYOUT["yaxis"]),
            yaxis2=dict(title="Peso (kg)", overlaying="y", side="right",
                        gridcolor="#2D3748"),
        )
        fig.update_layout(**layout)
        st.plotly_chart(fig, width='stretch')


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
footer()
