# Verificación · FleetLogix

Fecha: 7 de octubre de 2026 (Ecuador). Entorno local Python 3.12.14. Las dependencias de QA se registran aparte; esta comprobación no certifica todas las combinaciones de versiones del proyecto.

## Ejecutado

Cinco pruebas aprobadas: reproducibilidad, integridad de entregas y contraseñas con caracteres reservados. Arranque comprobado; informa la ausencia de PostgreSQL.

## Dependencias externas y límites

Necesita PostgreSQL y las vistas SQL. El dashboard lee DB_HOST, DB_PORT, DB_NAME, DB_USER y DB_PASSWORD, o Streamlit Secrets. El exportador usa PG_HOST, PG_PORT, PG_DB, PG_USER y PG_PASS.

Power BI contiene esquemas pendientes de exportación. AWS y otras integraciones descritas en el proyecto no se verificaron como servicios en producción. No se afirma ahorro ni throughput medido.

## Presentación Power BI

Las definiciones se revisaron para límites y superposiciones, y el diseño móvil sigue el esquema oficial PBIR. La prueba nativa completa en teléfono permanece pendiente. Las fuentes externas deben exportarse antes de actualizar las páginas sin datos.
