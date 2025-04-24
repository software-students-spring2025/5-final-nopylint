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
        print("Calling get_current_weather_ny()...")  # Debug
        try:
            temp, humidity = get_current_weather_ny()
            print(f"Raw values: temp={temp}, humidity={humidity}")  # Debug

            if temp is None or humidity is None:
                return jsonify({
                    "success": False,
                    "error": "Weather data not available at this time."
                }), 503

            return jsonify({
                "success": True,
                "temperature": f"{temp:.2f}",
                "humidity":    f"{humidity:.2f}"
            })

        except Exception as e:
            print(f"Error in /api/weather: {e}")  # Debug
            return jsonify({
                "success": False,
                "error": "An error occurred while fetching weather data.",
                "details": str(e)
            }), 500

    # ----- HISTORY PAGE & API -----
    @app.route('/history')
    def history_page():
        return render_template('history.html')

    @app.route('/api/history', methods=['GET'])
    def history_api():
        json_path = os.path.join(
            os.path.dirname(__file__),
            'api',
            'history.json'
        )
        with open(json_path, 'r') as f:
            data = json.load(f)
        return jsonify(data)

    # ----- METRICS COLLECTION & QUERY -----
    @app.route('/api/collect', methods=['POST'])
    def collect_api():
        payload = get_system_metrics()
        try:
            new_id = insert_metric(payload)
            return jsonify({'inserted_id': new_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/metrics', methods=['GET'])
    def metrics_api():
        docs = query_metrics()
        for d in docs:
            d['inserted_id'] = str(d.pop('_id'))
            d['timestamp']   = d['timestamp'].isoformat() + 'Z'
        return jsonify(docs)

    @app.route('/api/metrics/latest', methods=['GET'])
    def latest_api():
        d = get_latest()
        if not d:
            return jsonify({}), 404
        d['inserted_id'] = str(d.pop('_id'))
        d['timestamp']   = d['timestamp'].isoformat() + 'Z'
        return jsonify(d)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=4000, debug=True)

