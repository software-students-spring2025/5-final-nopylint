import os
import time
from dotenv import load_dotenv

load_dotenv("x.env")

USE_MOCK     = False
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL"))
SERIAL_PORT   = os.getenv("SERIAL_PORT")
BAUDRATE      = int(os.getenv("SERIAL_BAUDRATE"))

if USE_MOCK:
    print(f'using mock sensor because {USE_MOCK}')
    from raspberry_pi.mock_sensor import read as read_sensor
else:
    import serial

    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    time.sleep(2)  

    ser.write(b"start\r\n")
    ack = ser.readline().decode("utf-8", errors="ignore").strip()
    print(f"Pi replied: {ack}")  

    def read_sensor():
        """
        Block until we get a line "T=xx.xxC H=yy.yy%", parse and return dict.
        """
        while True:
            raw = ser.readline().decode("utf-8", errors="ignore").strip()
            if raw.startswith("T="):
                try:
                    t_part, h_part = raw.split()
                    temp = float(t_part[2:-1]) 
                    hum  = float(h_part[2:-1])  
                    print(f"pi return {temp} {hum}")
                    return {"temperature": temp, "humidity": hum}
                except Exception:
                    continue


def main():
    try:
        while True:
            data = read_sensor()
            print(f"Received data → temp={data['temperature']:.2f}°C, humidity={data['humidity']:.2f}%")
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        if not USE_MOCK:
            ser.write(b"stop\r\n")
            print("\nSent stop command to Pi. Exiting.")
        return

if __name__ == "__main__":
    main()
