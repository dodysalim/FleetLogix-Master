"""
Estilos, tema corporativo y helpers de UI.
"""
from __future__ import annotations

from datetime import datetime

import streamlit as st

# -----------------------------------------------------------------------------
# Paleta corporativa FleetLogix
# -----------------------------------------------------------------------------
COLOR_PRIMARY = "#4CC9F0"   # Cyan (acento)
COLOR_SECONDARY = "#F8B400" # Ámbar
COLOR_SUCCESS = "#00D4AA"   # Teal
COLOR_WARNING = "#F59E0B"   # Naranja
COLOR_DANGER = "#EF4444"    # Rojo
COLOR_MUTED = "#6B7280"
COLOR_BG = "#0E1117"
COLOR_CARD = "#1A1F2E"
COLOR_CARD_ALT = "#242B3D"
COLOR_BORDER = "#2D3748"
COLOR_TEXT = "#E6EDF3"
COLOR_TEXT_MUTED = "#9CA3AF"

PALETTE = [
    "#4CC9F0", "#00D4AA", "#F8B400", "#A78BFA",
    "#EF4444", "#60A5FA", "#34D399", "#F472B6",
    "#FBBF24", "#94A3B8",
]

# Plotly template con branding
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", size=12, color=COLOR_TEXT),
    colorway=PALETTE,
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(bgcolor=COLOR_CARD, bordercolor=COLOR_PRIMARY, font_size=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=COLOR_BORDER, borderwidth=0),
    xaxis=dict(gridcolor="#2D3748", linecolor="#2D3748", zerolinecolor="#2D3748"),
    yaxis=dict(gridcolor="#2D3748", linecolor="#2D3748", zerolinecolor="#2D3748"),
)


# -----------------------------------------------------------------------------
# CSS global
# -----------------------------------------------------------------------------
GLOBAL_CSS = f"""
<style>
  .main .block-container {{
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1400px;
  }}

  /* Header corporativo */
  .fl-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.25rem;
    background: linear-gradient(90deg, {COLOR_CARD} 0%, {COLOR_CARD_ALT} 100%);
    border-left: 4px solid {COLOR_PRIMARY};
    border-radius: 10px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
  }}
  .fl-header h1 {{
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: {COLOR_TEXT};
  }}
  .fl-header .fl-subtitle {{
    margin-top: 0.2rem;
    font-size: 0.85rem;
    color: {COLOR_TEXT_MUTED};
  }}
  .fl-header .fl-badge {{
    background: {COLOR_PRIMARY}22;
    color: {COLOR_PRIMARY};
    font-size: 0.75rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 12px;
    border: 1px solid {COLOR_PRIMARY}66;
    white-space: nowrap;
  }}

  /* Tarjetas KPI */
  .fl-kpi {{
    background: {COLOR_CARD};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
    padding: 1rem 1.1rem;
    height: 100%;
    transition: transform .15s ease, border-color .15s ease;
  }}
  .fl-kpi:hover {{
    transform: translateY(-2px);
    border-color: {COLOR_PRIMARY}AA;
  }}
  .fl-kpi .fl-kpi-label {{
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {COLOR_TEXT_MUTED};
    font-weight: 600;
  }}
  .fl-kpi .fl-kpi-value {{
    font-size: 1.85rem;
    font-weight: 700;
    line-height: 1.1;
    margin-top: 0.25rem;
    color: {COLOR_TEXT};
  }}
  .fl-kpi .fl-kpi-delta {{
    font-size: 0.78rem;
    margin-top: 0.35rem;
    color: {COLOR_TEXT_MUTED};
  }}
  .fl-kpi.fl-kpi-success {{ border-left: 3px solid {COLOR_SUCCESS}; }}
  .fl-kpi.fl-kpi-warn    {{ border-left: 3px solid {COLOR_WARNING}; }}
  .fl-kpi.fl-kpi-danger  {{ border-left: 3px solid {COLOR_DANGER}; }}
  .fl-kpi.fl-kpi-info    {{ border-left: 3px solid {COLOR_PRIMARY}; }}

  /* Secciones */
  .fl-section-title {{
    font-size: 0.95rem;
    font-weight: 600;
    color: {COLOR_TEXT};
    letter-spacing: 0.03em;
    text-transform: uppercase;
    margin: 1.25rem 0 0.5rem 0;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid {COLOR_BORDER};
  }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{
    background: {COLOR_CARD};
    border-right: 1px solid {COLOR_BORDER};
  }}
  section[data-testid="stSidebar"] .fl-side-status {{
    font-size: 0.75rem;
    color: {COLOR_TEXT_MUTED};
    padding: 0.5rem 0;
    border-top: 1px solid {COLOR_BORDER};
    margin-top: 1rem;
  }}

  /* DataFrames */
  .stDataFrame {{
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
    overflow: hidden;
  }}

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
  }}
  .stTabs [data-baseweb="tab"] {{
    background: transparent;
    border-radius: 8px 8px 0 0;
    padding: 8px 18px;
  }}
  .stTabs [aria-selected="true"] {{
    background: {COLOR_CARD};
    color: {COLOR_PRIMARY} !important;
    font-weight: 600;
  }}

  /* Footer */
  .fl-footer {{
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid {COLOR_BORDER};
    text-align: center;
    font-size: 0.75rem;
    color: {COLOR_TEXT_MUTED};
  }}
</style>
"""


def inject_css() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Componentes reutilizables
# -----------------------------------------------------------------------------
def page_header(title: str, subtitle: str, badge: str | None = None) -> None:
    """Renderiza el header corporativo de cada página."""
    badge_html = f'<span class="fl-badge">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="fl-header">
          <div>
            <h1>{title}</h1>
            <div class="fl-subtitle">{subtitle}</div>
          </div>
          {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, delta: str | None = None, variant: str = "info") -> None:
    """Tarjeta KPI sin depender de st.metric (mejor control visual)."""
    delta_html = f'<div class="fl-kpi-delta">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="fl-kpi fl-kpi-{variant}">
          <div class="fl-kpi-label">{label}</div>
          <div class="fl-kpi-value">{value}</div>
          {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str) -> None:
    st.markdown(f'<div class="fl-section-title">{title}</div>', unsafe_allow_html=True)


def footer() -> None:
    st.markdown(
        f"""
        <div class="fl-footer">
          FleetLogix Analytics · Proyecto Integrador M2 · Henry Data Science ·
          Generado {datetime.now().strftime("%Y-%m-%d %H:%M")}
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Formatos
# -----------------------------------------------------------------------------
def fmt_int(x) -> str:
    try:
        return f"{int(x):,}".replace(",", ".")
    except Exception:
        return "—"


def fmt_float(x, decimals: int = 2) -> str:
    try:
        return f"{float(x):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"


def fmt_pct(x, decimals: int = 1) -> str:
    try:
        return f"{float(x):.{decimals}f}%"
    except Exception:
        return "—"


def fmt_money(x, currency: str = "$") -> str:
    try:
        return f"{currency} {float(x):,.0f}".replace(",", ".")
    except Exception:
        return "—"
