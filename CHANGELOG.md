# Changelog

Todos los cambios relevantes de este proyecto se documentan aquí.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [Versionado Semántico](https://semver.org/lang/es/).

## [2.0.0] - 2026-10-26

### 🔧 Mantenimiento

- **Arquitectura:** se eliminó la duplicación entre `scripts/01_data_generation.py` (738 líneas, la versión que realmente se usaba) y `app/generators/` (la versión con pruebas). El script ahora es una entrada de ~40 líneas que usa el paquete `app/`.
- **SOLID:** `ProjectIntegrator` depende de `IDatabaseManager` y recibe los generadores por inyección; las sentencias SQL viven en `app/db/statements.py`; el resultado es un objeto `PipelineResult`.
- **Corregido:** los generadores de `app/` habían perdido dos reglas de negocio del script original: varias rutas por par de ciudades (3 con Bogotá, 2 en el resto → 48 rutas) y 95 % de conductores activos. Ambas restauradas.
- **Mejora:** los generadores usan un generador aleatorio propio por instancia; el script original modificaba el estado aleatorio global de Python y NumPy.
- Nuevo parámetro `--scale` para generar más volumen.
- 3 pruebas nuevas, incluida la orquestación completa con una base en memoria (8 en total).
- Verificación de punta a punta en PostgreSQL 16: mismos volúmenes que la versión anterior, 8 vistas creadas y las 5 páginas del dashboard sin excepciones.

## [1.1.0] - 2026-10-26

### 🔧 Mantenimiento

- **Corregido:** la vista `v_dim_date` fallaba en PostgreSQL (CTE recursiva que mezclaba `date` y `timestamp`); como el script corre en una transacción, ninguna de las 8 vistas del dashboard se creaba. Ahora se crean todas.
- **Corregido:** conflicto entre `numpy==1.26.4` y `pyarrow` 20+ que impedía mostrar tablas en el dashboard; `pyarrow` queda fijado a `<20`.
- Verificación de punta a punta: setup automático con ~535.000 registros sintéticos en PostgreSQL 16, las 8 vistas creadas y las 5 páginas del dashboard abren sin excepciones.
- Instrucciones de setup sin rutas personales.
- README con insignias de CI y versión.
