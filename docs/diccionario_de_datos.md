# 📖 Dictionary of Data - FleetLogix Enterprise

This document describes the semantics and constraints of the relational model tables.

---

## 1. Table: `vehicles` (Asset Master)

| Column | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `vehicle_id` | SERIAL | Unique internal identifier. | PK, Auto-increment |
| `license_plate` | VARCHAR(20) | Vehicle license plate (Colombia: ABC123). | UNIQUE, NOT NULL |
| `vehicle_type` | VARCHAR(50) | Category: Camión Grande, Camión Mediano, Van, Motocicleta. | NOT NULL |
| `capacity_kg` | DECIMAL(10,2) | Maximum load capacity in Kg. | > 0 |
| `fuel_type` | VARCHAR(20) | Fuel type: diesel, gasolina, eléctrico. | NULL allowed |
| `acquisition_date` | DATE | Date of acquisition of the vehicle. | NULL allowed |
| `status` | VARCHAR(20) | Status: active, maintenance, retired. | DEFAULT 'active' |

---

## 2. Table: `drivers` (Human Resources)

| Column | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `driver_id` | SERIAL | Unique identifier. | PK, Auto-increment |
| `employee_code` | VARCHAR(20) | Employee payroll code (EMP00001). | UNIQUE, NOT NULL |
| `first_name` | VARCHAR(100) | Driver's first name. | NOT NULL |
| `last_name` | VARCHAR(100) | Driver's last name. | NOT NULL |
| `license_number` | VARCHAR(50) | Commercial driver's license number. | UNIQUE, NOT NULL |
| `license_expiry` | DATE | License expiration date. | NOT NULL |
| `phone` | VARCHAR(20) | Contact phone number. | NULL allowed |
| `hire_date` | DATE | Date of hire. | NOT NULL |
| `status` | VARCHAR(20) | Status: active, inactive. | DEFAULT 'active' |

---

## 3. Table: `routes` (Geography)

| Column | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `route_id` | SERIAL | Unique route identifier. | PK |
| `route_code` | VARCHAR(20) | Route code (R001). | UNIQUE, NOT NULL |
| `origin_city` | VARCHAR(100) | Origin city name. | NOT NULL |
| `destination_city` | VARCHAR(100) | Destination city name. | NOT NULL |
| `distance_km` | DECIMAL(10,2) | Distance in kilometers. | > 0 |
| `estimated_duration_hours` | DECIMAL(5,2) | Estimated duration in hours. | > 0 |
| `toll_cost` | DECIMAL(10,2) | Total toll cost for the route. | DEFAULT 0 |

---

## 4. Table: `trips` (Operational Header)

| Column | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `trip_id` | SERIAL | Trip identifier. | PK |
| `vehicle_id` | INTEGER | Link to the vehicle used. | FK (vehicles.vehicle_id) |
| `driver_id` | INTEGER | Link to the assigned driver. | FK (drivers.driver_id) |
| `route_id` | INTEGER | Route of the trip. | FK (routes.route_id) |
| `departure_datetime` | TIMESTAMP | Departure date and time. | NOT NULL |
| `arrival_datetime` | TIMESTAMP | Arrival date and time. | NULL allowed |
| `fuel_consumed_liters` | DECIMAL(10,2) | Actual fuel consumed in liters. | > 0 |
| `total_weight_kg` | DECIMAL(10,2) | Total weight of cargo in Kg. | > 0 |
| `status` | VARCHAR(20) | Status: in_progress, completed, cancelled. | DEFAULT 'in_progress' |

---

## 5. Table: `deliveries` (Cargo Detail)

| Column | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `delivery_id` | SERIAL | Individual delivery identifier. | PK |
| `trip_id` | INTEGER | Trip this delivery belongs to. | FK (trips.trip_id) |
| `tracking_number` | VARCHAR(50) | Public tracking number (FL2026000001). | UNIQUE, NOT NULL |
| `customer_name` | VARCHAR(200) | Customer name. | NOT NULL |
| `delivery_address` | TEXT | Delivery address. | NOT NULL |
| `package_weight_kg` | DECIMAL(10,2) | Package weight in Kg. | > 0 |
| `scheduled_datetime` | TIMESTAMP | Scheduled delivery date/time. | NULL allowed |
| `delivered_datetime` | TIMESTAMP | Actual delivery date/time. | NULL allowed |
| `delivery_status` | VARCHAR(20) | Status: pending, delivered, failed, cancelled. | DEFAULT 'pending' |
| `recipient_signature` | BOOLEAN | Whether signature was collected. | DEFAULT FALSE |

---

## 6. Table: `maintenance` (Maintenance Records)

| Column | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `maintenance_id` | SERIAL | Maintenance record identifier. | PK |
| `vehicle_id` | INTEGER | Vehicle that received maintenance. | FK (vehicles.vehicle_id) |
| `maintenance_date` | DATE | Date of maintenance. | NOT NULL |
| `maintenance_type` | VARCHAR(50) | Type: Cambio de aceite, Revisión de frenos, etc. | NOT NULL |
| `description` | TEXT | Maintenance description. | NULL allowed |
| `cost` | DECIMAL(10,2) | Maintenance cost. | > 0 |
| `next_maintenance_date` | DATE | Next scheduled maintenance. | NULL allowed |
| `performed_by` | VARCHAR(200) | Technician who performed maintenance. | NULL allowed |

---

## 7. Entity Relationships

```
vehicles (1) ──────< trips (N)
     │                   │
     │                   └< deliveries (N)
     │
     └< maintenance (N)

drivers (1) ──────< trips (N)

routes (1) ──────< trips (N)
```

---

## Technical Notes

- **`DECIMAL` data types** are used for money and weights to avoid floating-point rounding errors.
- **All tables include `NOT NULL`** on key fields to ensure data quality from the source.
- **Foreign keys** enforce referential integrity between entities.
- **Timestamps** are stored in UTC for consistency across time zones.

---

**Author:** Dody Dueñas  
**Project:** Henry M2 - FleetLogix Enterprise  
**Date:** April 2026
