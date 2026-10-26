"""Fachada del pipeline de generación de datos sintéticos de FleetLogix.

Depende de abstracciones: `IDatabaseManager` para la base y `IDataGenerator` para cada entidad.
Los generadores se inyectan (por defecto, los de `app.generators`), así que se pueden
reemplazar en pruebas o para otra escala sin tocar la orquestación.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict

from app.core.interfaces import IDatabaseManager, IDataGenerator
from app.db import statements as sql
from app.generators.delivery_generator import DeliveryGenerator
from app.generators.driver_generator import DriverGenerator
from app.generators.maintenance_generator import MaintenanceGenerator
from app.generators.route_generator import RouteGenerator
from app.generators.trip_generator import TripGenerator
from app.generators.vehicle_generator import VehicleGenerator

DEFAULT_GENERATORS: Dict[str, Callable[[], IDataGenerator]] = {
    "vehicles": VehicleGenerator, "drivers": DriverGenerator, "routes": RouteGenerator,
    "trips": TripGenerator, "deliveries": DeliveryGenerator, "maintenance": MaintenanceGenerator,
}
BASE_COUNTS = {"vehicles": 200, "drivers": 400, "routes": 50, "trips": 100_000,
               "deliveries": 400_000, "maintenance": 5_000}


@dataclass
class PipelineResult:
    status: str
    duration_seconds: float
    records_generated: Dict[str, int] = field(default_factory=dict)

    def __getitem__(self, key):  # compatibilidad con el resultado en diccionario
        return getattr(self, key)


class ProjectIntegrator:
    def __init__(self, db_manager: IDatabaseManager,
                 generators: Dict[str, Callable[[], IDataGenerator]] = None):
        self._db = db_manager
        self._gen = {**DEFAULT_GENERATORS, **(generators or {})}
        self._logger = logging.getLogger(__name__)

    def _insert(self, statement: str, rows) -> int:
        self._db.execute_many(statement, rows)
        self._db.commit()
        return len(rows)

    def run_pipeline(self, scale_factor: int = 1, truncate: bool = True) -> PipelineResult:
        start = datetime.now()
        counts = {k: v * scale_factor for k, v in BASE_COUNTS.items()}
        generated = {}
        self._logger.info("Starting Data Generation Pipeline at %s (scale %sx)", start, scale_factor)
        try:
            self._db.connect()
            if truncate:
                self._db.execute_query(sql.TRUNCATE_ALL)
                self._db.commit()

            # 1. Tablas maestras
            generated["vehicles"] = self._insert(sql.INSERT_VEHICLES, self._gen["vehicles"]().generate(counts["vehicles"]))
            generated["drivers"] = self._insert(sql.INSERT_DRIVERS, self._gen["drivers"]().generate(counts["drivers"]))
            generated["routes"] = self._insert(sql.INSERT_ROUTES, self._gen["routes"]().generate(counts["routes"]))

            # 2. Viajes (claves foráneas desde la base)
            trips = self._gen["trips"]().generate(
                counts["trips"], vehicle_ids=self._db.execute_query(sql.SELECT_ACTIVE_VEHICLES),
                driver_ids=[r[0] for r in self._db.execute_query(sql.SELECT_ACTIVE_DRIVERS)],
                routes=self._db.execute_query(sql.SELECT_ROUTES))
            generated["trips"] = self._insert(sql.INSERT_TRIPS, trips)

            # 3. Entregas y 4. mantenimiento
            deliveries = self._gen["deliveries"]().generate(
                counts["deliveries"], trips_data=self._db.execute_query(sql.SELECT_TRIPS_FOR_DELIVERIES))
            generated["deliveries"] = self._insert(sql.INSERT_DELIVERIES, deliveries)
            maintenance = self._gen["maintenance"]().generate(
                counts["maintenance"], vehicle_stats=self._db.execute_query(sql.SELECT_VEHICLE_TRIP_STATS))
            generated["maintenance"] = self._insert(sql.INSERT_MAINTENANCE, maintenance)

            duration = (datetime.now() - start).total_seconds()
            self._logger.info("Pipeline completed successfully in %.2f seconds.", duration)
            return PipelineResult("success", duration, generated)
        except Exception:
            self._logger.error("Pipeline execution failed", exc_info=True)
            raise
        finally:
            self._db.close()
