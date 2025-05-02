import math
import random
from datetime import datetime, timezone

def generate_temperature():
    # Get the current hour of the day (0-23)
    current_hour = datetime.now().hour

    if 12 <= current_hour <= 18:
        # Daytime: temperature range 18 to 25
        base_temperature = 21.5 + 3.5 * math.sin((current_hour - 12) / 6 * math.pi)
    else:
        # Nighttime: temperature range 8 to 17
        base_temperature = 12.5 + 4.5 * math.sin((current_hour - 19) / 16 * math.pi)

    # Add a random fluctuation of ±2 degrees
    fluctuation = random.uniform(-2.0, 2.0)

    return round(base_temperature + fluctuation, 2)


def generate_battery_status():
    return round(random.uniform(75.0, 100.0), 2)

def generate_coordinates():
    # Coordinates for Berlin (latitude: ~52.52, longitude: ~13.40)
    latitude = round(random.uniform(52.50, 52.53), 6)
    longitude = round(random.uniform(13.37, 13.42), 6)
    return {"latitude": latitude, "longitude": longitude}

def generate_connection_status():
    return random.choices(
        ["online", "offline", "sleeping", "disconnected"],
        weights=[70, 5, 20, 5],
        k=1
    )[0]

def generate_timestamp():
    return datetime.now(timezone.utc).isoformat()

def generate_client_payload(device_id: str):
    return {
        "deviceId": device_id,
        "timestamp": generate_timestamp(),
        "temperature": generate_temperature(),
        "batteryStatus": generate_battery_status(),
        "coordinates": generate_coordinates(),
        "connectionStatus": generate_connection_status()
    }

if __name__ == "__main__":
    # Example usage
    device_id = "device_12345"
    payload = generate_client_payload(device_id)
    print(payload)