import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import uuid
from dotenv import load_dotenv

load_dotenv("x.env")

USE_MOCK = os.getenv("USE_MOCK_SENSOR", "true").lower() == "true"
if USE_MOCK:
    from mock_sensor import read as read_sensor
else:
    import Adafruit_DHT
    def read_sensor():
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
        return {"temperature": temperature, "humidity": humidity}

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))
DEVICE_ID     = os.getenv("DEVICE_ID", str(uuid.uuid4()))

from database.db import insert_metric


def main():
    while True:
        data = read_sensor()
        print("data readed")
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "device_id": DEVICE_ID,
            **data
        }
        print("payload created")

        try:
            insert_metric(payload)
            print("insert data successfully!")
        except Exception as e:
            print(f"Database error: {e}")

        print("sleep")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()