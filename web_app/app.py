import sys, os

from api.weather import get_current_weather_ny

# 把项目根目录加入 Python 搜索路径，以便找到 raspberry_pi 和 database 包
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 在任何模块导入前先加载环境变量
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'x.env'))

import json
from flask import Flask, render_template, jsonify, request

# 1) 导入数据库操作
from database.db import insert_metric, get_latest, query_metrics

# 2) 导入采集逻辑
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

    @app.route('/api/weather')
    def weather_api():
        print("Calling get_current_weather_ny()...")  # Debug

        try:
            temp, humidity = get_current_weather_ny()
            print(f"Raw values: temp={temp}, humidity={humidity}")  # Debug

            if temp is None or humidity is None:
                print("Weather data is None – possibly not available for this hour.")  # Debug
                return jsonify({
                    "success": False,
                    "error": "Weather data not available at this time."
                }), 503

            return jsonify({
                "success": True,
                "temperature": f"{temp:.2f}",
                "humidity": f"{humidity:.2f}"
            })

        except Exception as e:
            print(f"Error in /api/weather: {e}")  # Debug
            return jsonify({
                "success": False,
                "error": "An error occurred while fetching weather data.",
                "details": str(e)
            }), 500

    # 单次采集并入库
    @app.route('/api/collect', methods=['POST'])
    def collect_api():
        payload = get_system_metrics()
        try:
            new_id = insert_metric(payload)
            return jsonify({'inserted_id': new_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # 查看所有历史记录
    @app.route('/api/metrics', methods=['GET'])
    def metrics_api():
        docs = query_metrics()
        for d in docs:
            d['inserted_id'] = str(d.pop('_id'))
            d['timestamp']   = d['timestamp'].isoformat() + 'Z'
        return jsonify(docs)

    # 查看最新一条记录
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
