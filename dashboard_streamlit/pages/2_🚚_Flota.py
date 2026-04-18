"""
Página 2 · Flota
Análisis de rendimiento de vehículos + alertas de mantenimiento.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import db
from utils.styling import (
    PALETTE, PLOTLY_LAYOUT,
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    fmt_int, fmt_float, fmt_money,
    inject_css, page_header, kpi_card, section, footer,
)

st.set_page_config(page_title="FleetLogix · Flota", page_icon="🚚", layout="wide")
inject_css()

page_header(
    title="🚚 Análisis de Flota",
    subtitle="Rendimiento por vehículo, utilización de capacidad y alertas de mantenimiento",
    badge="OPERACIONES",
)


# -----------------------------------------------------------------------------
# Datos
# -----------------------------------------------------------------------------
try:
    veh = db.vehicle_performance()
    alerts = db.maintenance_alerts()
except Exception as exc:
    st.error(f"Error cargando datos: {exc}")
    st.stop()


# -----------------------------------------------------------------------------
# KPIs rápidos
# -----------------------------------------------------------------------------
section("📌 KPIs de flota")
total_veh = len(veh)
activos = int((veh["vehicle_status"] == "active").sum())
mant = int((veh["vehicle_status"] == "maintenance").sum())
avg_util = float(veh["avg_capacity_utilization_pct"].dropna().mean() or 0)

c1, c2, c3, c4, c5 = st.columns(5)
with c1: kpi_card("Vehículos totales", fmt_int(total_veh), "En el padrón", "info")
with c2: kpi_card("Activos", fmt_int(activos), "status = active", "success")
with c3: kpi_card("En mantenimiento", fmt_int(mant), "status = maintenance", "warn")
with c4:
    alert_crit = int((alerts["alert_level"].isin(["VENCIDO", "ESTA SEMANA"])).sum()) if len(alerts) else 0
    kpi_card("Alertas críticas", fmt_int(alert_crit), "Mant. vencido o esta semana",
             "danger" if alert_crit > 0 else "success")
with c5:
    kpi_card("Utilización promedio", f"{avg_util:.1f}%", "Capacidad cargada", "info")


# -----------------------------------------------------------------------------
# Filtros
# -----------------------------------------------------------------------------
st.write("")
fc1, fc2 = st.columns([1, 1])
with fc1:
    tipos = sorted([t for t in veh["vehicle_type"].dropna().unique()])
    tipos_sel = st.multiselect("Tipo de vehículo", tipos, default=tipos)
with fc2:
    fuels = sorted([f for f in veh["fuel_type"].dropna().unique()])
    fuels_sel = st.multiselect("Tipo de combustible", fuels, default=fuels)

veh_f = veh[
    veh["vehicle_type"].isin(tipos_sel) &
    veh["fuel_type"].isin(fuels_sel)
]


# -----------------------------------------------------------------------------
# Tabs con visualizaciones
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Top vehículos", "🎯 Scatter eficiencia", "🛠 Alertas de mantenimiento"])

with tab1:
    section("Top 15 vehículos por viajes completados")
    top = veh_f.nlargest(15, "completed_trips")[
        ["license_plate", "vehicle_type", "completed_trips", "total_fuel_liters",
         "avg_capacity_utilization_pct", "fuel_efficiency_l_per_100km"]
    ]
    fig = px.bar(
        top.sort_values("completed_trips"),
        x="completed_trips", y="license_plate",
        color="vehicle_type",
        orientation="h",
        color_discrete_sequence=PALETTE,
        hover_data=["total_fuel_liters", "avg_capacity_utilization_pct"],
    )
    fig.update_layout(
        **PLOTLY_LAYOUT, height=520,
        xaxis_title="Viajes completados", yaxis_title=None,
        legend_title="Tipo",
    )
    st.plotly_chart(fig, width='stretch')


with tab2:
    section("Utilización vs. Eficiencia de combustible")
    st.caption("Cada punto es un vehículo. Tamaño = total de viajes. "
               "Ideal: arriba-izquierda (alta utilización, bajo consumo).")
    scatter_df = veh_f.dropna(subset=["avg_capacity_utilization_pct", "fuel_efficiency_l_per_100km"])
    if scatter_df.empty:
        st.info("Sin datos para el filtro actual.")
    else:
        fig = px.scatter(
            scatter_df,
            x="fuel_efficiency_l_per_100km",
            y="avg_capacity_utilization_pct",
            size="total_trips",
            color="vehicle_type",
            hover_name="license_plate",
            hover_data=["fuel_type", "capacity_kg", "total_fuel_liters"],
            color_discrete_sequence=PALETTE,
        )
        fig.update_layout(
            **PLOTLY_LAYOUT, height=520,
            xaxis_title="Consumo (L / 100 km)",
            yaxis_title="Utilización de capacidad (%)",
        )
        st.plotly_chart(fig, width='stretch')


with tab3:
    section("Alertas de mantenimiento")
    if alerts.empty:
        st.success("✅ No hay alertas activas de mantenimiento.")
    else:
        # Summary por nivel
        sm = alerts["alert_level"].value_counts().reindex(
            ["VENCIDO", "ESTA SEMANA", "ESTE MES", "OK"], fill_value=0
        ).reset_index()
        sm.columns = ["Nivel", "Total"]
        color_map = {
            "VENCIDO": COLOR_DANGER,
            "ESTA SEMANA": COLOR_WARNING,
            "ESTE MES": COLOR_PRIMARY,
            "OK": COLOR_SUCCESS,
        }

        col_a, col_b = st.columns([1, 2])
        with col_a:
            fig = px.bar(
                sm, x="Total", y="Nivel", orientation="h",
                color="Nivel", color_discrete_map=color_map,
            )
            _layout_alerts = dict(PLOTLY_LAYOUT)
            _layout_alerts["yaxis"] = dict(
                categoryorder="array",
                categoryarray=["OK", "ESTE MES", "ESTA SEMANA", "VENCIDO"],
                **PLOTLY_LAYOUT.get("yaxis", {}),
            )
            fig.update_layout(**_layout_alerts, height=300, showlegend=False)
            st.plotly_chart(fig, width='stretch')
        with col_b:
            tabla = alerts[[
                "license_plate", "vehicle_type", "maintenance_type",
                "next_maintenance_date", "days_until_maintenance",
                "cost", "alert_level",
            ]].rename(columns={
                "license_plate": "Placa",
                "vehicle_type": "Tipo",
                "maintenance_type": "Mantenimiento",
                "next_maintenance_date": "Próxima fecha",
                "days_until_maintenance": "Días restantes",
                "cost": "Costo último",
                "alert_level": "Nivel",
            })
            st.dataframe(tabla, width='stretch', hide_index=True, height=300)

        # Descargar CSV
        csv = alerts.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Descargar alertas completas (CSV)",
            csv, file_name="alertas_mantenimiento.csv", mime="text/csv",
        )


# -----------------------------------------------------------------------------
# Detalle de flota
# -----------------------------------------------------------------------------
st.write("")
section("📋 Detalle completo de vehículos")
st.dataframe(
    veh_f.rename(columns={
        "license_plate": "Placa",
        "vehicle_type": "Tipo",
        "fuel_type": "Combustible",
        "capacity_kg": "Capacidad (kg)",
        "vehicle_status": "Estado",
        "total_trips": "Viajes",
        "completed_trips": "Completados",
        "total_fuel_liters": "Combustible (L)",
        "avg_fuel_per_trip": "L/viaje",
        "total_weight_kg": "Peso total (kg)",
        "avg_capacity_utilization_pct": "Util. %",
        "fuel_efficiency_l_per_100km": "L/100km",
    }).drop(columns=["vehicle_id"], errors="ignore"),
    width='stretch', hide_index=True, height=380,
)

footer()
