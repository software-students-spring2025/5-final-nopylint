import os, importlib, pytest

def test_get_system_metrics_fields(monkeypatch):

    monkeypatch.setenv("USE_MOCK_SENSOR", "true")


    import raspberry_pi.agent as agent_mod
    importlib.reload(agent_mod)
    monkeypatch.setattr(agent_mod, "read_sensor",lambda: {"temperature": 23.4, "humidity": 45.6})

    payload = agent_mod.get_system_metrics()
    assert payload["temperature"] == 23.4
    assert payload["humidity"] == 45.6
    assert "device_id" in payload
    assert "timestamp" in payload
