import os, importlib, pytest
from datetime import datetime

def test_get_system_metrics_fields(monkeypatch):
    monkeypatch.setenv("USE_MOCK_SENSOR", "true")
    import raspberry_pi.agent as agent_mod
    importlib.reload(agent_mod)

    monkeypatch.setattr(agent_mod, "read_sensor", lambda: {"temperature": 23.4, "humidity": 45.6})
    payload = agent_mod.get_system_metrics()

    assert payload["temperature"] == 23.4
    assert payload["humidity"] == 45.6
    assert "device_id" in payload
    assert isinstance(payload["device_id"], str) and len(payload["device_id"]) > 0
    assert "timestamp" in payload
    dt = datetime.fromisoformat(payload["timestamp"])
    assert isinstance(dt, datetime)

def test_get_system_metrics_with_real_sensor(monkeypatch):
    monkeypatch.setenv("USE_MOCK_SENSOR", "false")
    import raspberry_pi.agent as agent_mod
    importlib.reload(agent_mod)
    monkeypatch.setattr(agent_mod, "read_sensor", lambda: {"temperature": 11.1, "humidity": 22.2})
    payload = agent_mod.get_system_metrics()

    assert payload["temperature"] == 11.1
    assert payload["humidity"] == 22.2

def test_read_sensor_error_propagates(monkeypatch):
    monkeypatch.setenv("USE_MOCK_SENSOR", "true")
    import raspberry_pi.agent as agent_mod
    importlib.reload(agent_mod)

    def bad_read():
        raise RuntimeError("sensor fail")
    monkeypatch.setattr(agent_mod, "read_sensor", bad_read)

    with pytest.raises(RuntimeError):
        agent_mod.get_system_metrics()
