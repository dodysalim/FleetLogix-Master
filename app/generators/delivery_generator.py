import random
from typing import List, Dict
from datetime import timedelta, datetime, timezone
from app.core.interfaces import IDataGenerator

class DeliveryGenerator(IDataGenerator):
    """
    Generator for deliveries related to trips.
    """
    def __init__(self, seed: int = 42):
        self._seed = seed
        from faker import Faker
        self._fake = Faker('es_CO')
        self._fake.seed_instance(seed)
        random.seed(seed)

    def generate(self, count: int, **kwargs) -> List[tuple]:
        trips_data = kwargs.get('trips_data')
        
        if not trips_data:
            raise ValueError("Required 'trips_data' for generating deliveries is missing.")
            
        deliveries = []
        delivery_counter = 0
        
        for trip_id, departure, arrival, total_weight, city in trips_data:
            num_deliveries = np.random.choice([2, 3, 4, 5, 6], p=[0.1, 0.2, 0.4, 0.2, 0.1])
            
            # Distribute weight
            raw_weights = np.random.exponential(scale=1.0, size=num_deliveries)
            weights = (raw_weights / raw_weights.sum() * float(total_weight) * 0.95).clip(min=0.5)
            
            if arrival:
                duration = (arrival - departure).total_seconds() / 3600
                time_per_del = duration / num_deliveries
            else:
                time_per_del = 0.5

            for i in range(num_deliveries):
                tracking = f"FL{datetime.now().year}{str(delivery_counter+1).zfill(8)}"
                scheduled = departure + timedelta(hours=time_per_del * (i + 0.5))
                
                if arrival:
                    if random.random() < 0.9:
                        delivered = scheduled + timedelta(minutes=random.randint(-30, 30))
                    else:
                        delivered = scheduled + timedelta(minutes=random.randint(60, 180))
                    status = 'delivered'
                    signature = random.random() < 0.95
                else:
                    delivered = None
                    status = 'pending'
                    signature = False

                deliveries.append((
                    trip_id,
                    tracking,
                    self._fake.name(),
                    f"{self._fake.street_address()}, {city}",
                    round(weights[i], 2),
                    scheduled,
                    delivered,
                    status,
                    signature
                ))
                
                delivery_counter += 1
                if delivery_counter >= count: break
            if delivery_counter >= count: break
                
        return deliveries
