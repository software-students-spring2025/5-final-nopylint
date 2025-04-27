import sys, os, time, uuid
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))

load_dotenv("x.env")
USE_MOCK = True
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL"))
DEVICE_ID     = os.getenv("DEVICE_ID", str(uuid.uuid4()))

from web_app.database.db import insert_metric

if USE_MOCK:
    from raspberry_pi.mock_sensor import read as read_sensor
else:
    import serial

    PORT = os.getenv("SERIAL_PORT")
    BAUD = int(os.getenv("SERIAL_BAUDRATE"))
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)  

    ser.write(b"start\r\n")
    ack = ser.readline().decode("utf-8", errors="ignore").strip()
    print(f"Pi replied: {ack}") 

    def read_sensor():
        """
        Block until we get a line like "T=25.34C H=60.65%", then parse and return.
        """
        while True:
            raw = ser.readline().decode("utf-8", errors="ignore").strip()
            if raw.startswith("T="):
                # expected format: T=25.34C H=60.65%
                try:
                    # split into ["T=25.34C", "H=60.65%"]
                    t_part, h_part = raw.split()
                    temp = float(t_part[2:-1])       
                    hum  = float(h_part[2:-1])  
                    print(f"pi return {temp} {hum}")     
                    return {"temperature": temp, "humidity": hum}
                except Exception:
                    continue

def get_system_metrics():
    """
    Read one sample (mock or real), 
    assemble and return a payload dict ready for MongoDB.
    """
    data = read_sensor()
    payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "device_id": DEVICE_ID,
        **data
    }
    return payload

def main():
    try:
        while True:
            data = read_sensor()
            print(f"成功收集数据，数据为：temp={data['temperature']:.2f}, humidity={data['humidity']:.2f}")

            payload = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "device_id": DEVICE_ID,
                **data
            }

            try:
                insert_metric(payload)
                print("成功上传数据")
            except Exception as e:
                print(f"上传失败: {e}")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        # on Ctrl-C tell Pi to stop
        if not USE_MOCK:
            ser.write(b"stop\r\n")
            print("\nSent stop command to Pi. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
