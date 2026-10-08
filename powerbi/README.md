# FleetLogix Analytics — Power BI

PENDIENTE DE DATOS · exporta las vistas PostgreSQL originales · no se inventan viajes ni KPIs

## Abrir

1. Descarga el repositorio completo.
2. Ejecuta `python powerbi/configure_data.py`. Alternativamente, en Transformar datos → Administrar parámetros cambia `DataFolder` a la carpeta `powerbi/data/` con separador final.
3. Abre `powerbi/Analytics.pbip` en Power BI Desktop y pulsa Actualizar.

## Estructura y correspondencia

Las cinco páginas corresponden a Resumen, Flota, Conductores, Rutas y Combustible. No hay PostgreSQL accesible ni CSV exportados en el repositorio. Los esquemas están preparados, pero los gráficos quedan vacíos hasta exportar datos. No se considera un dashboard terminado con datos.

Ejecuta `python dashboard/data_exports/export_to_csv.py` con PG_HOST/PG_PORT/PG_DB/PG_USER/PG_PASS configurados y luego `python powerbi/export_data.py`. Los filtros de cada página afectan a su vista agregada; no se simula un filtro temporal global sobre vistas que no tienen fecha.

Las páginas conservan el análisis del proyecto original. Los controles de entrenamiento, conexión, escritura SQL e inferencia en vivo siguen en Python/Streamlit. El informe consume resultados exportados; no reemplaza esos servicios. Los CSV conservan su grano, y las medidas evitan sumar porcentajes o promedios.

## Verificación de esta entrega

El serializador TMDL nativo instalado con Power BI Desktop aceptó el modelo. Se comprobaron las referencias de los campos y los límites de cada visual. Esto valida la estructura; la apertura, actualización y representación de los gráficos se comprueban por separado. Los proyectos sin datos siguen pendientes.
