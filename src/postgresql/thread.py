import time
from psycopg2.pool import SimpleConnectionPool
from concurrent.futures import ThreadPoolExecutor
from simulateAttributes.simulator import generate_client_payload
from collections import defaultdict
import os

# Dictionary to store latency buckets
latency_buckets = defaultdict(int)
total_latency = 0  # Variable to track total latency
device_count_processed = 0  # Variable to track the number of devices processed

# Initialize connection pool
db_host = 'postgres.cps0eg466pdz.eu-central-1.rds.amazonaws.com'
db_name = 'postgres'
db_user = 'postgres'
db_password = 'xxx'

connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=81,  # Adjust the max connections as needed
    host=db_host,
    dbname=db_name,
    user=db_user,
    password=db_password,
    port=5432
)

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

def simulate_device(device_id):
    """Simulates a single device sending data to PostgreSQL."""
    global total_latency, device_count_processed
    conn = None
    try:
        conn = connection_pool.getconn()  # Borrow a connection from the pool
        cur = conn.cursor()

        start_time = time.time()  # Start latency measurement

        payload = generate_client_payload(device_id)

        # Insert or update data in PostgreSQL
        cur.execute("""
            INSERT INTO iot_clients (device_id, timestamp, temperature, battery_status, latitude, longitude, connection_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (device_id) DO UPDATE SET
                timestamp = EXCLUDED.timestamp,
                temperature = EXCLUDED.temperature,
                battery_status = EXCLUDED.battery_status,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                connection_status = EXCLUDED.connection_status
        """, (
            device_id,
            payload['timestamp'],
            payload['temperature'],
            payload['batteryStatus'],
            payload['coordinates']['latitude'],
            payload['coordinates']['longitude'],
            payload['connectionStatus']
        ))

        conn.commit()
        cur.close()

        end_time = time.time()  # End latency measurement
        latency_ms = (end_time - start_time) * 1000
        latency_bucket = bucketize_latency(latency_ms)
        latency_buckets[latency_bucket] += 1

        # Update total latency and device count
        total_latency += latency_ms
        device_count_processed += 1

        print(f"✅ Device {device_id} data sent successfully in {latency_ms:.2f} ms.")
    except Exception as e:
        print(f"❌ Error for device {device_id}: {e}")
    finally:
        if conn:
            connection_pool.putconn(conn)  # Return the connection to the pool

def simulate_load(device_count):
    """Simulates multiple devices sending data concurrently."""
    with ThreadPoolExecutor(max_workers=81) as executor:
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
    try:
        start_time = time.time()
        simulate_load(81)
        end_time = time.time()
        print(f"🕒 Simulation completed in {end_time - start_time:.2f} seconds.")
    finally:
        if connection_pool:
            connection_pool.closeall()  # Close all connections in the pool
