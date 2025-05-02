import boto3
from decimal import Decimal
from simulateAttributes.simulator import generate_client_payload

def initialize_clients_in_dynamodb(client_count):
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')

    # Replace 'YourTableName' with the name of your DynamoDB table
    table = dynamodb.Table('test')

    try:
        # Initialize multiple clients with simulated attributes
        for client_id in range(1, client_count + 1):
            device_id = f'client_{client_id}'
            payload = generate_client_payload(device_id)

            # Convert float values to Decimal
            payload['temperature'] = Decimal(str(payload['temperature']))
            payload['batteryStatus'] = Decimal(str(payload['batteryStatus']))
            payload['coordinates']['latitude'] = Decimal(str(payload['coordinates']['latitude']))
            payload['coordinates']['longitude'] = Decimal(str(payload['coordinates']['longitude']))

            print(f"Inserting item: {payload}")  # Debugging log

            table.put_item(
                Item={
                    'DeviceID': f'client_{client_id}',
                    'timestamp': payload['timestamp'],
                    'temperature': payload['temperature'],
                    'batteryStatus': payload['batteryStatus'],
                    'latitude': payload['coordinates']['latitude'],
                    'longitude': payload['coordinates']['longitude'],
                    'connectionStatus': payload['connectionStatus']
                }
            )

        print(f"{client_count} clients initialized successfully.")  # Debugging log
        return {
            'statusCode': 200,
            'body': f'{client_count} clients initialized successfully with simulated data'
        }
    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging log
        return {
            'statusCode': 500,
            'body': f'Error initializing clients: {str(e)}'
        }

def update_all_clients_in_dynamodb():
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')

    # Replace 'YourTableName' with the name of your DynamoDB table
    table = dynamodb.Table('test')

    try:
        # Scan the table to get all items
        response = table.scan()
        items = response.get('Items', [])

        # Update each item with a new payload
        for item in items:
            device_id = item['DeviceID']
            payload = generate_client_payload(device_id)

            # Convert float values to Decimal
            payload['temperature'] = Decimal(str(payload['temperature']))
            payload['batteryStatus'] = Decimal(str(payload['batteryStatus']))
            payload['coordinates']['latitude'] = Decimal(str(payload['coordinates']['latitude']))
            payload['coordinates']['longitude'] = Decimal(str(payload['coordinates']['longitude']))

            print(f"Updating item: {device_id} with payload: {payload}")  # Debugging log

            table.update_item(
                Key={'DeviceID': device_id},
                UpdateExpression="""
                    SET #ts = :timestamp,
                        temperature = :temperature,
                        batteryStatus = :batteryStatus,
                        latitude = :latitude,
                        longitude = :longitude,
                        connectionStatus = :connectionStatus
                """,
                ExpressionAttributeNames={
                    '#ts': 'timestamp'
                },
                ExpressionAttributeValues={
                    ':timestamp': payload['timestamp'],
                    ':temperature': payload['temperature'],
                    ':batteryStatus': payload['batteryStatus'],
                    ':latitude': payload['coordinates']['latitude'],
                    ':longitude': payload['coordinates']['longitude'],
                    ':connectionStatus': payload['connectionStatus']
                }
            )

        print("✅ All clients updated successfully in DynamoDB.")
    except Exception as e:
        print(f"❌ Error updating clients in DynamoDB: {str(e)}")

if __name__ == "__main__":
    initialize_clients_in_dynamodb(10)
   #  update_all_clients_in_dynamodb()