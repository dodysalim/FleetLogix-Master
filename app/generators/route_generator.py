import random
from typing import List, Dict
from app.core.interfaces import IDataGenerator

class RouteGenerator(IDataGenerator):
    """
    Generator for route data using consistent distance matrix.
    """
    def __init__(self, seed: int = 42):
        self._cities = ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena']
        random.seed(seed)
        self._distances = {
            ('Bogotá', 'Medellín'): 440,
            ('Bogotá', 'Cali'): 460,
            ('Bogotá', 'Barranquilla'): 1000,
            ('Bogotá', 'Cartagena'): 1050,
            ('Medellín', 'Cali'): 420,
            ('Medellín', 'Barranquilla'): 640,
            ('Medellín', 'Cartagena'): 640,
            ('Cali', 'Barranquilla'): 1100,
            ('Cali', 'Cartagena'): 1100,
            ('Barranquilla', 'Cartagena'): 120
        }

    def _get_distance(self, origin, destination):
        key = tuple(sorted([origin, destination]))
        return self._distances.get(key, 500)

    def generate(self, count: int, **kwargs) -> List[tuple]:
        routes = []
        route_counter = 1
        for origin in self._cities:
            for destination in self._cities:
                if origin != destination:
                    route_code = f"R{str(route_counter).zfill(3)}"
                    distance = self._get_distance(origin, destination) + random.uniform(-50, 50)
                    avg_speed = random.uniform(60, 80)
                    duration = distance / avg_speed
                    toll_cost = int(distance / 100) * 15000
                    
                    routes.append((
                        route_code,
                        origin,
                        destination,
                        round(distance, 2),
                        round(duration, 2),
                        toll_cost
                    ))
                    route_counter += 1
                    if route_counter > count: break
            if route_counter > count: break
        return routes[:count]
