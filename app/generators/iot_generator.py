import random
import json
from datetime import datetime, timedelta
from typing import List, Dict

class IoTGenerator:
    """
    Generator for IoT sensor telemetery data (GPS, Speed, Fuel).
    Saves to JSON for MongoDB ingestion.
    """
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.iot_events = ['frenada_brusca', 'exceso_velocidad', 'operacion_normal', 'ralenti_prolongado']

    def generate(self, count: int = 10000, vehicle_ids: List[int] = []) -> List[dict]:
        """
        Generates IoT events for given vehicles.
        """
        telemetry_data = []
        if not vehicle_ids:
            vehicle_ids = range(1, 201) # Default 200 vehicles

        start_time = datetime.now() - timedelta(days=30)
        
        for i in range(count):
            v_id = random.choice(vehicle_ids)
            timestamp = start_time + timedelta(minutes=random.randint(0, 43200)) # Last 30 days
            
            # Simulated GPS for Colombia (approx)
            lat = random.uniform(4.0, 6.0)
            lon = random.uniform(-75.0, -73.0)
            
            event = {
                "sensor_id": f"SN-{random.randint(1000, 9999)}",
                "vehicle_id": v_id,
                "timestamp": timestamp.isoformat(),
                "location": {
                    "type": "Point",
                    "coordinates": [round(lon, 6), round(lat, 6)]
                },
                "metrics": {
                    "speed_kmh": round(random.uniform(0, 110), 2),
                    "fuel_level_pct": round(random.uniform(10, 100), 2),
                    "engine_temp_c": round(random.uniform(70, 105), 2),
                    "load_weight_kg": round(random.uniform(0, 5000), 2)
                },
                "event_type": random.choices(self.iot_events, weights=[0.05, 0.1, 0.8, 0.05])[0]
            }
            telemetry_data.append(event)
            
        return telemetry_data

    def save_to_json(self, data: List[dict], filename: str = "iot_telemetry.json"):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"IoT data saved to {filename}")

if __name__ == "__main__":
    gen = IoTGenerator()
    data = gen.generate(10000)
    gen.save_to_json(data)
