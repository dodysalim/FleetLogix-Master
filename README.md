<p align="center"><img src="https://dodysalim.github.io/assets/project-covers/fleetlogix.webp" alt="FleetLogix" width="100%"></p>

<h1 align="center">FleetLogix</h1>

<p align="center"><b>Generación de datos y modelado logístico para analizar flota, rutas y entregas.</b></p>

<p align="center">
<img src="https://img.shields.io/badge/Henry_%C2%B7_M%C3%B3dulo_2-75E6CE?style=for-the-badge&labelColor=0b1222" alt="Henry · Módulo 2">
</p>

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"> <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"> <img src="https://img.shields.io/badge/SQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="SQL"> <img src="https://img.shields.io/badge/Snowflake-29B5E8?style=flat-square&logo=snowflake&logoColor=white" alt="Snowflake"> <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"> <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit"> <img src="https://img.shields.io/badge/Power_BI-F2C811?style=flat-square&logoColor=black" alt="Power BI">
</p>

<p align="center">
<a href="https://github.com/dodysalim/FleetLogix-Master/actions"><img src="https://github.com/dodysalim/FleetLogix-Master/actions/workflows/local-tests.yml/badge.svg" alt="CI"></a> <img src="https://img.shields.io/badge/versión-1.1.0-8F7BFF?style=flat-square" alt="Versión 1.1.0"> <img src="https://img.shields.io/badge/licencia-MIT-30405B?style=flat-square" alt="Licencia MIT">
</p>

<p align="center"><a href="https://dodysalim.github.io/"><b>🌐 Portafolio</b></a> · <a href="docs/PORTFOLIO_CASE.md"><b>📄 Caso de estudio</b></a> · <a href="docs/VALIDATION.md"><b>✅ Verificación</b></a></p>

---

## 📌 Resumen en 30 segundos

| | |
| --- | --- |
| **🎯 Problema** | Convertir entidades operativas de logística en indicadores de servicio y rendimiento. |
| **🛠️ Solución** | Generadores reproducibles, ETL, esquema relacional en PostgreSQL y vistas analíticas. |
| **📈 Entregables** | Dashboard Streamlit de 5 vistas (flota, conductores, rutas, combustible) y exportación a Power BI. |
| **🧪 Calidad** | 5 pruebas automatizadas de reproducibilidad e integridad. |
| **👤 Autor** | Dody Dueñas Remache. |

## ❓ La pregunta de negocio

¿Cómo convertir entidades operativas relacionadas en indicadores de servicio y rendimiento logístico?

## ✨ Qué incluye

- Generadores reproducibles por entidad, ETL y consultas analíticas.
- Cinco vistas Streamlit de flota, conductores, rutas y combustible.
- Exportación de vistas PostgreSQL para análisis en Power BI.

## 🚀 Cómo ejecutarlo

Usa Python 3.11 o 3.12 en un entorno independiente. Desde la raíz:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r dashboard_streamlit/requirements.txt
```

Después de configurar los datos:

```bash
python -m streamlit run dashboard_streamlit/streamlit_app.py
```

## 🗂️ Datos y configuración

Para montar la base completa en un paso (PostgreSQL local o Docker), ejecuta `bash dashboard/setup/setup.sh` (o `setup.ps1` en Windows); ver [guía de setup](dashboard/setup/README.md).

Necesita PostgreSQL y las vistas SQL. El dashboard lee DB_HOST, DB_PORT, DB_NAME, DB_USER y DB_PASSWORD, o Streamlit Secrets. El exportador usa PG_HOST, PG_PORT, PG_DB, PG_USER y PG_PASS.

## 📊 Power BI · PC y móvil

[Archivos e instrucciones](powerbi/README.md). Descarga el repositorio completo y abre `powerbi/Abrir-PowerBI.bat` en Windows; después pulsa **Actualizar**. Incluye A4 horizontal a tamaño real (100 %) y diseño móvil vertical. El archivo `.pbip` necesita sus carpetas Report, SemanticModel y data.

## 🧭 Estructura del repositorio

| Ruta | Qué contiene |
| --- | --- |
| [app/generators/](app/generators/) | Datos sintéticos por entidad |
| [app/core/](app/core/) | ETL e integración |
| [sql/](sql/) | Esquema relacional |
| [dashboard/sql/](dashboard/sql/) | Vistas y calendario |
| [dashboard/setup/README.md](dashboard/setup/README.md) | Configuración local de PostgreSQL |
| [dashboard_streamlit/](dashboard_streamlit/) | Dashboard |

## ✅ Calidad y alcance

Cinco pruebas aprobadas: reproducibilidad, integridad de entregas y contraseñas con caracteres reservados. Verificado de punta a punta (26-10-2026): setup automático en PostgreSQL 16 con ~535.000 registros, 8 vistas analíticas y las 5 páginas del dashboard sin errores. Sin base de datos, el dashboard informa la ausencia de PostgreSQL.

Power BI contiene esquemas pendientes de exportación. AWS y otras integraciones descritas en el proyecto no se verificaron como servicios en producción. No se afirma ahorro ni throughput medido.

Para repetir las pruebas desde la raíz:

```bash
python -m pytest tests -q
```

## 👥 Autoría

Proyecto académico Henry M2, con datos sintéticos. Dody Salim Dueñas Remache.

[Documentación anterior](docs/ORIGINAL_README.md), conservada como referencia histórica.

---

<p align="center">
<b>Dody Dueñas Remache</b> · Analista de Datos / Data Scientist<br>
<a href="https://dodysalim.github.io/">Portafolio</a> · <a href="https://github.com/dodysalim">GitHub</a> · <a href="https://www.linkedin.com/in/dody-duenas/">LinkedIn</a> · <a href="mailto:dodydurema67@gmail.com">dodydurema67@gmail.com</a>
</p>
