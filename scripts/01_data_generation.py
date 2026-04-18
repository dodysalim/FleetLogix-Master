"""
FleetLogix - Data Generation Module
===================================
Generates 505,000+ synthetic records maintaining business rules and referential integrity.

SOLID Principles Applied:
- Single Responsibility: Each generator class handles one entity
- Open/Closed: Easy to extend with new data types
- Liskov Substitution: All generators implement IDataGenerator interface
- Interface Segregation: Clean interfaces for each generator
- Dependency Inversion: Uses IDatabaseManager abstraction

Author: Dody Dueñas
Project: Henry M2 - FleetLogix Enterprise
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any, Optional
from abc import ABC, abstractmethod
import random
import numpy as np
import pandas as pd
from faker import Faker

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.postgres_manager import PostgresManager
from app.core.interfaces import IDataGenerator, IDatabaseManager


class DataGeneratorBase(ABC):
    """
    Abstract base class for all data generators.
    Implements Template Method pattern for common generation logic.
    """

    def __init__(self, seed: int = 42):
        self._fake = Faker("es_CO")
        self._fake.seed_instance(seed)
        random.seed(seed)
        np.random.seed(seed)
        self._logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def generate(self, count: int, **kwargs) -> List[Tuple]:
        """Generate synthetic data records"""
        pass

    def _log_progress(self, entity: str, count: int):
        self._logger.info(f"Generated {count} {entity} records")


class VehicleGenerator(DataGeneratorBase, IDataGenerator):
    """
    Vehicle Generator
    ================
    Generates vehicle records with realistic types, capacities, and license plates.

    Business Rules:
    - 90% active status, 10% maintenance
    - Capacity varies by vehicle type
    - Fuel type based on vehicle category

    Attributes:
        vehicle_types: List of (type, capacity_kg, fuel_type, weight)
    """

    VEHICLE_TYPES = [
        ("Camión Grande", 5000, "diesel", 0.25),
        ("Camión Mediano", 3000, "diesel", 0.25),
        ("Van", 1500, "gasolina", 0.25),
        ("Motocicleta", 50, "gasolina", 0.25),
    ]

    def __init__(self, seed: int = 42):
        super().__init__(seed)

    def generate(self, count: int, **kwargs) -> List[Tuple]:
        """Generate vehicle records"""
        vehicles = []

        for _ in range(count):
            v_type, capacity, fuel, _ = random.choices(
                self.VEHICLE_TYPES, weights=[vt[3] for vt in self.VEHICLE_TYPES]
            )[0]

            # Generate Colombian license plate
            license_plate = (
                f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
                f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
                f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
                f"{random.randint(100, 999)}"
            )

            # Acquisition date in last 5 years
            acquisition_date = self._fake.date_between(start_date="-5y", end_date="-1m")

            # Status distribution: 90% active, 10% maintenance
            status = random.choice(["active"] * 9 + ["maintenance"])

            vehicles.append(
                (license_plate, v_type, capacity, fuel, acquisition_date, status)
            )

        self._log_progress("vehicles", count)
        return vehicles


class DriverGenerator(DataGeneratorBase, IDataGenerator):
    """
    Driver Generator
    ================
    Generates driver records with Colombian license types and contact info.

    Business Rules:
    - 95% active status
    - License valid for 3 years with some near expiry
    - Colombian phone format (10 digits starting with 3)
    """

    LICENSE_TYPES = ["C1", "C2", "C3", "A2"]

    def __init__(self, seed: int = 42):
        super().__init__(seed)

    def generate(self, count: int, **kwargs) -> List[Tuple]:
        """Generate driver records"""
        drivers = []

        for i in range(count):
            employee_code = f"EMP{str(i + 1).zfill(5)}"
            first_name = self._fake.first_name()
            last_name = self._fake.last_name()

            # Colombian license number (10 digits)
            license_number = str(random.randint(1000000000, 9999999999))
            license_type = random.choice(self.LICENSE_TYPES)

            # License expiry: -1 month to +3 years
            license_expiry = self._fake.date_between(start_date="-1m", end_date="+3y")

            # Colombian cell phone (10 digits starting with 3)
            phone = f"3{random.randint(100000000, 999999999)}"

            # Hire date in last 5 years
            hire_date = self._fake.date_between(start_date="-5y", end_date="-1w")

            # 95% active
            status = random.choice(["active"] * 19 + ["inactive"])

            drivers.append(
                (
                    employee_code,
                    first_name,
                    last_name,
                    license_number,
                    license_expiry,
                    phone,
                    hire_date,
                    status,
                )
            )

        self._log_progress("drivers", count)
        return drivers


class RouteGenerator(DataGeneratorBase, IDataGenerator):
    """
    Route Generator
    ===============
    Generates routes between major Colombian cities.

    Cities:
    - Bogotá, Medellín, Cali, Barranquilla, Cartagena

    Business Rules:
    - Multiple routes between major cities
    - Distance based on real approximations
    - Duration based on 60-80 km/h average speed
    - Toll cost based on distance
    """

    CITIES = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena"]

    DISTANCES = {
        ("Bogotá", "Medellín"): 440,
        ("Bogotá", "Cali"): 460,
        ("Bogotá", "Barranquilla"): 1000,
        ("Bogotá", "Cartagena"): 1050,
        ("Medellín", "Cali"): 420,
        ("Medellín", "Barranquilla"): 640,
        ("Medellín", "Cartagena"): 640,
        ("Cali", "Barranquilla"): 1100,
        ("Cali", "Cartagena"): 1100,
        ("Barranquilla", "Cartagena"): 120,
    }

    def __init__(self, seed: int = 42):
        super().__init__(seed)

    def _get_distance(self, origin: str, destination: str) -> float:
        """Get approximate distance between cities"""
        key = tuple(sorted([origin, destination]))
        return self.DISTANCES.get(key, 500)

    def generate(self, count: int, **kwargs) -> List[Tuple]:
        """Generate route records"""
        routes = []
        route_counter = 1

        # Generate routes between all city combinations
        for origin in self.CITIES:
            for destination in self.CITIES:
                if origin == destination:
                    continue

                # More routes for Bogotá
                num_routes = 3 if origin == "Bogotá" or destination == "Bogotá" else 2

                for _ in range(num_routes):
                    if route_counter > count:
                        break

                    route_code = f"R{str(route_counter).zfill(3)}"

                    # Distance with variation
                    base_distance = self._get_distance(origin, destination)
                    distance = base_distance + random.uniform(-50, 50)

                    # Duration (60-80 km/h average)
                    avg_speed = random.uniform(60, 80)
                    duration = distance / avg_speed

                    # Toll cost (15k pesos per 100km)
                    toll_cost = int(distance / 100) * 15000

                    routes.append(
                        (
                            route_code,
                            origin,
                            destination,
                            round(distance, 2),
                            round(duration, 2),
                            toll_cost,
                        )
                    )

                    route_counter += 1

                if route_counter > count:
                    break

            if route_counter > count:
                break

        self._log_progress("routes", len(routes))
        return routes


class TripGenerator(DataGeneratorBase, IDataGenerator):
    """
    Trip Generator
    =============
    Generates trip records with realistic temporal distribution.

    Business Rules:
    - 95% completed status
    - Temporal distribution: more trips during business hours
    - Fuel consumption: 8-15 L/100km based on distance
    - Weight: 40-90% of vehicle capacity
    """

    def _get_hourly_distribution(self) -> np.ndarray:
        """Get probability distribution by hour of day"""
        probs = np.ones(24) * 0.02  # Base 2%
        probs[6:20] = 0.06  # 6am-8pm more activity
        probs[8:12] = 0.08  # 8am-12pm morning peak
        probs[14:18] = 0.07  # 2pm-6pm afternoon peak
        return probs / probs.sum()

    def generate(self, count: int, **kwargs) -> List[Tuple]:
        """Generate trip records"""
        vehicle_ids = kwargs.get("vehicle_ids", [])
        driver_ids = kwargs.get("driver_ids", [])
        routes = kwargs.get("routes", [])

        if not all([vehicle_ids, driver_ids, routes]):
            raise ValueError(
                "Missing required parameters: vehicle_ids, driver_ids, routes"
            )

        trips = []
        start_date = datetime.now() - timedelta(days=730)  # 2 years ago
        current_date = start_date

        for _ in range(count):
            vehicle_id, capacity = random.choice(vehicle_ids)
            capacity = float(capacity)
            driver_id = random.choice(driver_ids)
            route_id, distance, est_duration = random.choice(routes)

            distance = float(distance)
            est_duration = float(est_duration)

            # Hourly distribution
            hour = np.random.choice(range(24), p=self._get_hourly_distribution())
            departure = current_date.replace(hour=hour, minute=random.randint(0, 59))

            # Actual duration with variation
            actual_duration = est_duration * random.uniform(0.8, 1.3)
            arrival = departure + timedelta(hours=actual_duration)

            # Fuel consumption (8-15 L/100km)
            fuel_consumed = distance * random.uniform(0.08, 0.15)

            # Weight (40-90% of capacity)
            total_weight = capacity * random.uniform(0.4, 0.9)

            # Status (95% completed if arrival is in the past)
            if arrival < datetime.now():
                status = "completed"
            else:
                status = "in_progress"

            trips.append(
                (
                    vehicle_id,
                    driver_id,
                    route_id,
                    departure,
                    arrival if status == "completed" else None,
                    round(fuel_consumed, 2),
                    round(total_weight, 2),
                    status,
                )
            )

            # Advance date
            current_date += timedelta(minutes=int(1440 * 2 * 365 / count))

        self._log_progress("trips", count)
        return trips


class DeliveryGenerator(DataGeneratorBase, IDataGenerator):
    """
    Delivery Generator
    ==================
    Generates delivery records associated with trips.

    Business Rules:
    - 2-6 deliveries per trip (average 4)
    - 90% on-time delivery rate
    - 95% with recipient signature
    - Weight distributed exponentially
    """

    def _distribute_weight(self, total_weight: float, num_packages: int) -> np.ndarray:
        """Distribute total weight among packages"""
        weights = np.random.exponential(scale=1.0, size=num_packages)
        weights = weights / weights.sum() * total_weight * 0.95
        return np.maximum(weights, 0.5)

    def generate(self, count: int, **kwargs) -> List[Tuple]:
        """Generate delivery records"""
        trips_data = kwargs.get("trips_data", [])

        if not trips_data:
            raise ValueError("Missing required parameter: trips_data")

        deliveries = []
        delivery_counter = 0

        for trip_id, departure, arrival, total_weight, city in trips_data:
            if delivery_counter >= count:
                break

            # Number of deliveries per trip (2-6, average 4)
            num_deliveries = np.random.choice(
                [2, 3, 4, 5, 6], p=[0.1, 0.2, 0.4, 0.2, 0.1]
            )

            # Distribute weight
            weights = self._distribute_weight(float(total_weight), num_deliveries)

            # Time per delivery
            if arrival:
                delivery_duration = (arrival - departure).total_seconds() / 3600
                time_per_delivery = delivery_duration / num_deliveries
            else:
                time_per_delivery = 0.5

            for i in range(num_deliveries):
                if delivery_counter >= count:
                    break

                tracking_number = (
                    f"FL{datetime.now().year}{str(delivery_counter + 1).zfill(8)}"
                )
                customer_name = self._fake.name()
                delivery_address = f"{self._fake.street_address()}, {city}"
                package_weight = weights[i]

                # Scheduled time
                scheduled = departure + timedelta(hours=time_per_delivery * (i + 0.5))

                # Delivered time and status
                if arrival and random.random() < 0.9:
                    # 90% on-time
                    delivered = scheduled + timedelta(minutes=random.randint(-30, 30))
                    delivery_status = "delivered"
                    signature = random.random() < 0.95  # 95% with signature
                elif arrival:
                    # 10% delayed
                    delivered = scheduled + timedelta(minutes=random.randint(60, 180))
                    delivery_status = "delivered"
                    signature = random.random() < 0.95
                else:
                    delivered = None
                    delivery_status = "pending"
                    signature = False

                deliveries.append(
                    (
                        trip_id,
                        tracking_number,
                        customer_name,
                        delivery_address,
                        round(package_weight, 2),
                        scheduled,
                        delivered,
                        delivery_status,
                        signature,
                    )
                )

                delivery_counter += 1

        self._log_progress("deliveries", len(deliveries))
        return deliveries


class MaintenanceGenerator(DataGeneratorBase, IDataGenerator):
    """
    Maintenance Generator
    ====================
    Generates maintenance records based on vehicle usage.

    Business Rules:
    - ~1 maintenance per 20 trips
    - Cost with ±20% variation
    - Next maintenance based on type
    """

    MAINTENANCE_TYPES = [
        ("Cambio de aceite", 150000, 30),
        ("Revisión de frenos", 250000, 60),
        ("Cambio de llantas", 450000, 90),
        ("Mantenimiento general", 350000, 45),
        ("Revisión de motor", 500000, 60),
        ("Alineación y balanceo", 180000, 30),
    ]

    def generate(self, count: int, **kwargs) -> List[Tuple]:
        """Generate maintenance records"""
        vehicle_stats = kwargs.get("vehicle_stats", [])

        if not vehicle_stats:
            raise ValueError("Missing required parameter: vehicle_stats")

        maintenance_records = []

        for vehicle_id, trip_count, first_trip, last_trip in vehicle_stats:
            if len(maintenance_records) >= count:
                break

            # Number of maintenances (~1 per 20 trips)
            num_maintenance = max(1, trip_count // 20)

            if first_trip and last_trip:
                operation_days = (last_trip - first_trip).days

                for i in range(num_maintenance):
                    if len(maintenance_records) >= count:
                        break

                    days_offset = int(operation_days * (i + 1) / (num_maintenance + 1))
                    maintenance_date = (first_trip + timedelta(days=days_offset)).date()

                    m_type, base_cost, days_next = random.choice(self.MAINTENANCE_TYPES)

                    cost = base_cost * random.uniform(0.8, 1.2)
                    description = f"{m_type} programado para {maintenance_date}"
                    next_maintenance = maintenance_date + timedelta(days=days_next)
                    performed_by = f"{self._fake.first_name()} {self._fake.last_name()}"

                    maintenance_records.append(
                        (
                            vehicle_id,
                            maintenance_date,
                            m_type,
                            description,
                            round(cost, 2),
                            next_maintenance,
                            performed_by,
                        )
                    )

        self._log_progress("maintenance", len(maintenance_records))
        return maintenance_records


class ProjectIntegrator:
    """
    Project Integrator
    ==================
    Facade for the complete FleetLogix data generation pipeline.
    Manages generation order and database orchestration.

    This class follows the Facade pattern to simplify the complex
    subsystem of data generation.

    SOLID Principles:
    - Single Responsibility: Orchestrates the entire pipeline
    - Dependency Inversion: Uses IDatabaseManager abstraction
    """

    def __init__(self, db_manager: IDatabaseManager):
        self._db = db_manager
        self._logger = logging.getLogger(__name__)

    def run_pipeline(self, scale_factor: int = 1):
        """
        Execute the complete data generation pipeline.

        Args:
            scale_factor: Multiplier for record counts (1 = 505k+ records)
        """
        start_time = datetime.now()
        self._logger.info(f"Starting Data Generation Pipeline at {start_time}")

        try:
            self._db.connect()

            # Clean tables for a fresh execution
            self._logger.info("Cleaning existing data for a fresh start...")
            self._db.execute_query("TRUNCATE maintenance, deliveries, trips, routes, drivers, vehicles CASCADE")
            self._db.commit()

            # Define counts based on scale factor
            num_vehicles = 200 * scale_factor
            num_drivers = 400 * scale_factor
            num_routes = 50 * scale_factor
            num_trips = 100000 * scale_factor
            num_deliveries = 400000 * scale_factor
            num_maint = 5000 * scale_factor

            # Phase 1: Generate master tables
            self._logger.info(
                f"Phase 1: Generating master data (scale: {scale_factor}x)"
            )
            self._generate_master_tables(num_vehicles, num_drivers, num_routes)

            # Phase 2: Retrieve foreign key IDs
            self._logger.info("Phase 2: Retrieving foreign key IDs")
            vehicle_ids = self._db.execute_query(
                "SELECT vehicle_id, capacity_kg FROM vehicles WHERE status = 'active'"
            )
            driver_ids = [
                r[0]
                for r in self._db.execute_query(
                    "SELECT driver_id FROM drivers WHERE status = 'active'"
                )
            ]
            routes_list = self._db.execute_query(
                "SELECT route_id, distance_km, estimated_duration_hours FROM routes"
            )

            # Phase 3: Generate trips
            self._logger.info("Phase 3: Generating trip data")
            trips_data = TripGenerator().generate(
                num_trips,
                vehicle_ids=vehicle_ids,
                driver_ids=driver_ids,
                routes=routes_list,
            )
            self._db.execute_many(
                """INSERT INTO trips 
                   (vehicle_id, driver_id, route_id, departure_datetime, 
                    arrival_datetime, fuel_consumed_liters, total_weight_kg, status) 
                   VALUES %s""",
                trips_data,
            )
            self._db.commit()

            # Phase 4: Generate deliveries
            self._logger.info("Phase 4: Generating delivery data")
            trips_ref = self._db.execute_query("""
                SELECT t.trip_id, t.departure_datetime, t.arrival_datetime, 
                       t.total_weight_kg, r.destination_city 
                FROM trips t 
                JOIN routes r ON t.route_id = r.route_id
            """)
            deliveries_data = DeliveryGenerator().generate(
                num_deliveries, trips_data=trips_ref
            )
            self._db.execute_many(
                """INSERT INTO deliveries 
                   (trip_id, tracking_number, customer_name, delivery_address, 
                    package_weight_kg, scheduled_datetime, delivered_datetime, 
                    delivery_status, recipient_signature) 
                   VALUES %s""",
                deliveries_data,
            )
            self._db.commit()

            # Phase 5: Generate maintenance
            self._logger.info("Phase 5: Generating maintenance data")
            maint_v_ref = self._db.execute_query("""
                SELECT vehicle_id, COUNT(*), MIN(departure_datetime), MAX(arrival_datetime) 
                FROM trips 
                GROUP BY vehicle_id
                HAVING COUNT(*) > 0
            """)
            maint_data = MaintenanceGenerator().generate(
                num_maint, vehicle_stats=maint_v_ref
            )
            self._db.execute_many(
                """INSERT INTO maintenance 
                   (vehicle_id, maintenance_date, maintenance_type, description, 
                    cost, next_maintenance_date, performed_by) 
                   VALUES %s""",
                maint_data,
            )
            self._db.commit()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self._logger.info(
                f"Pipeline completed successfully in {duration:.2f} seconds"
            )

            return {
                "status": "success",
                "duration_seconds": duration,
                "records_generated": {
                    "vehicles": num_vehicles,
                    "drivers": num_drivers,
                    "routes": num_routes,
                    "trips": num_trips,
                    "deliveries": len(deliveries_data),
                    "maintenance": len(maint_data),
                },
            }

        except Exception as e:
            self._logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            raise
        finally:
            self._db.close()

    def _generate_master_tables(
        self, num_vehicles: int, num_drivers: int, num_routes: int
    ):
        """Generate master table data"""

        # Generate vehicles
        vehicles = VehicleGenerator().generate(num_vehicles)
        self._db.execute_many(
            """INSERT INTO vehicles 
               (license_plate, vehicle_type, capacity_kg, fuel_type, acquisition_date, status) 
               VALUES %s""",
            vehicles,
        )

        # Generate drivers
        drivers = DriverGenerator().generate(num_drivers)
        self._db.execute_many(
            """INSERT INTO drivers 
               (employee_code, first_name, last_name, license_number, license_expiry, 
                phone, hire_date, status) 
               VALUES %s""",
            drivers,
        )

        # Generate routes
        routes = RouteGenerator().generate(num_routes)
        self._db.execute_many(
            """INSERT INTO routes 
               (route_code, origin_city, destination_city, distance_km, 
                estimated_duration_hours, toll_cost) 
               VALUES %s""",
            routes,
        )

        self._db.commit()
        self._logger.info("Master tables generated successfully")


def main():
    """Main entry point for data generation"""
    from dotenv import load_dotenv

    load_dotenv()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("=" * 60)
    print("FleetLogix - Data Generation Pipeline")
    print("Author: Dody Dueñas")
    print("Project: Henry M2 - FleetLogix Enterprise")
    print("=" * 60)

    db = PostgresManager()
    integrator = ProjectIntegrator(db)

    # Execute with scale factor 1 (505,000+ records)
    result = integrator.run_pipeline(scale_factor=1)

    print("\n" + "=" * 60)
    print("Pipeline Execution Summary:")
    print(f"Status: {result['status']}")
    print(f"Duration: {result['duration_seconds']:.2f} seconds")
    print("\nRecords Generated:")
    for entity, count in result["records_generated"].items():
        print(f"  {entity}: {count:,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
