
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, 'x.env'))

import json
from flask import Flask, render_template, jsonify, request

from web_app.api.weather import get_current_weather_ny

from web_app.database.db import insert_metric, get_latest, query_metrics
from raspberry_pi.agent import get_system_metrics  

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
    )

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/weather', methods=['GET'])
    def weather_api():

        api_temp, api_humidity = get_current_weather_ny()
        system_metrics = get_system_metrics()
        env_temp = system_metrics.get('temperature')
        env_humidity = system_metrics.get('humidity')

        return jsonify({
        "success": True,
        "api_temp": api_temp,
        "api_humidity":  api_humidity,
        "env_temp": env_temp,
        "env_humidity": env_humidity,
        "timestamp": request.args.get('timestamp', None)
    })

    @app.route('/history')
    def history_page():
        return render_template('history.html')

    @app.route('/api/history', methods=['GET'])
    def history_api():
        docs = query_metrics()

        labels = []
        envTempValues = []
        regionalTempValues = []
        envHumidityValues = []
        regionalHumidityValues = []

        for d in docs:

            ts = d.get("timestamp", "unknown") 
            labels.append(ts)
            
            env_temp = d.get("temperature", None)
            env_hum  = d.get("humidity", None)
            api_temp = d.get("api_temperature", None)
            api_hum  = d.get("api_humidity", None)


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
        
        return jsonify(result)

    @app.route('/api/collect', methods=['POST'])
    def collect_api():
        system_metrics = get_system_metrics()
        try:
            temp, humidity = get_current_weather_ny()
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
    
    @app.route('/api/suggestion', methods=['GET'])
    def suggestion_api():
        try:
            api_temp, api_humidity = get_current_weather_ny()
            system_metrics = get_system_metrics()
            env_temp = system_metrics.get('temperature')
            env_humidity = system_metrics.get('humidity')

            prompt = (
                f"Given the current environment temperature {env_temp}°C and humidity {env_humidity}%, "
                f"and the regional temperature {api_temp}°C and humidity {api_humidity}%, "
                f"give a 1-2 sentence suggestion on what to wear or any useful tip."
            )

            response = client.chat.completions.create(
                model="gpt-4",  # or "gpt-3.5-turbo" if you want
                messages=[
                    {"role": "system", "content": "You are a helpful weather-based suggestion assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=80,
                temperature=0.7
            )

            suggestion = response.choices[0].message.content.strip()

            return jsonify({"suggestion": suggestion})
            
        except Exception as e:
            print(f"❌ Suggestion generation error: {e}")
            return jsonify({"error": str(e)}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=4000, debug=True)
