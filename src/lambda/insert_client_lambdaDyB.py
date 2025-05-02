import boto3
import time
from decimal import Decimal
from simulateAttributes.simulator import generate_client_payload

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table('test')  # Replace with your actual table name

def lambda_handler(event, context):
    # Read client_count from event, default to 10
    client_count = int(event.get('client_count', 10))

    try:
        start_time = time.time()  # 🔹 Start latency measurement

        for client_id in range(1, client_count + 1):
            device_id = f'client_{client_id}'
            payload = generate_client_payload(device_id)

            # Convert float values to Decimal for DynamoDB
            payload['temperature'] = Decimal(str(payload['temperature']))
            payload['batteryStatus'] = Decimal(str(payload['batteryStatus']))
            payload['coordinates']['latitude'] = Decimal(str(payload['coordinates']['latitude']))
            payload['coordinates']['longitude'] = Decimal(str(payload['coordinates']['longitude']))

            table.put_item(
                Item={
                    'DeviceID': device_id,
                    'timestamp': payload['timestamp'],
                    'temperature': payload['temperature'],
                    'batteryStatus': payload['batteryStatus'],
                    'latitude': payload['coordinates']['latitude'],
                    'longitude': payload['coordinates']['longitude'],
                    'connectionStatus': payload['connectionStatus']
                }
            )

        end_time = time.time()  # 🔹 End latency measurement
        latency_ms = (end_time - start_time) * 1000

        print(f"✅ {client_count} clients initialized in {latency_ms:.2f} ms.")
        return {
            'statusCode': 200,
            'body': f'{client_count} clients initialized successfully. Latency: {latency_ms:.2f} ms'
        }

    except Exception as e:
        print(f"❌ Error initializing clients: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error initializing clients: {str(e)}'
        }
