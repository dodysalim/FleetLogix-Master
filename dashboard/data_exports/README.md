# 📤 data_exports/

Carpeta donde caen los CSV/Parquet generados por `export_to_csv.py`.

## Uso

```bash
# Desde la raíz del proyecto
python dashboard/data_exports/export_to_csv.py
```

Genera:
- `v_kpi_executive.csv`
- `v_deliveries_timeseries.csv`
- `v_vehicle_performance.csv`
- `v_driver_performance.csv`
- `v_route_traffic.csv`
- `v_maintenance_alerts.csv`
- `v_fuel_efficiency.csv`
- `v_dim_date.csv`

## Cuándo usarlo

- Demo offline (sin Docker corriendo)
- Compartir snapshot de datos sin dar acceso a la BD
- Backup rápido pre-refactor del modelo

## Notas

- Los CSV se exportan con BOM (`utf-8-sig`) para que Excel y Streamlit standalone los abran sin problemas con tildes.
- Parquet requiere `pyarrow`: `pip install pyarrow`.
- Esta carpeta está en `.gitignore` por defecto (excepto este README y el script).
