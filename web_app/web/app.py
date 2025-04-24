import os
import json
from flask import render_template, jsonify

from db import insert_metric
from collector import get_system_metrics  

def register_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/weather')
    def weather_api():
        json_path = os.path.join(os.path.dirname(__file__), '..', 'api', 'weather.json')
        with open(json_path, 'r') as file:
            data = json.load(file)
        return jsonify(data)

    @app.route('/api/collect', methods=['POST'])
    def collect_api():
        data = get_system_metrics()

        new_id = insert_metric(data)

        return jsonify({'inserted_id': new_id}), 201
