"""
Página 5 · Combustible
Consumo mensual, eficiencia por tipo y análisis comparativo.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import db
from utils.styling import (
    PALETTE, PLOTLY_LAYOUT,
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING,
    fmt_int, fmt_float,
    inject_css, page_header, kpi_card, section, footer,
)

st.set_page_config(page_title="FleetLogix · Combustible", page_icon="⛽", layout="wide")
inject_css()

page_header(
    title="⛽ Análisis de Combustible",
    subtitle="Consumo mensual, eficiencia por tipo de vehículo y tendencias",
    badge="SOSTENIBILIDAD",
)


try:
    fuel = db.fuel_efficiency()
except Exception as exc:
    st.error(f"Error cargando datos: {exc}")
    st.stop()

if fuel.empty:
    st.warning("No hay datos de eficiencia de combustible aún.")
    st.stop()

fuel["month"] = pd.to_datetime(fuel["month"])


# -----------------------------------------------------------------------------
# KPIs
# -----------------------------------------------------------------------------
section("📌 KPIs de combustible")
total_L = float(fuel["total_fuel_liters"].sum())
total_km = float(fuel["total_distance_km"].sum() or 0)
avg_eff = (total_L / total_km * 100) if total_km else 0
trip_count = int(fuel["trip_count"].sum())
meses = fuel["month"].nunique()

c1, c2, c3, c4, c5 = st.columns(5)
with c1: kpi_card("Total combustible", fmt_float(total_L, 0) + " L", "Acumulado histórico", "warn")
with c2: kpi_card("Total distancia", fmt_float(total_km / 1000, 1) + " mil km", "Km recorridos", "info")
with c3:
    var = "success" if avg_eff < 25 else "warn" if avg_eff < 35 else "danger"
    kpi_card("Eficiencia global", f"{avg_eff:.2f} L/100km", "Consumo promedio", var)
with c4: kpi_card("Viajes con consumo", fmt_int(trip_count), "Registros válidos", "info")
with c5: kpi_card("Meses con datos", fmt_int(meses), "Cobertura temporal", "info")


# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Tendencia mensual", "🚚 Eficiencia por tipo",
    "🥧 Composición por combustible", "📋 Datos"
])

with tab1:
    section("Evolución mensual del consumo")
    monthly = fuel.groupby("month", as_index=False).agg(
        total_fuel_liters=("total_fuel_liters", "sum"),
        total_distance_km=("total_distance_km", "sum"),
        trip_count=("trip_count", "sum"),
    )
    monthly["eff_l_100km"] = (monthly["total_fuel_liters"] /
                              monthly["total_distance_km"].replace(0, pd.NA) * 100).round(2)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly["month"], y=monthly["total_fuel_liters"],
        name="Combustible (L)", marker_color=COLOR_WARNING, opacity=0.75,
    ))
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["eff_l_100km"],
        name="L/100km", yaxis="y2", mode="lines+markers",
        line=dict(color=COLOR_PRIMARY, width=3),
    ))
    layout = dict(PLOTLY_LAYOUT)
    layout.update(
        height=440,
        hovermode="x unified",
        yaxis=dict(title="Combustible (L)", **PLOTLY_LAYOUT["yaxis"]),
        yaxis2=dict(title="Eficiencia (L/100km)", overlaying="y",
                    side="right", gridcolor="#2D3748"),
    )
    fig.update_layout(**layout)
    st.plotly_chart(fig, width='stretch')


with tab2:
    section("Eficiencia por tipo de vehículo")
    by_type = fuel.groupby("vehicle_type", as_index=False).agg(
        total_fuel=("total_fuel_liters", "sum"),
        total_km=("total_distance_km", "sum"),
        trips=("trip_count", "sum"),
    )
    by_type["eff_l_100km"] = (by_type["total_fuel"] /
                              by_type["total_km"].replace(0, pd.NA) * 100).round(2)

    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.bar(
            by_type.sort_values("eff_l_100km"),
            x="eff_l_100km", y="vehicle_type",
            orientation="h",
            color="eff_l_100km",
            color_continuous_scale=["#00D4AA", "#F8B400", "#EF4444"],
            labels={"eff_l_100km": "L/100km", "vehicle_type": "Tipo"},
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=380,
                          xaxis_title="Consumo (L/100km)", yaxis_title=None)
        st.plotly_chart(fig, width='stretch')
    with col_b:
        fig = px.bar(
            by_type.sort_values("trips"),
            x="trips", y="vehicle_type",
            orientation="h",
            color="vehicle_type",
            color_discrete_sequence=PALETTE,
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=380,
                          xaxis_title="Viajes completados",
                          yaxis_title=None, showlegend=False)
        st.plotly_chart(fig, width='stretch')


with tab3:
    section("Composición por tipo de combustible")
    by_fuel = fuel.groupby("fuel_type", as_index=False).agg(
        total_fuel=("total_fuel_liters", "sum"),
        trips=("trip_count", "sum"),
    )

    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.pie(
            by_fuel, names="fuel_type", values="total_fuel",
            hole=0.55, color_discrete_sequence=PALETTE,
        )
        fig.update_traces(textposition="outside", textinfo="label+percent",
                          marker=dict(line=dict(color="#0E1117", width=2)))
        fig.update_layout(**PLOTLY_LAYOUT, height=380,
                          title_text="Litros consumidos por tipo")
        st.plotly_chart(fig, width='stretch')
    with col_b:
        fig = px.pie(
            by_fuel, names="fuel_type", values="trips",
            hole=0.55, color_discrete_sequence=PALETTE,
        )
        fig.update_traces(textposition="outside", textinfo="label+percent",
                          marker=dict(line=dict(color="#0E1117", width=2)))
        fig.update_layout(**PLOTLY_LAYOUT, height=380,
                          title_text="Viajes por tipo")
        st.plotly_chart(fig, width='stretch')


with tab4:
    section("Detalle mensual")
    vista = fuel.rename(columns={
        "month": "Mes",
        "vehicle_type": "Tipo vehículo",
        "fuel_type": "Combustible",
        "trip_count": "Viajes",
        "total_fuel_liters": "Total L",
        "avg_fuel_per_trip": "L/viaje",
        "total_distance_km": "Distancia (km)",
        "fuel_efficiency_l_per_100km": "L/100km",
    })
    vista["Mes"] = vista["Mes"].dt.strftime("%Y-%m")
    st.dataframe(vista, width='stretch', hide_index=True, height=420)

    csv = fuel.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv,
                       file_name="fuel_efficiency.csv", mime="text/csv")

footer()
