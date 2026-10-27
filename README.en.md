<p align="center"><img src="https://dodysalim.github.io/assets/project-covers/fleetlogix.webp" alt="FleetLogix" width="100%"></p>

<h1 align="center">FleetLogix</h1>

<p align="center"><b>Synthetic data generation and logistics modeling to analyze fleet, routes and deliveries.</b></p>

<p align="center"><img src="https://img.shields.io/badge/Henry_·_Module_2-75E6CE?style=for-the-badge&labelColor=0b1222" alt="Henry · Module 2"></p>

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"> <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"> <img src="https://img.shields.io/badge/SQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="SQL"> <img src="https://img.shields.io/badge/Snowflake-29B5E8?style=flat-square&logo=snowflake&logoColor=white" alt="Snowflake"> <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"> <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit"> <img src="https://img.shields.io/badge/Power_BI-F2C811?style=flat-square&logoColor=black" alt="Power BI">
</p>

<p align="center"><a href="https://dodysalim.github.io/"><b>🌐 Portfolio</b></a> · <a href="README.md"><b>🇪🇸 Versión en español</b></a></p>

---

## 📌 At a glance

| | |
| --- | --- |
| **🎯 Problem** | Turn related logistics entities into service and performance indicators. |
| **🛠️ Solution** | SOLID generation pipeline (injectable generators and database), relational schema and 8 analytical views. |
| **📈 Deliverables** | ~535,000 synthetic rows, 5-page Streamlit dashboard and Power BI export. |
| **🧪 Quality** | 8 automated tests; verified end-to-end on PostgreSQL 16. |

## 🏗️ Architecture

```mermaid
flowchart LR
    CLI[scripts/01_data_generation.py] --> INT[ProjectIntegrator<br/>fachada]
    subgraph GEN[app/generators · IDataGenerator]
        V[Vehículos] --- DR[Conductores] --- R[Rutas] --- T[Viajes] --- DE[Entregas] --- M[Mantenimiento]
    end
    INT --> GEN
    INT --> DBM{IDatabaseManager}
    DBM --> PG[(PostgreSQL<br/>~535.000 filas)]
    DBM -.-> SF[(Snowflake)]
    PG --> VW[8 vistas analíticas]
    VW --> ST[Streamlit · 5 páginas]
    VW --> PBI[Power BI]
```

## 🚀 How to run

```bash
pip install -r requirements.txt -r dashboard_streamlit/requirements.txt
bash dashboard/setup/setup.sh        # PostgreSQL + data + views
python -m streamlit run dashboard_streamlit/streamlit_app.py
python -m pytest tests -q
```

## ⚖️ Scope

Synthetic data; AWS integrations described in the project were not verified as production services.

---

<p align="center">
<b>Dody Dueñas Remache</b> · Data Analyst / Data Scientist · Guayaquil, Ecuador (remote LATAM)<br>
<a href="https://dodysalim.github.io/">Portfolio</a> · <a href="https://github.com/dodysalim">GitHub</a> · <a href="https://www.linkedin.com/in/dody-duenas/">LinkedIn</a> · <a href="mailto:dodydurema67@gmail.com">dodydurema67@gmail.com</a>
</p>
