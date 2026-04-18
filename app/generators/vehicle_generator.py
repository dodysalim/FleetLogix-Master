import random
from typing import List, Dict
from faker import Faker
from app.core.interfaces import IDataGenerator

class VehicleGenerator(IDataGenerator):
    """
    Generator for vehicle data using Faker.
    Follows Strategy Pattern.
    """
    def __init__(self, seed: int = 42):
        self._fake = Faker('es_CO')
        self._fake.seed_instance(seed)
        self._vehicle_types = [
            ('Camión Grande', 5000, 'diesel'),
            ('Camión Mediano', 3000, 'diesel'),
            ('Van', 1500, 'gasolina'),
            ('Motocicleta', 50, 'gasolina')
        ]

    def generate(self, count: int, **kwargs) -> List[tuple]:
        vehicles = []
        for _ in range(count):
            v_type, capacity, fuel = random.choice(self._vehicle_types)
            
            # Colombian Plate (ABC123)
            plate = f"{self._fake.random_uppercase_letter()}{self._fake.random_uppercase_letter()}{self._fake.random_uppercase_letter()}{random.randint(100,999)}"
            
            acquisition_date = self._fake.date_between(start_date="-5y", end_date="-1m")
            status = random.choice(['active'] * 9 + ['maintenance'])
            
            vehicles.append((
                plate,
                v_type,
                capacity,
                fuel,
                acquisition_date,
                status
            ))
        return vehicles
