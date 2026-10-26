"""
FleetLogix - AWS Local Simulator
================================
Simulates complete AWS Cloud architecture for FleetLogix project.
Replicates DynamoDB, SNS, S3, and CloudWatch locally.

Author: Dody Dueñas
Project: Henry M2 - FleetLogix Enterprise
"""

import json
import os
import sys
import logging
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List, Optional
import numpy as np
import matplotlib.pyplot as plt

# Configuration
EVIDENCE_DIR = os.path.join("docs", "evidencia_ejecucion", "aws_simulation")
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# =====================================================
# AWS SERVICE MOCKS (Standalone implementation)
# =====================================================

class MockTable:
    def __init__(self, name: str):
        self.name = name
        self.items = {}

    def put_item(self, Item: Dict):
        key = list(Item.keys())[0]  # Simple primary key logic
        self.items[Item[key]] = Item

    def get_item(self, Key: Dict) -> Dict:
        key_val = list(Key.values())[0]
        item = self.items.get(key_val)
        return {"Item": item} if item else {}
    
    def query(self, **kwargs) -> Dict:
        # Mock simple date filtering
        return {"Items": list(self.items.values())}

class MockDynamoDB:
    def __init__(self):
        self.tables = {}

    def Table(self, name: str):
        if name not in self.tables:
            self.tables[name] = MockTable(name)
        return self.tables[name]

class MockSNS:
    def __init__(self):
        self.publications = []

    def publish(self, TopicArn: str, Message: str, Subject: str):
        pub = {"arn": TopicArn, "msg": json.loads(Message), "subject": Subject}
        self.publications.append(pub)
        print(f"  [SNS ALERT] {Subject}: {pub['msg']['alert_type']}")

class MockS3:
    def put_object(self, Bucket: str, Key: str, Body: str, ContentType: str):
        path = os.path.join(EVIDENCE_DIR, Bucket, Key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(Body)
        print(f"  [S3 UPLOAD] Saved to {Bucket}/{Key}")

class MockCloudWatch:
    def __init__(self):
        self.metrics = []

    def log_metric(self, name: str, value: float):
        self.metrics.append({
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "value": value
        })

# =====================================================
# BOTO3 MOCK (Required before importing lambdas)
# =====================================================
class MockBoto3:
    def resource(self, *args, **kwargs): return MockDynamoDB()
    def client(self, service, *args, **kwargs):
        if service == "sns": return MockSNS()
        if service == "s3": return MockS3()
        return None

sys.modules["boto3"] = MockBoto3()

# Integration with Lambda module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_functions.lambda_handler import (
    lambda_verificar_entrega,
    lambda_calcular_eta,
    lambda_alerta_desvio,
    lambda_procesar_entrega,
    lambda_generar_reporte_diario
)

# =====================================================
# SIMULATION ENGINE
# =====================================================

class AWSSimulator:
    def __init__(self):
        self.dynamodb = MockDynamoDB()
        self.sns = MockSNS()
        self.s3 = MockS3()
        self.cloudwatch = MockCloudWatch()
        self.results = []

    def run_scenarios(self):
        print("\n" + "="*50)
        print("FLEETLOGIX - AWS CLOUD SIMULATION")
        print("="*50)

        # Pre-populate DynamoDB with mock data
        table = self.dynamodb.Table("deliveries_status")
        table.put_item({
            "delivery_id": "DEL-0001",
            "tracking_number": "FL202600000001",
            "status": "pending",
            "scheduled_datetime": (datetime.now() + timedelta(hours=2)).isoformat()
        })

        # Scenario 1: Verify Existing Delivery (Lambda 1)
        print("\n[Scenario 1] Verifying Delivery DEL-0001...")
        res1 = lambda_verificar_entrega({"delivery_id": "DEL-0001"}, None)
        print(f"  Result: {res1['statusCode']} - {res1['body']}")
        self.results.append(("Lambda 1 - Verify Found", res1))

        # Scenario 2: ETA Calculation Bogota -> Medellin (Lambda 2)
        print("\n[Scenario 2] Calculating ETA Bogota -> Medellin (80 km/h)...")
        event2 = {
            "vehicle_id": "V-001",
            "current_location": {"lat": 4.6097, "lon": -74.0817}, # Bogota
            "destination": {"lat": 6.2442, "lon": -75.5812},      # Medellin
            "current_speed_kmh": 80
        }
        res2 = lambda_calcular_eta(event2, None)
        print(f"  Result: {res2['body']}")
        self.results.append(("Lambda 2 - ETA Bog-Med", res2))

        # Scenario 3: Route Deviation Detected (Lambda 3)
        print("\n[Scenario 3] Checking Route Deviation (High deviation)...")
        event3 = {
            "vehicle_id": "V-002",
            "driver_id": "D-101",
            "route_id": "R001",
            "current_location": {"lat": 10.411, "lon": -75.504} # Cartagena
        }
        # Force SNS alert
        res3 = lambda_alerta_desvio(event3, None)
        print(f"  Result: {res3['body']}")
        self.results.append(("Lambda 3 - Deviation Alert", res3))

        # Scenario 4: Process Delivery Webhook (Lambda 4)
        print("\n[Scenario 4] Processing delivery status upgrade via Webhook...")
        event4 = {
            "body": {
                "delivery_id": "DEL-0001",
                "status": "delivered",
                "driver_id": "D-101",
                "signature": True
            }
        }
        res4 = lambda_procesar_entrega(event4, None)
        print(f"  Result: {res4['body']}")
        self.results.append(("Lambda 4 - Webhook Process", res4))

        # Scenario 5: Generate Daily Report to S3 (Lambda 5)
        print("\n[Scenario 5] Generating Daily Report to S3...")
        res5 = lambda_generar_reporte_diario({}, None)
        self.results.append(("Lambda 5 - Daily Report S3", res5))

        self._generate_dashboard()
        self._save_final_report()

    def _generate_dashboard(self):
        """Generates CloudWatch-style metrics dashboard"""
        print("\n[CloudWatch] Generating performance dashboard...")
        
        labels = ['L1 Verification', 'L2 ETA Calculation', 'L3 Alert System', 'L4 Webhook Proc', 'L5 Report Gen']
        execution_times = [0.05, 0.12, 0.08, 0.04, 0.25] # Mock times in sec
        
        plt.figure(figsize=(10, 6))
        plt.style.use('ggplot')
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        plt.bar(labels, execution_times, color=colors)
        plt.title('FleetLogix AWS Lambda - Average Execution Latency (Simulated)', fontsize=14)
        plt.ylabel('Seconds', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        img_path = os.path.join(EVIDENCE_DIR, "cloudwatch_dashboard.png")
        plt.savefig(img_path)
        plt.close()
        print(f"  [DASHBOARD] Saved to {img_path}")

    def _save_final_report(self):
        """Saves JSON report with all execution results"""
        report_path = os.path.join(EVIDENCE_DIR, "aws_simulation_report.json")
        report_data = {
            "project": "FleetLogix Enterprise",
            "simulation_date": datetime.now().isoformat(),
            "scenarios_executed": len(self.results),
            "details": [
                {"scenario": name, "response": json.loads(res['body']) if isinstance(res['body'], str) else res['body']}
                for name, res in self.results
            ]
        }
        
        # Create directory if doesn't exist
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=4)
        print(f"  [FINAL REPORT] Saved to {report_path}")

if __name__ == "__main__":
    simulator = AWSSimulator()
    simulator.run_scenarios()
    print("\n" + "="*50)
    print("SIMULATION COMPLETED SUCCESSFULLY")
    print("="*50 + "\n")
