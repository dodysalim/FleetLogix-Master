import random
from typing import List
from datetime import timedelta
from faker import Faker
from app.core.interfaces import IDataGenerator

class MaintenanceGenerator(IDataGenerator):
    """
    Generator for maintenance records.
    """
    def __init__(self, seed: int = 42):
        self._fake = Faker('es_CO')
        self._fake.seed_instance(seed)
        random.seed(seed)
        self._maintenance_types = [
            ('Cambio de aceite', 150000, 30),
            ('Revisión de frenos', 250000, 60),
            ('Cambio de llantas', 450000, 90),
            ('Mantenimiento general', 350000, 45),
            ('Revisión de motor', 500000, 60),
            ('Alineación y balanceo', 180000, 30)
        ]

    def generate(self, count: int, **kwargs) -> List[tuple]:
        vehicle_stats = kwargs.get('vehicle_stats')
        if not vehicle_stats:
            raise ValueError("Required 'vehicle_stats' for generating maintenance is missing.")
            
        maintenance_records = []
        
        for vehicle_id, trip_count, first_trip, last_trip in vehicle_stats:
            num_maintenance = max(1, trip_count // 20)
            
            if first_trip and last_trip:
                operation_days = (last_trip - first_trip).days
                
                for i in range(num_maintenance):
                    if len(maintenance_records) >= count: break
                    
                    days_offset = int(operation_days * (i + 1) / (num_maintenance + 1))
                    maint_date = (first_trip + timedelta(days=days_offset)).date()
                    
                    m_type, base_cost, days_next = random.choice(self._maintenance_types)
                    cost = base_cost * random.uniform(0.8, 1.2)
                    
                    maintenance_records.append((
                        vehicle_id,
                        maint_date,
                        m_type,
                        f"{m_type} programado para {maint_date}",
                        round(cost, 2),
                        maint_date + timedelta(days=days_next),
                        f"{self._fake.first_name()} {self._fake.last_name()}"
                    ))
            if len(maintenance_records) >= count: break
            
        return maintenance_records
