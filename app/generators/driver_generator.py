import random
from typing import List, Dict
from faker import Faker
from app.core.interfaces import IDataGenerator

class DriverGenerator(IDataGenerator):
    """
    Generator for driver data with performance metrics and SCD implementation.
    """
    def __init__(self, seed: int = 42):
        self._fake = Faker('es_CO')
        self._fake.seed_instance(seed)
        self._license_types = ['C1', 'C2', 'C3', 'A2']
        self._used_emp_codes = set()
        self._used_license_numbers = set()

    def generate(self, count: int, **kwargs) -> List[tuple]:
        drivers = []
        for i in range(count):
            employee_code = f"EMP{str(i+1).zfill(4)}"
            
            while True:
                license_num = f"{random.randint(1000000000, 9999999999)}"
                if license_num not in self._used_license_numbers:
                    self._used_license_numbers.add(license_num)
                    break
            
            hire_date = self._fake.date_between(start_date="-5y", end_date="-1w")
            phone = f"3{random.randint(100000000, 999999999)}"
            
            drivers.append((
                employee_code,
                self._fake.first_name(),
                self._fake.last_name(),
                license_num,
                self._fake.date_between(start_date="-1m", end_date="+3y"),
                phone,
                hire_date,
                "active"
            ))
        return drivers
