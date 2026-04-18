# 📸 Evidencia de Ejecución Real - FleetLogix Enterprise
## Proyecto Integrador M2 - Henry Data Science

**Autor:** Dody Dueñas  
**Fecha:** Abril 2026  
**Institución:** Henry Data Science

---

> **NOTA:** Para agregar capturas de pantalla reales, tome fotos de la ejecución de estas queries en su herramienta favorita (DBeaver, pgAdmin, DataGrip, etc.) y guárdelas en la carpeta `docs/capturas_de_pantalla/`

---

## 1. Resumen de la Base de Datos

### Registros Totales: 661,276

| Tabla | Registros |
|-------|-----------|
| vehicles | 1,000 |
| drivers | 5,000 |
| routes | 500 |
| trips | 130,000 |
| deliveries | 519,776 |
| maintenance | 5,000 |

---

## 2. Ejecución de Queries - Resultados Reales

### Query 1: Listar Vehículos Activos
```sql
SELECT vehicle_id, license_plate, vehicle_type, status 
FROM vehicles WHERE status = 'active' LIMIT 3;
```
**Resultado:**
```
vehicle_id | license_plate | vehicle_type  | status
-----------|--------------|---------------|--------
1          | AB 3321 ZI   | Motocicleta   | active
2          | P 0133 NB    | Camión Grande | active
3          | OR 8637 GY   | Camión Grande | active
```

---

### Query 2: Agrupar por Tipo de Vehículo
```sql
SELECT vehicle_type, COUNT(*) 
FROM vehicles GROUP BY vehicle_type;
```
**Resultado:**
```
vehicle_type  | count
-------------|------
Van           | 264
Camión Grande | 243
Camión Mediano| 253
Motocicleta   | 240
```

---

### Query 3: Top 5 Rutas por Distancia
```sql
SELECT route_code, origin_city, destination_city, distance_km 
FROM routes ORDER BY distance_km DESC LIMIT 5;
```
**Resultado:**
```
route_code | origin_city  | destination_city | distance_km
-----------|-------------|------------------|------------
R475       | Mendoza     | Buenos Aires     | 1070.20
R164       | Buenos Aires| Mendoza          | 1070.19
R286       | Mendoza     | Buenos Aires     | 1070.09
R107       | Mendoza     | Buenos Aires     | 1069.90
R317       | Mendoza     | Buenos Aires     | 1069.63
```

---

### Query 4: JOIN Triple (trips + vehicles + drivers + routes)
```sql
SELECT t.trip_id, v.license_plate, d.first_name || ' ' || d.last_name, r.route_code
FROM trips t
JOIN vehicles v ON t.vehicle_id = v.vehicle_id
JOIN drivers d ON t.driver_id = d.driver_id
JOIN routes r ON t.route_id = r.route_id
WHERE t.status = 'completed' LIMIT 5;
```
**Resultado:**
```
trip_id | license_plate | driver_name        | route_code
--------|---------------|--------------------|------------
1       | IB 8214 GV    | Moisés Hurtado     | R328
2       | TE 0978 KB    | Román Blazquez     | R217
3       | C 1778 KW    | Chucho Asensio     | R215
4       | CA 7770 ZY   | Celestino Ramos    | R111
5       | ZA 8141 TO   | Heraclio Briones   | R236
```

---

### Query 5: Top Conductores con Más Viajes
```sql
SELECT d.first_name, d.last_name, COUNT(t.trip_id) as total
FROM drivers d
JOIN trips t ON d.driver_id = t.driver_id
GROUP BY d.driver_id, d.first_name, d.last_name
ORDER BY total DESC LIMIT 5;
```
**Resultado:**
```
first_name | last_name   | total
-----------|-------------|------
Dorotea    | Quintanilla | 45
Eloy       | Aguilar    | 45
Natalio    | Fuentes    | 44
Valentina   | Raya       | 44
Marita     | Amorós     | 42
```

---

### Query 6: Entregas por Ciudad
```sql
SELECT r.destination_city, COUNT(del.delivery_id)
FROM deliveries del
JOIN trips t ON del.trip_id = t.trip_id
JOIN routes r ON t.route_id = r.route_id
GROUP BY r.destination_city ORDER BY COUNT(del.delivery_id) DESC LIMIT 5;
```
**Resultado:**
```
destination_city | count
-----------------|--------
Buenos Aires     | 261,122
Rosario          | 73,674
Córdoba          | 62,304
Mendoza          | 61,674
La Plata         | 61,002
```

---

### Query 7: Consumo de Combustible por Ruta
```sql
SELECT r.route_code, SUM(t.fuel_consumed_liters) as total, COUNT(t.trip_id) as trips
FROM trips t JOIN routes r ON t.route_id = r.route_id
WHERE t.status = 'completed'
GROUP BY r.route_code ORDER BY total DESC LIMIT 5;
```
**Resultado:**
```
route_code | total_fuel    | trips
-----------|---------------|------
R196       | 68,720.15 L   | 283
R286       | 67,385.83 L   | 272
R307       | 67,162.13 L   | 276
R147       | 66,954.14 L   | 274
R059       | 66,614.19 L   | 279
```

