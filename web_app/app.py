import os
import json
from flask import Flask, render_template, jsonify

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
    )

    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/history')
    def history():
        return render_template('history.html')

    @app.route('/api/weather')
    def weather_api():
        json_path = os.path.join(os.path.dirname(__file__),  'api', 'weather.json')
        with open(json_path, 'r') as file:
            data = json.load(file)
        return jsonify(data)

    return app


if __name__ == '__main__':
    # When you run `python web/app.py` this block fires
    app = create_app()
    app.run(host='0.0.0.0', port=4000, debug=True)
