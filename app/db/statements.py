"""Sentencias SQL del pipeline de generación (separadas de la orquestación)."""

TRUNCATE_ALL = "TRUNCATE maintenance, deliveries, trips, routes, drivers, vehicles CASCADE"

INSERT_VEHICLES = ("INSERT INTO vehicles (license_plate, vehicle_type, capacity_kg, fuel_type, acquisition_date, status) "
                   "VALUES %s")
INSERT_DRIVERS = ("INSERT INTO drivers (employee_code, first_name, last_name, license_number, license_expiry, phone, "
                  "hire_date, status) VALUES %s")
INSERT_ROUTES = ("INSERT INTO routes (route_code, origin_city, destination_city, distance_km, "
                 "estimated_duration_hours, toll_cost) VALUES %s")
INSERT_TRIPS = ("INSERT INTO trips (vehicle_id, driver_id, route_id, departure_datetime, arrival_datetime, "
                "fuel_consumed_liters, total_weight_kg, status) VALUES %s")
INSERT_DELIVERIES = ("INSERT INTO deliveries (trip_id, tracking_number, customer_name, delivery_address, "
                     "package_weight_kg, scheduled_datetime, delivered_datetime, delivery_status, recipient_signature) "
                     "VALUES %s")
INSERT_MAINTENANCE = ("INSERT INTO maintenance (vehicle_id, maintenance_date, maintenance_type, description, cost, "
                      "next_maintenance_date, performed_by) VALUES %s")

SELECT_ACTIVE_VEHICLES = "SELECT vehicle_id, capacity_kg FROM vehicles WHERE status = 'active'"
SELECT_ACTIVE_DRIVERS = "SELECT driver_id FROM drivers WHERE status = 'active'"
SELECT_ROUTES = "SELECT route_id, distance_km, estimated_duration_hours FROM routes"
SELECT_TRIPS_FOR_DELIVERIES = """
    SELECT t.trip_id, t.departure_datetime, t.arrival_datetime, t.total_weight_kg, r.destination_city
    FROM trips t JOIN routes r ON t.route_id = r.route_id
"""
SELECT_VEHICLE_TRIP_STATS = """
    SELECT vehicle_id, COUNT(*), MIN(departure_datetime), MAX(arrival_datetime)
    FROM trips GROUP BY vehicle_id HAVING COUNT(*) > 0
"""
