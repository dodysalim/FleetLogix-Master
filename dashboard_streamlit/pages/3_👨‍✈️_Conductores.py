"""
Página 3 · Conductores
Ranking, tasa de éxito de entregas y alertas de licencia.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils import db
from utils.styling import (
    PALETTE, PLOTLY_LAYOUT,
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    fmt_int, fmt_pct,
    inject_css, page_header, kpi_card, section, footer,
)

st.set_page_config(page_title="FleetLogix · Conductores", page_icon="👨‍✈️", layout="wide")
inject_css()

page_header(
    title="👨‍✈️ Análisis de Conductores",
    subtitle="Ranking de desempeño, tasa de éxito y control de licencias",
    badge="RRHH · OPERACIONES",
)


try:
    drv = db.driver_performance()
except Exception as exc:
    st.error(f"Error cargando datos: {exc}")
    st.stop()


# -----------------------------------------------------------------------------
# KPIs
# -----------------------------------------------------------------------------
section("📌 KPIs de conductores")
total = len(drv)
activos = int((drv["driver_status"] == "active").sum())
venc = int((drv["license_status"] == "VENCIDA").sum())
por_venc = int((drv["license_status"] == "POR VENCER").sum())
tasa_prom = float(drv["success_rate_pct"].dropna().mean() or 0)

c1, c2, c3, c4, c5 = st.columns(5)
with c1: kpi_card("Total conductores", fmt_int(total), "En el padrón", "info")
with c2: kpi_card("Activos", fmt_int(activos), "status = active", "success")
with c3:
    kpi_card("Licencias vencidas", fmt_int(venc), "Acción inmediata",
             "danger" if venc > 0 else "success")
with c4:
    kpi_card("Por vencer (30d)", fmt_int(por_venc), "Renovar pronto",
             "warn" if por_venc > 0 else "success")
with c5:
    var = "success" if tasa_prom >= 85 else "warn" if tasa_prom >= 70 else "danger"
    kpi_card("Tasa éxito promedio", fmt_pct(tasa_prom), "Entregas exitosas", var)


# -----------------------------------------------------------------------------
# Filtros
# -----------------------------------------------------------------------------
st.write("")
fc1, fc2 = st.columns([1, 1])
with fc1:
    estados = sorted(drv["driver_status"].dropna().unique().tolist())
    estados_sel = st.multiselect("Estado", estados, default=estados)
with fc2:
    top_n = st.slider("Top N conductores", 5, 30, 15)

drv_f = drv[drv["driver_status"].isin(estados_sel)]


# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🏆 Top por viajes", "✅ Tasa de éxito", "🪪 Alertas de licencia"])

with tab1:
    section(f"Top {top_n} conductores por viajes completados")
    top = drv_f.nlargest(top_n, "completed_trips")
    fig = px.bar(
        top.sort_values("completed_trips"),
        x="completed_trips", y="full_name",
        color="success_rate_pct",
        orientation="h",
        color_continuous_scale=["#EF4444", "#F59E0B", "#00D4AA"],
        hover_data=["employee_code", "total_deliveries", "successful_deliveries"],
        labels={"success_rate_pct": "% Éxito"},
    )
    fig.update_layout(
        **PLOTLY_LAYOUT, height=max(400, 28 * len(top) + 80),
        xaxis_title="Viajes completados", yaxis_title=None,
    )
    st.plotly_chart(fig, width='stretch')


with tab2:
    section(f"Top {top_n} por tasa de éxito de entregas")
    # Filtrar conductores con al menos 10 entregas para que la tasa sea significativa
    filtered = drv_f[drv_f["total_deliveries"] >= 10].nlargest(top_n, "success_rate_pct")
    if filtered.empty:
        st.info("Sin conductores con ≥10 entregas en el filtro.")
    else:
        fig = px.bar(
            filtered.sort_values("success_rate_pct"),
            x="success_rate_pct", y="full_name",
            color="total_deliveries",
            orientation="h",
            color_continuous_scale="Viridis",
            labels={"success_rate_pct": "% Éxito", "total_deliveries": "Total entregas"},
        )
        fig.update_layout(
            **PLOTLY_LAYOUT, height=max(400, 28 * len(filtered) + 80),
            xaxis_title="Tasa de éxito (%)", yaxis_title=None,
            xaxis_range=[0, 100],
        )
        st.plotly_chart(fig, width='stretch')


with tab3:
    section("Estado de licencias")
    lic = drv["license_status"].value_counts().reindex(
        ["VIGENTE", "POR VENCER", "VENCIDA"], fill_value=0
    ).reset_index()
    lic.columns = ["Estado", "Total"]
    color_map = {
        "VIGENTE": COLOR_SUCCESS,
        "POR VENCER": COLOR_WARNING,
        "VENCIDA": COLOR_DANGER,
    }

    col_a, col_b = st.columns([1, 2])
    with col_a:
        fig = px.pie(
            lic, names="Estado", values="Total", hole=0.55,
            color="Estado", color_discrete_map=color_map,
        )
        fig.update_traces(textinfo="label+value",
                          marker=dict(line=dict(color="#0E1117", width=2)))
        fig.update_layout(**PLOTLY_LAYOUT, height=380, showlegend=False)
        st.plotly_chart(fig, width='stretch')
    with col_b:
        alerts = drv[drv["license_status"].isin(["VENCIDA", "POR VENCER"])][
            ["employee_code", "full_name", "license_expiry", "license_status", "driver_status"]
        ].rename(columns={
            "employee_code": "Código",
            "full_name": "Nombre",
            "license_expiry": "Vencimiento",
            "license_status": "Estado licencia",
            "driver_status": "Estado contrato",
        })
        if alerts.empty:
            st.success("✅ Todas las licencias están vigentes.")
        else:
            st.dataframe(alerts, width='stretch', hide_index=True, height=340)


# -----------------------------------------------------------------------------
# Detalle completo
# -----------------------------------------------------------------------------
st.write("")
section("📋 Detalle completo de conductores")
vista = drv_f.rename(columns={
    "employee_code": "Código",
    "full_name": "Nombre",
    "driver_status": "Estado",
    "license_status": "Licencia",
    "license_expiry": "Vto. licencia",
    "hire_date": "Contratación",
    "total_trips": "Viajes",
    "completed_trips": "Completados",
    "total_deliveries": "Entregas",
    "successful_deliveries": "Exitosas",
    "success_rate_pct": "% Éxito",
    "total_fuel_liters": "Combustible (L)",
}).drop(columns=["driver_id", "first_name", "last_name"], errors="ignore")
st.dataframe(vista, width='stretch', hide_index=True, height=380)

# CSV download
csv = drv_f.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Descargar CSV completo", csv,
                   file_name="conductores_performance.csv", mime="text/csv")

footer()
