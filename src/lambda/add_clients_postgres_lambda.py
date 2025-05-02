import time
import psycopg2
from simulateAttributes.simulator import generate_client_payload
import os

def get_db_connection():
    try:
        conn_start = time.time()
        conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            port=5432
        )
        conn_end = time.time()
        print(f'🔌 Connection time: {(conn_end - conn_start) * 1000:.2f} ms')
        return conn
    except Exception as e:
        print(f"❌ Error connecting to DB: {str(e)}")
        raise

def lambda_handler(event, context):
    # Number of  Clients in the event (z. B. {"client_count": 50})
    client_count = int(event.get('client_count', 10))

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        start_time = time.time()

        for client_id in range(1, client_count + 1):
            device_id = f'client_{client_id}'
            payload = generate_client_payload(device_id)

            cur.execute("""
                INSERT INTO iot_clients (
                    device_id, timestamp, temperature,
                    battery_status, latitude, longitude, connection_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
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
        conn.close()

        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        print(f"✅ {client_count} clients inserted in {latency_ms:.2f} ms.")
        return {
            'statusCode': 200,
            'body': f'{client_count} clients inserted into PostgreSQL. Latency: {latency_ms:.2f} ms'
        }

    except Exception as e:
        print(f"❌ Error inserting clients: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error inserting clients: {str(e)}'
        }
