[![Sensor Image CI/CD](https://github.com/software-students-spring2025/5-final-nopylint/actions/workflows/sensor.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-nopylint/actions/workflows/sensor.yml)
[![DB CI/CD](https://github.com/software-students-spring2025/5-final-nopylint/actions/workflows/db.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-nopylint/actions/workflows/db.yml)
# Final Project

An exercise to put to practice software development teamwork, subsystem communication, containers, deployment, and CI/CD pipelines. See [instructions](./instructions.md) for details.

Team Members: [Nina Li](https://github.com/nina-jsl), [Jason Lin](https://github.com/JasonLIN0226), [Allen Ni](https://github.com/AllenNi66), [Sirui Wang](https://github.com/siruiii)


## Quick Start Guide

This project streams temperature and humidity data from a Raspberry Pi to a Flask‑based dashboard running on your Mac (or any host computer).

---

### 1 · Set up environment

```bash
python3 -m venv .venv          
source .venv/bin/activate     
pip install -r web_app/requirements.txt
```

---


### 2 · Run the sensor script on the Raspberry Pi

On the Pi (SSH or physical login):

```bash
python3 sensor_serial.py
```

---

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
---

## 4 · Open the dashboard

Visit the URL printed above—typically <http://localhost:4000>.

You’ll see:

* **Environment** – live temperature / humidity from the Pi  
* **Regional** – current NYC weather (via Open‑Meteo API)  
* Values refresh every **5 s**.  
* Click **Save This** to store a snapshot in MongoDB, or **View History** to browse all records, or **Generate Suggestion** to get personalized clothing and weather tips based on current conditions.

---


## License

MIT © 2025 nopylint

