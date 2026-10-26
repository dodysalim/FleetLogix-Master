from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
MAPPING={'v_deliveries_timeseries': 'Resumen', 'v_vehicle_performance': 'Flota', 'v_driver_performance': 'Conductores', 'v_route_traffic': 'Rutas', 'v_fuel_efficiency': 'Combustible'}
def main():
    for view,table in MAPPING.items():
        source=ROOT/'dashboard/data_exports'/f'{view}.csv'
        target=ROOT/'powerbi/data'/f'{table}.csv'
        expected=pd.read_csv(target,nrows=0).columns.tolist()
        data=pd.read_csv(source)
        missing=set(expected)-set(data)
        if missing: raise ValueError(f'{view}: faltan columnas {sorted(missing)}')
        data[expected].to_csv(target,index=False,encoding='utf-8')
        print(table,len(data))
if __name__=='__main__': main()
