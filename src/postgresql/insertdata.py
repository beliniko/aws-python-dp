import psycopg2
from simulateAttributes.simulator import generate_client_payload

def insert_payload(payload: dict):
    conn = psycopg2.connect(
        host='postgres.cps0eg466pdz.eu-central-1.rds.amazonaws.com',
        dbname='postgres',
        user='postgres',
        password='J):wNEu#s5)o$R??:G(L*iL4H8P9',
        port=5432
    )

    cur = conn.cursor()

    insert_query = """
    INSERT INTO iot_clients (
        device_id, timestamp, temperature, battery_status, latitude, longitude, connection_status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    cur.execute(insert_query, (
        payload['deviceId'],
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
