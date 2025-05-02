import boto3
import time
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
from simulateAttributes.simulator import generate_client_payload
from collections import defaultdict
from botocore.config import Config

# Configure the connection pool size
config = Config(
    region_name='eu-central-1',
    max_pool_connections=100  # Increase the pool size as needed
)

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', config=config)
table = dynamodb.Table('test')  # Replace with your DynamoDB table name

# Dictionary to store latency buckets
latency_buckets = defaultdict(int)
total_latency = 0  # Variable to track total latency
device_count_processed = 0  # Variable to track the number of devices processed

def bucketize_latency(latency_ms):
    """Categorize latency into buckets."""
    if latency_ms < 50:
        return "<50ms"
    elif latency_ms < 100:
        return "50-100ms"
    elif latency_ms < 200:
        return "100-200ms"
    elif latency_ms < 500:
        return "200-500ms"
    else:
        return ">=500ms"

def warm_up(device_count):
    """Warm-up phase to establish connections or perform initial setup."""
    with ThreadPoolExecutor(max_workers=device_count) as executor:
        device_ids = [f'client_{i}' for i in range(1, device_count + 1)]
        executor.map(lambda device_id: simulate_device(device_id, warm_up=True), device_ids)
    print("✅ Warm-up phase completed.")

def simulate_device(device_id, warm_up=False):
    """Simulates a single device sending data to DynamoDB."""
    global total_latency, device_count_processed
    try:
        if not warm_up:
            start_time = time.time()  # Start latency measurement

        payload = generate_client_payload(device_id)

        # Convert float values to Decimal for DynamoDB
        payload['temperature'] = Decimal(str(payload['temperature']))
        payload['batteryStatus'] = Decimal(str(payload['batteryStatus']))
        payload['coordinates']['latitude'] = Decimal(str(payload['coordinates']['latitude']))
        payload['coordinates']['longitude'] = Decimal(str(payload['coordinates']['longitude']))

        # Send data to DynamoDB
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

        if not warm_up:
            end_time = time.time()  # End latency measurement
            latency_ms = (end_time - start_time) * 1000
            latency_bucket = bucketize_latency(latency_ms)
            latency_buckets[latency_bucket] += 1

            # Update total latency and device count
            total_latency += latency_ms
            device_count_processed += 1

            print(f"✅ Device {device_id} data sent successfully in {latency_ms:.2f} ms.")
        else:
            print(f"🌐 Warm-up for device {device_id} completed.")
    except Exception as e:
        print(f"❌ Error for device {device_id}: {e}")

def simulate_load(device_count):
    """Simulates multiple devices sending data concurrently."""
    warm_up(device_count)  # Perform warm-up phase

    with ThreadPoolExecutor(max_workers=device_count) as executor:
        device_ids = [f'client_{i}' for i in range(1, device_count + 1)]
        executor.map(simulate_device, device_ids)

    # Print latency distribution
    print("\nLatency Distribution:")
    for bucket, count in sorted(latency_buckets.items()):
        print(f"{bucket}: {count} devices")

    # Compute and print average latency
    if device_count_processed > 0:
        average_latency = total_latency / device_count_processed
        print(f"\n📊 Average Latency: {average_latency:.2f} ms")

if __name__ == "__main__":
    start_time = time.time()
    simulate_load(10)
    end_time = time.time()
    print(f"🕒 Simulation completed in {end_time - start_time:.2f} seconds.")