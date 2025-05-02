import psycopg2
from datetime import datetime

def get_db_connection():
    # Connect to your postgresDB
    db_host = 'postgres.cps0eg466pdz.eu-central-1.rds.amazonaws.com'
    db_name = 'postgres'
    db_user = 'postgres'
    db_password = 'J):wNEu#s5)o$R??:G(L*iL4H8P9'

    try:
        conn = psycopg2.connect(
            host=db_host,
            dbname=db_name,
            user=db_user,
            password=db_password,
            port=5432
        )
        return conn
    except Exception as e:
        print(f"❌ Error connecting to the database: {str(e)}")
        raise

def insert_time_to_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO clients (time_stamp) VALUES (%s)", (datetime.now(),))
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Time inserted successfully")
    except Exception as e:
        print(f"❌ Error inserting time: {str(e)}")

from simulateAttributes.simulator import generate_client_payload
from postgresql.insertdata import insert_payload

def initialize_clients_in_postgresql(client_count):

    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert simulated data for each client
        for client_id in range(1, client_count + 1):
            device_id = f'client_{client_id}'
            payload = generate_client_payload(device_id)

            cur.execute(
                """
                INSERT INTO iot_clients (device_id, timestamp, temperature, battery_status, latitude, longitude, connection_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    payload['deviceId'],
                    payload['timestamp'],
                    payload['temperature'],
                    payload['batteryStatus'],
                    payload['coordinates']['latitude'],
                    payload['coordinates']['longitude'],
                    payload['connectionStatus']
                )
            )

        # Commit the transaction
        conn.commit()
        cur.close()
        conn.close()

        print(f"{client_count} clients initialized successfully in PostgreSQL.")
    except Exception as e:
        print(f"❌ Error initializing clients in PostgreSQL: {str(e)}")

def update_all_clients():
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch all device IDs
        cur.execute("SELECT device_id FROM iot_clients")
        device_ids = cur.fetchall()

        # Update each client with a new payload
        for (device_id,) in device_ids:
            payload = generate_client_payload(device_id)

            cur.execute(
                """
                UPDATE iot_clients
                SET timestamp = %s,
                    temperature = %s,
                    battery_status = %s,
                    latitude = %s,
                    longitude = %s,
                    connection_status = %s
                WHERE device_id = %s
                """,
                (
                    payload['timestamp'],
                    payload['temperature'],
                    payload['batteryStatus'],
                    payload['coordinates']['latitude'],
                    payload['coordinates']['longitude'],
                    payload['connectionStatus'],
                    device_id
                )
            )

        # Commit the transaction
        conn.commit()
        cur.close()
        conn.close()

        print("✅ All clients updated successfully.")
    except Exception as e:
        print(f"❌ Error updating clients: {str(e)}")


if __name__ == "__main__":
    initialize_clients_in_postgresql(200)
  #  update_all_clients()