---

### Query 8: Análisis Mensual (CTE)
```sql
SELECT TO_CHAR(scheduled_datetime, 'YYYY-MM') as mes, COUNT(*) as total,
COUNT(CASE WHEN delivery_status = 'delivered' THEN 1 END) as entregadas
FROM deliveries WHERE scheduled_datetime IS NOT NULL
GROUP BY TO_CHAR(scheduled_datetime, 'YYYY-MM') ORDER BY mes DESC LIMIT 5;
```
**Resultado:**
```
mes    | total  | entregadas
--------|--------|------------
2026-04| 4,784  | 4,073
2026-03| 13,676 | 12,325
2026-02| 12,447 | 11,161
2026-01| 13,628 | 12,258
2025-12| 13,508 | 12,157
```

---

### Query 9: Costo Mantenimiento por Tipo
```sql
SELECT v.vehicle_type, ROUND(AVG(m.cost), 2) as promedio
FROM vehicles v JOIN maintenance m ON v.vehicle_id = m.vehicle_id
GROUP BY v.vehicle_type ORDER BY promedio DESC;
```
**Resultado:**
```
vehicle_type  | promedio
--------------|-------------
Motocicleta   | $313,705.25
Van           | $312,376.04
Camión Grande | $310,789.29
Camión Mediano| $308,042.64
```

---

### Query 10: Window Function (Ranking)
```sql
SELECT d.first_name, r.destination_city, COUNT(del.delivery_id) as cant,
RANK() OVER (PARTITION BY r.destination_city ORDER BY COUNT(del.delivery_id) DESC) as rank
FROM drivers d
JOIN trips t ON d.driver_id = t.driver_id
JOIN routes r ON t.route_id = r.route_id
JOIN deliveries del ON t.trip_id = del.trip_id
GROUP BY d.driver_id, d.first_name, r.destination_city LIMIT 8;
```
**Resultado:**
```
first_name | destination_city | cant | rank
-----------|-----------------|------|----
Luna       | Buenos Aires    | 108  | 1
Chucho     | Buenos Aires    | 106  | 2
Eligio     | Buenos Aires    | 105  | 3
Susanita   | Buenos Aires    | 105  | 3
Elodia     | Buenos Aires    | 105  | 3
Mayte      | Buenos Aires    | 104  | 6
Ester      | Buenos Aires    | 103  | 7
Lucio      | Buenos Aires    | 102  | 8
```

---

### Query 11: Subconsulta (Licencias por Vencer)
```sql
SELECT first_name, last_name, license_expiry FROM drivers
WHERE license_expiry <= CURRENT_DATE + INTERVAL '90 days'
AND status = 'active' ORDER BY license_expiry ASC LIMIT 5;
```
**Resultado:**
```
first_name | last_name    | license_expiry
-----------|--------------|---------------
Dorotea    | Quintanilla | 2026-04-11
Alonso     | Santamaría  | 2026-04-12
Candela    | Casares     | 2026-04-12
Fortunata  | Diego       | 2026-04-12
Ascensión  | Camacho     | 2026-04-13
```

---

### Query 12: Informe Ejecutivo Consolidado
```sql
SELECT 
(SELECT COUNT(*) FROM vehicles WHERE status = 'active') as vehicles,
(SELECT COUNT(*) FROM drivers WHERE status = 'active') as drivers,
(SELECT COUNT(*) FROM trips WHERE status = 'completed') as trips,
(SELECT COUNT(*) FROM deliveries WHERE delivery_status = 'delivered') as entregas,
(SELECT ROUND(SUM(package_weight_kg)/1000, 2) FROM deliveries WHERE delivery_status = 'delivered') as toneladas
```
**Resultado:**
```
Vehículos activos:     1,000
Conductores activos:   5,000
Viajes completados:    123,423
Entregas realizadas:    467,328
Toneladas entregadas:  117,059.08
```

---

## 3. Cómo Tomar las Capturas de Pantalla

### Paso 1: Abrir su herramienta SQL preferida
- **DBeaver**: https://dbeaver.io/
- **pgAdmin**: https://www.pgadmin.org/
- **DataGrip**: https://www.jetbrains.com/datagrip/

### Paso 2: Conectar a la base de datos
```
Host: localhost
Port: 5432
Database: fleetlogix_db
Username: postgres
Password: Dody2003
```

### Paso 3: Ejecutar cada query y tomar captura

### Paso 4: Guardar las imágenes
Guarde cada captura en: `docs/capturas_de_pantalla/`

### Nombres sugeridos para las capturas:
- `01_vehiculos_activos.png`
- `02_conteo_por_tipo.png`
- `03_top_rutas.png`
- `04_join_triple.png`
- `05_top_conductores.png`
- `06_entregas_ciudad.png`
- `07_consumo_combustible.png`
- `08_analisis_mensual.png`
- `09_costo_mantenimiento.png`
- `10_window_function.png`
- `11_licencias_vencer.png`
- `12_informe_ejecutivo.png`

---

**Documento creado para evidencias reales del proyecto**  
**Autor: Dody Dueñas - Henry M2**
