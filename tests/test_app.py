import pytest
import time
from web_app.app import create_app
from web_app.database.db import collection

@pytest.fixture(autouse=True)
def clear_db():
    collection.delete_many({})
    yield
    collection.delete_many({})

@pytest.fixture
def client(monkeypatch):
    import web_app.app as app_mod
    monkeypatch.setattr(app_mod, "get_system_metrics", lambda: {"temperature": 25, "humidity": 50})
    import web_app.api.weather as weather_mod
    monkeypatch.setattr(weather_mod, "get_current_weather_ny", lambda: (20, 40))

    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()



def test_index(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"<html" in r.data


def test_history_page(client):
    r = client.get("/history")
    assert r.status_code == 200
    assert b"<html" in r.data


def test_history_api_empty(client):
    r = client.get("/api/history")
    assert r.status_code == 200
    j = r.get_json()
    assert j["labels"] == []
    assert j["envTempValues"] == []
    assert j["regionalTempValues"] == []
    assert j["envHumidityValues"] == []
    assert j["regionalHumidityValues"] == []


# def test_collect_and_metrics(client):
#     r1 = client.post("/api/collect")
#     assert r1.status_code == 201
#     ins = r1.get_json()["inserted_id"]
#     r2 = client.get("/api/metrics/latest")
#     assert r2.status_code == 200
#     latest = r2.get_json()
#     assert latest["inserted_id"] == ins
#     assert latest["temperature"] == 25
#     assert latest["humidity"] == 50
#     r3 = client.get("/api/metrics")
#     arr = r3.get_json()
#     assert isinstance(arr, list) and arr[0]["inserted_id"] == ins


def test_metrics_latest_not_found(client):
    r = client.get("/api/metrics/latest")
    assert r.status_code == 404


def test_suggestion_api(client):
    r = client.get("/api/suggestion")
    assert r.status_code == 200
    j = r.get_json()
    assert "suggestion" in j and isinstance(j["suggestion"], str)


def test_weather_api(client):
    r = client.get("/api/weather")
    assert r.status_code == 200
    j = r.get_json()
    for k in ("api_humidity", "api_temp", "env_humidity", "env_temp"):
        assert k in j

