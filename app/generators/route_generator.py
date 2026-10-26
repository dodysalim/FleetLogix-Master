import random
from typing import List, Dict
from app.core.interfaces import IDataGenerator

class RouteGenerator(IDataGenerator):
    """
    Generator for route data using consistent distance matrix.
    """
    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)
        self._cities = ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena']
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

    def routes_per_pair(self, origin: str, destination: str) -> int:
        """Regla de negocio: más rutas alternativas cuando el par incluye a Bogotá."""
        return 3 if "Bogotá" in (origin, destination) else 2

    def generate(self, count: int, **kwargs) -> List[tuple]:
        routes = []
        pairs = [(o, d) for o in self._cities for d in self._cities if o != d]
        for origin, destination in pairs:
            for _ in range(self.routes_per_pair(origin, destination)):
                if len(routes) >= count:
                    return routes
                distance = self._get_distance(origin, destination) + self._rng.uniform(-50, 50)
                duration = distance / self._rng.uniform(60, 80)          # 60-80 km/h
                toll_cost = int(distance / 100) * 15000                  # 15.000 COP cada 100 km
                routes.append((f"R{len(routes) + 1:03d}", origin, destination,
                               round(distance, 2), round(duration, 2), toll_cost))
        return routes
