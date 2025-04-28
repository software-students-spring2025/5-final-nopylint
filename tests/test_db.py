from datetime import datetime
import pytest
from web_app.database.db import insert_metric, get_latest, query_metrics

def test_insert_and_get_latest(monkeypatch):
    now = datetime(2025, 1, 1, 12, 0, 0)
    import web_app.database.db as db_module
    class DummyDateTime:
        @staticmethod
        def now(tz=None):
            return now
        @staticmethod
        def utcnow():
            return now
    monkeypatch.setattr(db_module, "datetime", DummyDateTime)

    payload = {"device_id": "d1", "temperature": 22.5, "humidity": 55.5}
    new_id = insert_metric(payload)
    assert isinstance(new_id, str)

    latest = get_latest()
    assert latest["device_id"] == "d1"
    assert latest["temperature"] == 22.5
    assert latest["humidity"] == 55.5
    assert latest["timestamp"] == now

def test_query_metrics_time_range(monkeypatch):
    import web_app.database.db as db_module
    base = datetime(2025, 1, 1, 0, 0, 0)
    def make_datetime(hour):
        class DT:
            @staticmethod
            def now(tz=None):
                return base.replace(hour=hour)
            @staticmethod
            def utcnow():
                return base.replace(hour=hour)
        return DT

    for i in range(3):
        monkeypatch.setattr(db_module, "datetime", make_datetime(i))
        insert_metric({"device_id": f"d{i}", "temperature": 20+i, "humidity": 50})


    results = query_metrics(base, base.replace(hour=1))

    assert len(results) == 2
    assert results[0]["device_id"] == "d1"
    assert results[1]["device_id"] == "d0"
