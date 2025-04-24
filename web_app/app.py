import os, json
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

    @app.route('/api/weather')
    def weather_api():
        json_path = os.path.join(
            os.path.dirname(__file__),
            'api',              # <project-root>/web_app/api/weather.json
            'weather.json'
        )
        with open(json_path) as f:
            return jsonify(json.load(f))

    @app.route('/history')
    def history():
        return render_template('history.html')

    @app.route('/api/history')
    def history_api():
        json_path = os.path.join(
            os.path.dirname(__file__),
            'api',              # <project-root>/web_app/api/history.json
            'history.json'
        )
        with open(json_path) as f:
            return jsonify(json.load(f))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=4000, debug=True)

