# tests/test_app.py
import pytest
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
    monkeypatch.setattr(app_mod, "get_system_metrics", lambda: {"temperature": 0, "humidity": 0})
    import web_app.api.weather as weather_mod
    monkeypatch.setattr(weather_mod, "get_current_weather_ny", lambda: (0, 0))
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()

def test_index_and_history_page(client):
    for path in ["/", "/history"]:
        r = client.get(path)
        assert r.status_code == 200
        assert b"<html" in r.data

def test_history_api_empty(client):
    r = client.get("/api/history")
    assert r.status_code == 200
    assert r.get_json() == {
        "labels": [],
        "envTempValues": [],
        "regionalTempValues": [],
        "envHumidityValues": [],
        "regionalHumidityValues": []
    }

def test_collect_then_history_single(client):
    r = client.post("/api/collect")
    assert r.status_code == 201
    data = r.get_json()
    assert "inserted_id" in data
    r = client.get("/api/history")
    assert r.status_code == 200
    hist = r.get_json()
    assert isinstance(hist["labels"], list)
    assert len(hist["labels"]) >= 1
    assert isinstance(hist["labels"][0], str)
    for key in ("envTempValues", "regionalTempValues", "envHumidityValues", "regionalHumidityValues"):
        lst = hist[key]
        assert isinstance(lst, list)
        assert len(lst) >= 1
        assert isinstance(lst[0], (int, float))

def test_collect_then_history_multiple(client):
    for _ in range(3):
        r = client.post("/api/collect")
        assert r.status_code == 201
    r = client.get("/api/history")
    assert r.status_code == 200
    hist = r.get_json()
    assert isinstance(hist["labels"], list)
    assert len(hist["labels"]) >= 3
    assert all(isinstance(x, str) for x in hist["labels"][-3:])
    for key in ("envTempValues", "regionalTempValues", "envHumidityValues", "regionalHumidityValues"):
        lst = hist[key]
        assert isinstance(lst, list)
        assert len(lst) >= 3
        assert all(isinstance(x, (int, float)) for x in lst[-3:])

def test_suggestion_api(client):
    r = client.get("/api/suggestion")
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        j = r.get_json()
        assert "suggestion" in j and isinstance(j["suggestion"], str)

def test_weather_api(client):
    r = client.get("/api/weather")
    assert r.status_code == 200
    j = r.get_json()
    for field in ("api_temp", "api_humidity", "env_temp", "env_humidity"):
        assert field in j
        assert isinstance(j[field], (int, float))
