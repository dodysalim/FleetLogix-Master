# FleetLogix Enterprise — Simulación AWS Local

## Descripción

Este módulo implementa un **simulador completo de la arquitectura AWS de FleetLogix**
que puede ejecutarse sin credenciales reales de AWS. Replica fielmente el comportamiento
de DynamoDB, SNS, S3 y CloudWatch en memoria y en disco local.

---

## Arquitectura Simulada

```
┌─────────────────┐     ┌──────────────────────────────────────────────────┐
│   API Gateway   │────▶│          AWS Lambda Functions (5)                │
│  (simulado)     │     │  1. lambda_verificar_entrega                     │
└─────────────────┘     │  2. lambda_calcular_eta         (Haversine real) │
                        │  3. lambda_alerta_desvio        (SNS alert)      │
┌─────────────────┐     │  4. lambda_procesar_entrega     (webhook)        │
│  EventBridge    │────▶│  5. lambda_generar_reporte_diario (→ S3)        │
│  (simulado)     │     └──────────┬──────────┬──────────┬────────────────┘
└─────────────────┘                │          │          │
                                   ▼          ▼          ▼
                            DynamoDB       SNS         S3
                           (en memoria)  (consola)  (en disco)
                                          │
                                          ▼
                                     CloudWatch
                                    (métricas + gráficas)
```

---

## Cómo Ejecutar

```bash
# Desde la raíz del proyecto
python -X utf8 scripts/aws_local_simulator.py
```

### Salidas generadas

| Archivo | Descripción |
|---------|-------------|
| `docs/evidencia_ejecucion/aws_simulation/aws_simulation_report.json` | Reporte JSON con todos los resultados |
| `docs/evidencia_ejecucion/aws_simulation/cloudwatch_dashboard.png` | Dashboard CloudWatch simulado |
| `docs/evidencia_ejecucion/aws_simulation/fleetlogix-reports/daily-reports/YYYY-MM-DD.json` | Reporte diario generado por Lambda 5 |

---

## Funciones Lambda Implementadas

### Lambda 1 — Verificar Entrega
- **Trigger:** API Gateway `POST /deliveries/verify`
- **Input:** `{ "delivery_id": "DEL-0001" }`
- **Acción:** Consulta DynamoDB y retorna estado de la entrega
- **Output:** JSON con `is_completed`, `status`, `tracking_number`

### Lambda 2 — Calcular ETA
- **Trigger:** EventBridge cada 5 minutos
- **Input:** `vehicle_id`, `current_location` (lat/lon), `destination`, `speed`
- **Acción:** Calcula distancia Haversine real y ETA; persiste en DynamoDB
- **Output:** `distance_remaining_km`, `eta`, `estimated_minutes`

### Lambda 3 — Alerta de Desvío
- **Trigger:** Kinesis Stream GPS (simulado)
- **Input:** `vehicle_id`, `route_id`, `current_location`
- **Acción:** Compara posición actual vs waypoints; si desvío > 5 km → SNS alert
- **Output:** `is_deviated`, `deviation_km`, `alert_sent`

### Lambda 4 — Procesar Webhook de Entrega
- **Trigger:** API Gateway `POST /delivery/webhook`
- **Input:** `delivery_id`, `status`, `driver_id`, `signature`
- **Acción:** Actualiza registro en DynamoDB
- **Output:** Confirmación de procesamiento

### Lambda 5 — Reporte Diario
- **Trigger:** EventBridge diario a las 06:00 AM
- **Input:** vacío (EventBridge cron)
- **Acción:** Consulta entregas del día anterior; calcula métricas; guarda JSON en S3
- **Output:** `total_deliveries`, `delivered`, `failed`, `success_rate`

---

## Servicios Mock Implementados

| Servicio | Clase Mock | Comportamiento |
|----------|-----------|----------------|
| DynamoDB | `MockDynamoDB` / `MockTable` | CRUD en memoria (dict) |
| SNS | `MockSNS` | Print a consola + lista de publicaciones |
| S3 | `MockS3` | Escribe archivos en `docs/evidencia_ejecucion/aws_simulation/` |
| CloudWatch | `MockCloudWatch` | Acumula métricas; genera gráfico matplotlib |

---

## Escenarios de Prueba

| # | Escenario | Lambda | Resultado esperado |
|---|-----------|--------|-------------------|
| 1 | Entrega DEL-0001 encontrada | 1 | HTTP 200, is_completed = true/false |
| 2 | Entrega DEL-9999 inexistente | 1 | HTTP 404 |
| 3 | ETA Bogotá → Medellín, 80 km/h | 2 | ~178 min, Haversine 238 km |
| 4 | ETA Cali → Barranquilla, 70 km/h | 2 | ~738 min, 861 km |
| 5 | Sin desvío (en waypoint) | 3 | is_deviated = false |
| 6 | Con desvío 99 km, SNS alert | 3 | is_deviated = true, SNS publicado |
| 7 | Webhook entrega exitosa | 4 | HTTP 200, DynamoDB actualizado |
| 8 | Reporte diario → S3 | 5 | JSON en `fleetlogix-reports/` |

---

## Requisitos

```
matplotlib>=3.8
numpy
pandas
```

> No requiere `boto3` ni credenciales AWS. 100% ejecutable en local.

---

*FleetLogix Enterprise · Dody Dueñas · Henry M2 · 2026*
