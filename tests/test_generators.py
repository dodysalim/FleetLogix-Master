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
