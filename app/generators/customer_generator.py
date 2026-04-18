import random
from typing import List, Dict
from faker import Faker
from app.core.interfaces import IDataGenerator

class CustomerGenerator(IDataGenerator):
    """
    Generator for customer dimension using categorization logic.
    """
    def __init__(self, seed: int = 42):
        self._fake = Faker('es_ES')
        self._fake.seed_instance(seed)
        self._customer_types = ['Individual', 'Empresa', 'Gobierno']
        self._cities = ["Buenos Aires", "Rosario", "Córdoba", "Mendoza", "La Plata"]

    def generate(self, count: int, **kwargs) -> List[tuple]:
        customers = []
        for _ in range(count):
            customer_type = random.choice(self._customer_types)
            total_deliveries = random.randint(1, 1000)
            
            # Deterministic category logic
            if total_deliveries > 200:
                category = 'Premium'
            elif total_deliveries > 50:
                category = 'Regular'
            else:
                category = 'Ocasional'
            
            customers.append((
                self._fake.company() if customer_type != 'Individual' else self._fake.name(),
                customer_type,
                random.choice(self._cities),
                category,
                self._fake.date_between(start_date='-5y', end_date='today'),
                total_deliveries
            ))
        return customers
