import json
import time
import pytest
from web_app.app import create_app

@pytest.fixture
def client(monkeypatch):
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()

def test_weather_endpoint(client):
    resp = client.get("/api/weather")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "env_temp" in data
    assert "env_humidity" in data
    assert "regional_temp" in data
    assert "regional_humidity" in data
    assert "suggestion" in data

def test_collect_and_metrics(client):
    
    resp = client.post("/api/collect")
    assert resp.status_code == 201
    body = resp.get_json()
    assert "inserted_id" in body
    time.sleep(0.01)

    resp2 = client.get("/api/metrics/latest")
    assert resp2.status_code == 200
    latest = resp2.get_json()
    assert "device_id" in latest
    assert "timestamp" in latest
    assert "temperature" in latest
    assert "humidity" in latest

    resp3 = client.get("/api/metrics")
    assert resp3.status_code == 200
    all_data = resp3.get_json()
    assert any(d["inserted_id"] == body["inserted_id"] for d in all_data)
