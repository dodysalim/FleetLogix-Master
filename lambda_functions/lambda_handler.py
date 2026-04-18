"""
FleetLogix - AWS Lambda Functions Module
=======================================
Professional AWS Lambda functions for real-time processing.

Features:
- Delivery verification
- ETA calculation
- Route deviation alerts
- Integration with DynamoDB, SNS, S3

SOLID Principles Applied:
- Single Responsibility: Each function handles one feature
- Open/Closed: Easy to extend with new features
- Dependency Inversion: Uses AWS SDK abstractions

Author: Dody Dueñas
Project: Henry M2 - FleetLogix Enterprise
"""

import json
import os
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional

import boto3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS Clients
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")
s3 = boto3.client("s3")

# Table names from environment
DELIVERIES_TABLE = os.environ.get("DELIVERIES_TABLE", "deliveries_status")
VEHICLE_TABLE = os.environ.get("VEHICLE_TABLE", "vehicle_tracking")
ROUTES_TABLE = os.environ.get("ROUTES_TABLE", "routes_waypoints")
ALERTS_TABLE = os.environ.get("ALERTS_TABLE", "alerts_history")
SNS_TOPIC_ARN = os.environ.get(
    "SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:123456789012:fleetlogix-alerts"
)


# =====================================================
# LAMBDA 1: Verify Delivery Status
# =====================================================
def lambda_verificar_entrega(event: Dict, context) -> Dict[str, Any]:
    """
    Verifies if a delivery was completed by checking DynamoDB.

    Trigger: API Gateway POST /deliveries/verify

    Args:
        event: Contains delivery_id and tracking_number
        context: Lambda context

    Returns:
        JSON response with delivery status
    """

    # Extract data from event
    delivery_id = event.get("delivery_id")
    tracking_number = event.get("tracking_number")

    # Validate required fields
    if not delivery_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "delivery_id is required"}),
        }

    # Connect to DynamoDB table
    table = dynamodb.Table(DELIVERIES_TABLE)

    try:
        # Fetch delivery
        response = table.get_item(Key={"delivery_id": delivery_id})

        if "Item" in response:
            item = response["Item"]
            is_completed = item.get("status") == "delivered"

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "delivery_id": delivery_id,
                        "tracking_number": item.get("tracking_number"),
                        "is_completed": is_completed,
                        "status": item.get("status"),
                        "delivered_datetime": str(item.get("delivered_datetime", "")),
                    }
                ),
            }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps(
                    {"error": "Delivery not found", "delivery_id": delivery_id}
                ),
            }

    except Exception as e:
        logger.error(f"Error verifying delivery: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# =====================================================
# LAMBDA 2: Calculate Estimated Time of Arrival (ETA)
# =====================================================
def lambda_calcular_eta(event: Dict, context) -> Dict[str, Any]:
    """
    Calculates ETA based on current location and destination.

    Trigger: EventBridge every 5 minutes

    Args:
        event: Contains vehicle_id, current_location, destination, current_speed_kmh
        context: Lambda context

    Returns:
        JSON response with ETA and distance
    """

    # Extract data from event
    vehicle_id = event.get("vehicle_id")
    current_location = event.get("current_location")  # {'lat': float, 'lon': float}
    destination = event.get("destination")  # {'lat': float, 'lon': float}
    current_speed_kmh = event.get("current_speed_kmh", 60)

    # Validate required fields
    if not all([vehicle_id, current_location, destination]):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required parameters"}),
        }

    try:
        # Calculate simple distance (Haversine approximation)
        lat_diff = abs(destination["lat"] - current_location["lat"])
        lon_diff = abs(destination["lon"] - current_location["lon"])

        # Approximation: 111 km per degree
        distance_km = ((lat_diff**2 + lon_diff**2) ** 0.5) * 111

        # Calculate time
        if current_speed_kmh > 0:
            hours = distance_km / current_speed_kmh
            eta = datetime.now() + timedelta(hours=hours)
        else:
            eta = None

        # Save to DynamoDB
        table = dynamodb.Table(VEHICLE_TABLE)
        table.put_item(
            Item={
                "vehicle_id": vehicle_id,
                "timestamp": datetime.now().isoformat(),
                "current_location": current_location,
                "destination": destination,
                "distance_remaining_km": Decimal(str(round(distance_km, 2))),
                "eta": eta.isoformat() if eta else None,
                "current_speed_kmh": Decimal(str(current_speed_kmh)),
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "vehicle_id": vehicle_id,
                    "distance_remaining_km": round(distance_km, 2),
                    "eta": eta.isoformat() if eta else "Not available",
                    "estimated_minutes": round(hours * 60) if eta else None,
                }
            ),
        }

    except Exception as e:
        logger.error(f"Error calculating ETA: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# =====================================================
# LAMBDA 3: Route Deviation Alert
# =====================================================
def lambda_alerta_desvio(event: Dict, context) -> Dict[str, Any]:
    """
    Detects route deviations and sends alerts via SNS.

    Trigger: Kinesis Stream from GPS

    Args:
        event: Contains vehicle_id, current_location, route_id, driver_id
        context: Lambda context

    Returns:
        JSON response with deviation status
    """

    # Extract data from event
    vehicle_id = event.get("vehicle_id")
    current_location = event.get("current_location")  # {'lat': float, 'lon': float}
    route_id = event.get("route_id")
    driver_id = event.get("driver_id")

    # Validate required fields
    if not all([vehicle_id, current_location, route_id]):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required parameters"}),
        }

    try:
        # Get expected route from DynamoDB
        table = dynamodb.Table(ROUTES_TABLE)
        response = table.get_item(Key={"route_id": route_id})

        if "Item" not in response:
            return {"statusCode": 404, "body": json.dumps({"error": "Route not found"})}

        waypoints = response["Item"].get("waypoints", [])

        # Calculate minimum distance to route
        min_distance = float("inf")
        for waypoint in waypoints:
            lat_diff = abs(waypoint["lat"] - current_location["lat"])
            lon_diff = abs(waypoint["lon"] - current_location["lon"])
            distance = ((lat_diff**2 + lon_diff**2) ** 0.5) * 111  # km
            min_distance = min(min_distance, distance)

        # Deviation threshold: 5 km
        DEVIATION_THRESHOLD_KM = 5
        is_deviated = min_distance > DEVIATION_THRESHOLD_KM

        if is_deviated:
            # Send SNS alert
            message = {
                "vehicle_id": vehicle_id,
                "driver_id": driver_id,
                "route_id": route_id,
                "deviation_km": round(min_distance, 2),
                "current_location": current_location,
                "timestamp": datetime.now().isoformat(),
                "alert_type": "ROUTE_DEVIATION",
            }

            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=json.dumps(message),
                Subject="Alert: Route Deviation Detected",
            )

            # Save alert to DynamoDB
            alerts_table = dynamodb.Table(ALERTS_TABLE)
            alerts_table.put_item(Item=message)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "vehicle_id": vehicle_id,
                    "is_deviated": is_deviated,
                    "deviation_km": round(min_distance, 2),
                    "alert_sent": is_deviated,
                    "threshold_km": DEVIATION_THRESHOLD_KM,
                }
            ),
        }

    except Exception as e:
        logger.error(f"Error checking deviation: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# =====================================================
# LAMBDA 4: Process Delivery Webhook
# =====================================================
def lambda_procesar_entrega(event: Dict, context) -> Dict[str, Any]:
    """
    Processes delivery webhook from mobile app.

    Trigger: API Gateway POST /delivery/webhook

    Args:
        event: Contains delivery data from mobile app
        context: Lambda context

    Returns:
        JSON response confirming delivery processing
    """

    # Extract delivery data
    delivery_data = event.get("body", {})

    required_fields = ["delivery_id", "status", "driver_id"]
    for field in required_fields:
        if field not in delivery_data:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Missing required field: {field}"}),
            }

    table = dynamodb.Table(DELIVERIES_TABLE)

    try:
        # Update delivery status
        item = {
            "delivery_id": delivery_data["delivery_id"],
            "status": delivery_data["status"],
            "driver_id": delivery_data["driver_id"],
            "updated_at": datetime.now().isoformat(),
        }

        if delivery_data.get("status") == "delivered":
            item["delivered_datetime"] = datetime.now().isoformat()
            item["recipient_signature"] = delivery_data.get("signature", False)

        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Delivery processed successfully",
                    "delivery_id": delivery_data["delivery_id"],
                }
            ),
        }

    except Exception as e:
        logger.error(f"Error processing delivery: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# =====================================================
# LAMBDA 5: Generate Daily Report
# =====================================================
def lambda_generar_reporte_diario(event: Dict, context) -> Dict[str, Any]:
    """
    Generates daily delivery report and saves to S3.

    Trigger: EventBridge daily at 6 AM

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        JSON response with report status
    """

    try:
        # Query deliveries from DynamoDB
        table = dynamodb.Table(DELIVERIES_TABLE)

        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        response = table.query(
            KeyConditionExpression="begins_with(timestamp, :date)",
            ExpressionAttributeValues={":date": yesterday},
        )

        deliveries = response.get("Items", [])

        # Calculate metrics
        total = len(deliveries)
        delivered = sum(1 for d in deliveries if d.get("status") == "delivered")
        failed = sum(1 for d in deliveries if d.get("status") == "failed")

        report = {
            "date": yesterday,
            "total_deliveries": total,
            "delivered": delivered,
            "failed": failed,
            "success_rate": round(100.0 * delivered / total, 2) if total > 0 else 0,
            "generated_at": datetime.now().isoformat(),
        }

        # Save to S3
        bucket = os.environ.get("REPORTS_BUCKET", "fleetlogix-reports")
        key = f"daily-reports/{yesterday}.json"

        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(report),
            ContentType="application/json",
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Daily report generated", "report": report}),
        }

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# =====================================================
# AWS CONFIGURATION REFERENCE
# =====================================================
"""
AWS CONFIGURATION:

1. Lambda Functions - Verify Delivery:
   - Trigger: API Gateway POST /deliveries/verify
   - Execution: Every time mobile app marks delivery

2. Lambda Functions - Calculate ETA:
   - Trigger: EventBridge every 5 minutes
   - Processing: All vehicles on route

3. Lambda Functions - Route Deviation Alert:
   - Trigger: Kinesis Stream from GPS
   - Execution: With each location update

4. Lambda Functions - Process Delivery Webhook:
   - Trigger: API Gateway POST /delivery/webhook
   - Execution: Mobile app delivery completion

5. Lambda Functions - Generate Daily Report:
   - Trigger: EventBridge daily at 6 AM
   - Execution: Once per day

REQUIRED IAM PERMISSIONS:
- dynamodb:GetItem
- dynamodb:PutItem
- dynamodb:Query
- sns:Publish
- s3:PutObject
"""


def handler(event, context):
    """Main handler for Lambda"""
    return {"statusCode": 400, "body": json.dumps({"error": "Invalid trigger"})}
