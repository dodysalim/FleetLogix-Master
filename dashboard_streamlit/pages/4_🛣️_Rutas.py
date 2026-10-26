"""
Página 4 · Rutas
Tráfico, eficiencia y costo por ruta.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils import db
from utils.styling import (
    PALETTE, PLOTLY_LAYOUT,
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING,
    fmt_int, fmt_float, fmt_money,
    inject_css, page_header, kpi_card, section, footer,
)

st.set_page_config(page_title="FleetLogix · Rutas", page_icon="🛣️", layout="wide")
inject_css()

page_header(
    title="🛣️ Análisis de Rutas",
    subtitle="Tráfico, distancia, consumo y eficiencia por corredor logístico",
    badge="LOGÍSTICA",
)


try:
    rt = db.route_traffic()
except Exception as exc:
    st.error(f"Error cargando datos: {exc}")
    st.stop()

if rt.empty:
    st.warning("No hay datos de rutas todavía.")
    st.stop()


# -----------------------------------------------------------------------------
# KPIs
# -----------------------------------------------------------------------------
section("📌 KPIs de rutas")
total_rutas = len(rt)
total_viajes = int(rt["trip_count"].sum())
total_km = float((rt["trip_count"] * rt["distance_km"]).sum())
total_fuel = float(rt["total_fuel_liters"].sum() or 0)
avg_eff = float(rt["fuel_efficiency_l_per_100km"].dropna().mean() or 0)

c1, c2, c3, c4, c5 = st.columns(5)
with c1: kpi_card("Rutas activas", fmt_int(total_rutas), "Corredores en uso", "info")
with c2: kpi_card("Viajes totales", fmt_int(total_viajes), "Suma de trip_count", "info")
with c3: kpi_card("Km recorridos", fmt_float(total_km / 1000, 1) + " mil",
                  "trip_count × distance_km", "info")
with c4: kpi_card("Combustible total", fmt_float(total_fuel, 0) + " L",
                  "Acumulado", "warn")
with c5:
    var = "success" if avg_eff < 25 else "warn" if avg_eff < 35 else "danger"
    kpi_card("Eficiencia media", f"{avg_eff:.1f} L/100km", "Promedio rutas", var)


# -----------------------------------------------------------------------------
# Filtros
# -----------------------------------------------------------------------------
st.write("")
fc1, fc2 = st.columns([2, 1])
with fc1:
    origenes = sorted(rt["origin_city"].dropna().unique())
    origen_sel = st.multiselect("Ciudad origen", origenes, default=origenes)
with fc2:
    top_n = st.slider("Top N rutas", 5, 30, 15)

rt_f = rt[rt["origin_city"].isin(origen_sel)]


# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Top rutas por tráfico", "⛽ Eficiencia por ruta", "📋 Detalle"])

with tab1:
    section(f"Top {top_n} rutas por viajes")
    top = rt_f.nlargest(top_n, "trip_count")
    fig = px.bar(
        top.sort_values("trip_count"),
        x="trip_count", y="route_label",
        color="distance_km",
        orientation="h",
        color_continuous_scale="Cividis",
        labels={"trip_count": "Viajes", "distance_km": "Distancia (km)"},
        hover_data=["distinct_vehicles", "distinct_drivers", "total_deliveries"],
    )
    fig.update_layout(
        **PLOTLY_LAYOUT, height=max(400, 28 * len(top) + 80),
        xaxis_title="Cantidad de viajes", yaxis_title=None,
    )
    st.plotly_chart(fig, width='stretch')


with tab2:
    section(f"Eficiencia (L/100km) — Top {top_n} rutas")
    eff_df = rt_f.dropna(subset=["fuel_efficiency_l_per_100km"]) \
                 .nlargest(top_n, "trip_count")
    fig = px.scatter(
        eff_df,
        x="distance_km",
        y="fuel_efficiency_l_per_100km",
        size="trip_count",
        color="origin_city",
        hover_name="route_label",
        hover_data=["destination_city", "total_fuel_liters"],
        color_discrete_sequence=PALETTE,
        labels={
            "distance_km": "Distancia (km)",
            "fuel_efficiency_l_per_100km": "Consumo (L/100km)",
        },
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=520)
    st.plotly_chart(fig, width='stretch')


with tab3:
    section("Detalle completo de rutas")
    vista = rt_f.rename(columns={
        "route_code": "Código",
        "origin_city": "Origen",
        "destination_city": "Destino",
        "route_label": "Ruta",
        "distance_km": "Distancia (km)",
        "estimated_duration_hours": "Duración (h)",
        "toll_cost": "Peajes",
        "trip_count": "Viajes",
        "distinct_vehicles": "Vehículos",
        "distinct_drivers": "Conductores",
        "total_deliveries": "Entregas",
        "total_fuel_liters": "Combustible (L)",
        "avg_fuel_per_trip": "L/viaje",
        "fuel_efficiency_l_per_100km": "L/100km",
    }).drop(columns=["route_id"], errors="ignore")
    st.dataframe(vista, width='stretch', hide_index=True, height=420)

    csv = rt_f.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv,
                       file_name="rutas_traffic.csv", mime="text/csv")

footer()
