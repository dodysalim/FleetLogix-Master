import logging
from datetime import datetime
from typing import List, Dict
from app.db.postgres_manager import PostgresManager
from app.generators.vehicle_generator import VehicleGenerator
from app.generators.driver_generator import DriverGenerator
from app.generators.route_generator import RouteGenerator
from app.generators.customer_generator import CustomerGenerator
from app.generators.trip_generator import TripGenerator
from app.generators.delivery_generator import DeliveryGenerator

class ProjectIntegrator:
    """
    Facade for the FleetLogix Data Generation Pipeline.
    Manages generation order and database orchestration.
    """
    def __init__(self, db_manager: PostgresManager):
        self._db = db_manager
        self._logger = logging.getLogger(__name__)

    def run_pipeline(self, scale_factor: int = 1):
        start_time = datetime.now()
        self._logger.info(f"Starting Data Generation Pipeline at {start_time}")
        
        try:
            self._db.connect()
            
            # Counts (Match official 1x scale)
            num_vehicles = 200 * scale_factor
            num_drivers = 400 * scale_factor
            num_routes = 50 * scale_factor
            num_trips = 100000 * scale_factor
            num_deliveries = 400000 * scale_factor
            num_maint = 5000 * scale_factor

            # 1. Master Tables
            self._logger.info(f"Generating Master data for {scale_factor}x scale...")
            vehicles = VehicleGenerator().generate(num_vehicles)
            drivers = DriverGenerator().generate(num_drivers)
            routes = RouteGenerator().generate(num_routes)
            
            self._db.execute_many(
                "INSERT INTO vehicles (license_plate, vehicle_type, capacity_kg, fuel_type, acquisition_date, status) VALUES %s",
                vehicles
            )
            self._db.execute_many(
                "INSERT INTO drivers (employee_code, first_name, last_name, license_number, license_expiry, phone, hire_date, status) VALUES %s",
                drivers
            )
            self._db.execute_many(
                "INSERT INTO routes (route_code, origin_city, destination_city, distance_km, estimated_duration_hours, toll_cost) VALUES %s",
                routes
            )
            self._db.commit()
            
            # 2. Retrieval
            v_data = self._db.execute_query("SELECT vehicle_id, capacity_kg FROM vehicles WHERE status = 'active'")
            driver_ids = [r[0] for r in self._db.execute_query("SELECT driver_id FROM drivers WHERE status = 'active'")]
            routes_list = self._db.execute_query("SELECT route_id, distance_km, estimated_duration_hours FROM routes")
            
            # 3. Trips
            self._logger.info("Generating Trip data...")
            trips_data = TripGenerator().generate(num_trips, vehicle_ids=v_data, driver_ids=driver_ids, routes=routes_list)
            self._db.execute_many(
                "INSERT INTO trips (vehicle_id, driver_id, route_id, departure_datetime, arrival_datetime, fuel_consumed_liters, total_weight_kg, status) VALUES %s",
                trips_data
            )
            self._db.commit()
            
            # 4. Deliveries
            self._logger.info("Generating Delivery data...")
            trips_ref = self._db.execute_query("""
                SELECT t.trip_id, t.departure_datetime, t.arrival_datetime, t.total_weight_kg, r.destination_city 
                FROM trips t JOIN routes r ON t.route_id = r.route_id
            """)
            deliveries_data = DeliveryGenerator().generate(num_deliveries, trips_data=trips_ref)
            self._db.execute_many(
                "INSERT INTO deliveries (trip_id, tracking_number, customer_name, delivery_address, package_weight_kg, scheduled_datetime, delivered_datetime, delivery_status, recipient_signature) VALUES %s",
                deliveries_data
            )
            self._db.commit()

            # 5. Maintenance
            self._logger.info("Generating Maintenance data...")
            maint_v_ref = self._db.execute_query("""
                SELECT vehicle_id, COUNT(*), MIN(departure_datetime), MAX(arrival_datetime) 
                FROM trips GROUP BY vehicle_id
            """)
            from app.generators.maintenance_generator import MaintenanceGenerator
            maint_data = MaintenanceGenerator().generate(num_maint, vehicle_stats=maint_v_ref)
            self._db.execute_many(
                "INSERT INTO maintenance (vehicle_id, maintenance_date, maintenance_type, description, cost, next_maintenance_date, performed_by) VALUES %s",
                maint_data
            )
            self._db.commit()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self._logger.info(f"Pipeline completed successfully in {duration:.2f} seconds.")
            
        except Exception as e:
            self._logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            raise
        finally:
            self._db.close()
