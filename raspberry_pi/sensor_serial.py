
import time
import serial
import board
import busio
import adafruit_shtc3

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_shtc3.SHTC3(i2c)

ser = serial.Serial('/dev/ttyGS0', 115200, timeout=5)

streaming = False

while True:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='ignore').strip().lower()
        if line == 'start':
            streaming = True
            ser.write(b'ACK START\r\n')
        elif line == 'stop':
            streaming = False
            ser.write(b'ACK STOP\r\n')

    if streaming:
        temp, hum = sensor.measurements
        msg = f"T={temp:.2f}C H={hum:.2f}%\r\n"
        ser.write(msg.encode('utf-8'))
        print("Sent:", msg.strip())
        time.sleep(5)
    else:
        time.sleep(0.1)
