# Changelog

Todos los cambios relevantes de este proyecto se documentan aquí.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [Versionado Semántico](https://semver.org/lang/es/).

## [1.1.0] - 2026-10-26

### 🔧 Mantenimiento

- **Corregido:** la vista `v_dim_date` fallaba en PostgreSQL (CTE recursiva que mezclaba `date` y `timestamp`); como el script corre en una transacción, ninguna de las 8 vistas del dashboard se creaba. Ahora se crean todas.
- **Corregido:** conflicto entre `numpy==1.26.4` y `pyarrow` 20+ que impedía mostrar tablas en el dashboard; `pyarrow` queda fijado a `<20`.
- Verificación de punta a punta: setup automático con ~535.000 registros sintéticos en PostgreSQL 16, las 8 vistas creadas y las 5 páginas del dashboard abren sin excepciones.
- Instrucciones de setup sin rutas personales.
- README con insignias de CI y versión.

