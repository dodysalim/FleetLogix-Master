import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, List
from app.core.interfaces import IDataGenerator

class TripGenerator(IDataGenerator):
    """
    Generator for trips with temporal distribution logic.
    """
    def __init__(self, seed: int = 42):
        self._seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def _get_hourly_distribution(self):
        probs = np.ones(24) * 0.02
        probs[6:20] = 0.06
        probs[8:12] = 0.08
        probs[14:18] = 0.07
        return probs / probs.sum()

    def generate(self, count: int, **kwargs) -> List[tuple]:
        vehicle_ids = kwargs.get('vehicle_ids')
        driver_ids = kwargs.get('driver_ids')
        routes = kwargs.get('routes')
        
        if not vehicle_ids or not driver_ids or not routes:
            raise ValueError("Required data for generating trips is missing.")
            
        trips = []
        start_date = datetime.now() - timedelta(days=730)
        current_date = start_date
        
        for i in range(count):
            vehicle_id, capacity = random.choice(vehicle_ids)
            driver_id = random.choice(driver_ids)
            route_id, distance, est_duration = random.choice(routes)
            
            hour = np.random.choice(range(24), p=self._get_hourly_distribution())
            departure = current_date.replace(hour=hour, minute=random.randint(0, 59))
            
            actual_duration = float(est_duration) * random.uniform(0.8, 1.3)
            arrival = departure + timedelta(hours=actual_duration)
            
            fuel_consumed = float(distance) * random.uniform(0.08, 0.15)
            total_weight = float(capacity) * random.uniform(0.4, 0.9)
            
            status = 'completed' if arrival < datetime.now() else 'in_progress'
            
            trips.append((
                vehicle_id,
                driver_id,
                route_id,
                departure,
                arrival if status == 'completed' else None,
                round(fuel_consumed, 2),
                round(total_weight, 2),
                status
            ))
            
            current_date += timedelta(minutes=int(1440 * 2 * 365 / count))
        return trips
