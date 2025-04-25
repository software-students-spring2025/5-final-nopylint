import sys
import os

# 0) Make sure your project root is on the path before importing local modules
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

# 1) Load .env before anything else
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, 'x.env'))

import json
from flask import Flask, render_template, jsonify, request

# 2) Now import your own modules
from api.weather import get_current_weather_ny
from database.db import insert_metric, get_latest, query_metrics
from raspberry_pi.agent import get_system_metrics  


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
    )

    @app.route('/')
    def index():
        return render_template('index.html')

    # ----- DYNAMIC WEATHER ENDPOINT -----
    @app.route('/api/weather', methods=['GET'])
    def weather_api():
        # print("Calling get_current_weather_ny()...")  # Debug

        temp, humidity = get_current_weather_ny()
        # print(f"Raw values: temp={temp}, humidity={humidity}")  # Debug

        return jsonify({
            "success": True,
            "temperature": temp,
            "humidity":  humidity,
            "timestamp": request.args.get('timestamp', None)
        })

    # ----- HISTORY PAGE & API -----
    @app.route('/history')
    def history_page():
        return render_template('history.html')

    @app.route('/api/history', methods=['GET'])
    def history_api():
        docs = query_metrics()
        # print(f"Fetched {len(docs)} documents from DB")

        labels = []
        envTempValues = []
        regionalTempValues = []
        envHumidityValues = []
        regionalHumidityValues = []

        for d in docs:
            # print(f"Processing document: {d}")  # 🔥 Print each doc

            ts = d.get("timestamp", "unknown")  # <- fixed
            labels.append(ts)
            
            env_temp = d.get("temperature", None)
            env_hum  = d.get("humidity", None)
            api_temp = d.get("api_temperature", None)
            api_hum  = d.get("api_humidity", None)

            # print(f"Parsed: ts={ts}, env_temp={env_temp}, env_hum={env_hum}, api_temp={api_temp}, api_hum={api_hum}")

            envTempValues.append(env_temp)
            envHumidityValues.append(env_hum)
            regionalTempValues.append(api_temp)
            regionalHumidityValues.append(api_hum)

        result = {
            "labels": labels,
            "envTempValues": envTempValues,
            "regionalTempValues": regionalTempValues,
            "envHumidityValues": envHumidityValues,
            "regionalHumidityValues": regionalHumidityValues
        }
        
        # print("Returning JSON:", result)  # 🔥 Final debug before returning
        return jsonify(result)



    # ----- METRICS COLLECTION & QUERY -----
    @app.route('/api/collect', methods=['POST'])
    def collect_api():
        system_metrics = get_system_metrics()
        try:
            temp, humidity = get_current_weather_ny()
            # Merge the two payloads
            payload = {
                **system_metrics,
                'api_temperature': temp,
                'api_humidity': humidity
            }
            new_id = insert_metric(payload)
            return jsonify({'inserted_id': new_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/metrics', methods=['GET'])
    def metrics_api():
        docs = query_metrics()
        for d in docs:
            d['inserted_id'] = str(d.pop('_id'))
            d['timestamp'] = d.get('timestamp', 'unknown')
        return jsonify(docs)

    @app.route('/api/metrics/latest', methods=['GET'])
    def latest_api():
        d = get_latest()
        if not d:
            return jsonify({}), 404
        d['inserted_id'] = str(d.pop('_id'))
        d['timestamp'] = d.get('timestamp', 'unknown')
        return jsonify(d)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=4000, debug=True)

