# Use the official Python slim image (multi‐arch: will pull ARM on a Pi)
FROM python:3.12-slim

# set a working directory inside the container
WORKDIR /app

# copy and install Python dependencies
COPY raspberry_pi/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy all your sensor code into the image
COPY raspberry_pi/ ./raspberry_pi/
COPY web_app/ ./web_app/
# (Optional) expose serial device at runtime via --device 
# e.g. docker run --device /dev/ttyUSB0 ...

WORKDIR /app/raspberry_pi
# default command: run your main script
CMD ["python", "agent.py"]
