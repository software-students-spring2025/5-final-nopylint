
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, 'x.env'))

import json
from flask import Flask, render_template, jsonify, request

from web_app.api.weather import get_current_weather_ny

from web_app.database.db import insert_metric, get_latest, query_metrics, save,fetch_history
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
        docs = fetch_history()

        labels = []
        envTempValues = []
        regionalTempValues = []
        envHumidityValues = []
        regionalHumidityValues = []

        for d in docs:

            ts = d.get("timestamp", "unknown") 
            labels.append(ts)
            
            env_temp = d.get("env_temp", None)
            env_hum  = d.get("env_humidity", None)
            api_temp = d.get("api_temp", None)
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
        env_temp = system_metrics.get('temperature')
        env_humidity = system_metrics.get('humidity')
        try:
            api_temp, api_humidity = get_current_weather_ny()
            payload = {
                "api_temp": api_temp,
                "api_humidity":  api_humidity,
                "env_temp": env_temp,
                "env_humidity": env_humidity,
            }
            new_id = save(payload)
            return jsonify({'inserted_id': new_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
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
