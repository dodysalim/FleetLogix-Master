![FleetLogix](docs/cover.svg)

# FleetLogix

**Generación de datos y modelado logístico para analizar flota, rutas y entregas.**

HENRY · MÓDULO 2 · Python · PostgreSQL · SQL · Streamlit

[Portafolio](https://dodysalim.github.io/) · [Caso y alcance](docs/PORTFOLIO_CASE.md) · [Verificación](docs/VALIDATION.md)

## La pregunta

¿Cómo convertir entidades operativas relacionadas en indicadores de servicio y rendimiento logístico?

## Qué puedes revisar

- Generadores reproducibles por entidad, ETL y consultas analíticas.
- Cinco vistas Streamlit de flota, conductores, rutas y combustible.
- Exportación de vistas PostgreSQL para análisis en Power BI.

## Inicio local

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

## Datos y configuración

Necesita PostgreSQL y las vistas SQL. El dashboard lee DB_HOST, DB_PORT, DB_NAME, DB_USER y DB_PASSWORD, o Streamlit Secrets. El exportador usa PG_HOST, PG_PORT, PG_DB, PG_USER y PG_PASS.

## Power BI · PC y móvil

[Archivos e instrucciones](powerbi/README.md). Descarga el repositorio completo y abre `powerbi/Abrir-PowerBI.bat` en Windows; después pulsa **Actualizar**. Incluye A4 horizontal a tamaño real (100 %) y diseño móvil vertical. El archivo `.pbip` necesita sus carpetas Report, SemanticModel y data.

## Recorrido por el código

| Ruta | Qué contiene |
| --- | --- |
| [app/generators/](app/generators/) | Datos sintéticos por entidad |
| [app/core/](app/core/) | ETL e integración |
| [sql/](sql/) | Esquema relacional |
| [dashboard/sql/](dashboard/sql/) | Vistas y calendario |
| [dashboard/setup/README.md](dashboard/setup/README.md) | Configuración local de PostgreSQL |
| [dashboard_streamlit/](dashboard_streamlit/) | Dashboard |

## Comprobación y alcance

Cinco pruebas aprobadas: reproducibilidad, integridad de entregas y contraseñas con caracteres reservados. Arranque comprobado; informa la ausencia de PostgreSQL.

Power BI contiene esquemas pendientes de exportación. AWS y otras integraciones descritas en el proyecto no se verificaron como servicios en producción. No se afirma ahorro ni throughput medido.

Para repetir las pruebas desde la raíz:

```bash
python -m pytest tests -q
```

## Autoría

Proyecto académico Henry M2, con datos sintéticos. Dody Salim Dueñas Remache.

[Documentación anterior](docs/ORIGINAL_README.md), conservada como referencia histórica.
