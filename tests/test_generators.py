import random
from datetime import datetime, timedelta

import pytest

from app.generators.customer_generator import CustomerGenerator
from app.generators.vehicle_generator import VehicleGenerator
from app.generators.delivery_generator import DeliveryGenerator


@pytest.mark.parametrize('generator', [CustomerGenerator, VehicleGenerator])
def test_seed_reproduces_output_without_global_random_state(generator):
    random.seed(999)
    state = random.getstate()
    first = generator(seed=17).generate(8)
    assert random.getstate() == state
    assert first == generator(seed=17).generate(8)


def test_deliveries_use_valid_trip_keys_and_do_not_change_global_rng():
    departure = datetime(2025, 1, 1, 8)
    trip = (31, departure, departure + timedelta(hours=4), 300, 'Bogotá')
    state = random.getstate()
    deliveries = DeliveryGenerator(seed=42).generate(3, trips_data=[trip])
    assert random.getstate() == state
    assert 1 <= len(deliveries) <= 3
    assert all(row[0] == 31 and row[4] > 0 for row in deliveries)
    assert len({row[1] for row in deliveries}) == len(deliveries)


def test_deliveries_require_trips():
    with pytest.raises(ValueError):
        DeliveryGenerator().generate(1)


def test_routes_follow_business_rules():
    from app.generators.route_generator import RouteGenerator
    routes = RouteGenerator(seed=1).generate(50)
    assert len(routes) == 48                                # 20 pares: 8 con Bogotá ×3 + 12 ×2
    assert len({r[0] for r in routes}) == len(routes)
    bogota = [r for r in routes if "Bogotá" in (r[1], r[2])]
    assert len(bogota) == 24
    assert all(r[5] == int(r[3] / 100) * 15000 for r in routes)
    assert len(RouteGenerator().generate(5)) == 5


def test_drivers_mostly_active_with_unique_licenses():
    from app.generators.driver_generator import DriverGenerator
    drivers = DriverGenerator(seed=3).generate(400)
    active = sum(d[7] == "active" for d in drivers) / len(drivers)
    assert 0.9 < active < 1.0
    assert len({d[3] for d in drivers}) == len(drivers)


class FakeDB:
    """Base de datos en memoria que registra lo que el integrador ejecuta."""
    def __init__(self):
        self.inserted, self.queries = {}, []
    def connect(self): pass
    def close(self): pass
    def commit(self): pass
    def execute_many(self, query, rows): self.inserted[query.split()[2]] = len(rows)
    def execute_query(self, query, params=None):
        self.queries.append(query.strip().split()[0])
        if "FROM vehicles" in query: return [(1, 3000), (2, 1500)]
        if "FROM drivers" in query: return [(1,), (2,)]
        if "FROM routes" in query: return [(1, 440, 6.0)]
        if "JOIN routes" in query:
            d = datetime(2025, 1, 1, 8)
            return [(i, d, d + timedelta(hours=5), 1000, "Cali") for i in range(1, 4)]
        if "GROUP BY vehicle_id" in query:
            return [(1, 40, datetime(2025, 1, 1), datetime(2025, 6, 1))]
        return None


def test_integrator_orchestrates_with_injected_db():
    from app.core.integrator import ProjectIntegrator
    from app.generators.trip_generator import TripGenerator

    class FewTrips(TripGenerator):
        def generate(self, count, **kw):
            return super().generate(5, **kw)

    db = FakeDB()
    result = ProjectIntegrator(db, generators={"trips": FewTrips}).run_pipeline()
    assert result.status == "success" and result["status"] == "success"
    assert db.queries[0] == "TRUNCATE"
    assert db.inserted["vehicles"] == 200 and db.inserted["routes"] == 48 and db.inserted["trips"] == 5
    assert set(result.records_generated) == {"vehicles", "drivers", "routes", "trips", "deliveries", "maintenance"}
