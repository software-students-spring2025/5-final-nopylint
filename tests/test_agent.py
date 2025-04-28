import pytest
from raspberry_pi.agent import get_system_metrics

def test_get_system_metrics_fields(monkeypatch):
    import raspberry_pi.agent as agent_mod
    monkeypatch.setattr(agent_mod, "read_sensor", lambda: {"temperature": 23.4, "humidity": 45.6})

    payload = get_system_metrics()
    assert "device_id" in payload
    assert "timestamp" in payload
    assert payload["temperature"] == 23.4
    assert payload["humidity"] == 45.6
