[![Sensor Image CI/CD](https://github.com/software-students-spring2025/5-final-nopylint/actions/workflows/sensor.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-nopylint/actions/workflows/sensor.yml)
[![DB CI/CD](https://github.com/software-students-spring2025/5-final-nopylint/actions/workflows/db.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-nopylint/actions/workflows/db.yml)
# Final Project

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.

## ☁️ Smart Weather Dashboard
### Description
- This project is a web-based dashboard that collects, displays, and interprets real-time temperature and humidity data from a Raspberry Pi or simulated input. It demonstrates a lightweight, functional system for capturing and displaying environmental data in real time. It integrates hardware sensing via a Raspberry Pi, regional weather data through a public API, and AI-generated feedback. 

- This web-based dashboard displays live temperature and humidity readings from two sources:

   - Environment: Real-time data captured by a Raspberry Pi + SHTC3 Temperature & Humidity sensor.
   - Regional (NYC): Current weather data fetched from the [Open-Meteo API](https://open-meteo.com/).

- This project features a Flask backend, a HTML/CSS frontend, and uses Chart.js to visualize historical trends in weather data.

### Key features

Live updates every 5 seconds for sensor data.

- **Save This**: Records the current data snapshot into a MongoDB database.

- **View History**: Opens a visual history page showing trends in temperature and humidity over time, using interactive charts.

- **Generate Suggestion**: Leverages OpenAI to provide personalized clothing and weather tips based on both the environmental and regional conditions.

### Team Members
[Nina Li](https://github.com/nina-jsl), [Jason Lin](https://github.com/JasonLIN0226), [Allen Ni](https://github.com/AllenNi66), [Sirui Wang](https://github.com/siruiii)

## Docker Hub Images
[Raspberry Pi Sensor](https://hub.docker.com/r/ninajsl/5-final-nopylint-sensor)

[Web App + Database](https://hub.docker.com/r/ninajsl/5-final-nopylint-web-app)

## Quick Start Guide
### 0. Environment Configuration

This project uses an `x.env` file to manage environment variables securely.

- The `x.env` file is already set up with all required variables **except for OpenAI API key**.
- If you have a raspberry pi for testing, you can set `USE_MOCK_SENSOR=false`
- You must manually add the key to this file before running the app

#### To do:
1. Open the `x.env` file located at the project root
2. Add the OpenAI API key (shared in Discord Channel)

### 1 · Set up environment

```bash
python3 -m venv .venv          
source .venv/bin/activate     
pip install -r web_app/requirements.txt
```


### 2 · Run the sensor script on the Raspberry Pi

On the Pi (SSH or physical login):

```bash
python3 sensor_serial.py
```

### 3 · Start the Flask dashboard on your Mac

Back on your host machine (still inside `.venv`):

```bash
python web_app/app.py
```

* The server listens on **`0.0.0.0:4000`** (change the port in `app.py` if you like).
* Console output shows the exact URL, e.g.

```
 * Running on http://127.0.0.1:4000 (Press CTRL+C to quit)
```

You should see a stream of lines on your Raspberry Pi such as:

```
T=24.7C H=61.3%
```

### 4 · Open the dashboard

Visit the URL printed above—typically <http://localhost:4000>.

You’ll see:

* **Environment** – live temperature / humidity from the Pi  
* **Regional** – current NYC weather (via Open‑Meteo API)  
* Values refresh every **5 s**.  
* Click **Save This** to store a snapshot in MongoDB, or **View History** to browse all records, or **Generate Suggestion** to get personalized clothing and weather tips based on current conditions.


## License

MIT © 2025 nopylint

