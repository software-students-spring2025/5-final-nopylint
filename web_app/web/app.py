import os
import json
from flask import render_template, jsonify

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