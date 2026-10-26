# 📊 Modelo Entidad-Relación (ER) - FleetLogix

Este diagrama representa la arquitectura relacional de la base de datos PostgreSQL, diseñada para soportar operaciones masivas de transporte y logística.

```mermaid
erDiagram
    VEHICLES ||--o{ TRIPS : "utilizado en"
    VEHICLES ||--o{ MAINTENANCE : "recibe"
    DRIVERS ||--o{ TRIPS : "opera"
    ROUTES ||--o{ TRIPS : "definida por"
    TRIPS ||--o{ DELIVERIES : "contiene"

    VEHICLES {
        int vehicle_id PK
        string license_plate UK
        string vehicle_type
        decimal capacity_kg
        string fuel_type
        date acquisition_date
        string status
    }

    DRIVERS {
        int driver_id PK
        string employee_code UK
        string first_name
        string last_name
        string license_number UK
        date license_expiry
        string phone
        date hire_date
        string status
    }

    ROUTES {
        int route_id PK
        string route_code UK
        string origin_city
        string destination_city
        decimal distance_km
        decimal estimated_duration_hours
        decimal toll_cost
    }

    TRIPS {
        int trip_id PK
        int vehicle_id FK
        int driver_id FK
        int route_id FK
        timestamp departure_datetime
        timestamp arrival_datetime
        decimal fuel_consumed_liters
        decimal total_weight_kg
        string status
    }

    DELIVERIES {
        int delivery_id PK
        int trip_id FK
        string tracking_number UK
        string customer_name
        text delivery_address
        decimal package_weight_kg
        timestamp scheduled_datetime
        timestamp delivered_datetime
        string delivery_status
        boolean recipient_signature
    }

    MAINTENANCE {
        int maintenance_id PK
        int vehicle_id FK
        date maintenance_date
        string maintenance_type
        text description
        decimal cost
        date next_maintenance_date
        string performed_by
    }
```

## 🔍 Análisis de Patrones de Negocio
1.  **Atomicidad de Entregas:** Una entrega no existe sin un viaje (`TRIPS`), lo que asegura la trazabilidad logística desde el origen hasta el punto final.
2.  **Optimización por Rutas:** La tabla `ROUTES` centraliza los costos fijos (peajes) y distancias, permitiendo calcular la rentabilidad proyectada antes de la ejecución del viaje.
3.  **Ciclo de Vida de Activos:** La relación `VEHICLES` -> `MAINTENANCE` permite un análisis preventivo de costos operativos vs. vida útil del vehículo.
4.  **Cumplimiento de SLA:** La marca de tiempo en `DELIVERIES` (`scheduled` vs `delivered`) es la métrica clave para el cálculo de bonificaciones a conductores y satisfacción del cliente.
