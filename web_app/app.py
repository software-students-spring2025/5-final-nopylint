import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, 'x.env'))
from flask import Flask, render_template, jsonify, request
from web_app.api.weather import get_weather_summary
from web_app.database.db import insert_metric, get_latest, query_metrics
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

    @app.route('/api/weather', methods=['GET'])
    def weather_api():
        summary = get_weather_summary()
        return jsonify(summary)

    @app.route('/api/collect', methods=['POST'])
    def collect_api():
        payload = get_system_metrics()
        new_id = insert_metric(payload)
        return jsonify({'inserted_id': new_id}), 201

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
