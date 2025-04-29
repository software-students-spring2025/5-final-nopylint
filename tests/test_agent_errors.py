import os
import sys
import importlib
import pytest

def reload_agent():
    import raspberry_pi.agent as m
    return importlib.reload(m)

def test_get_system_metrics_on_sensor_error(monkeypatch, capsys):
    monkeypatch.setenv("USE_MOCK_SENSOR", "true")
    agent = reload_agent()
    monkeypatch.setattr(agent, "read_sensor", lambda: (_ for _ in ()).throw(Exception("boom")))
    with pytest.raises(Exception) as excinfo:
        agent.get_system_metrics()
    assert "boom" in str(excinfo.value)

def test_module_level_loadenv_and_path():
    import raspberry_pi.agent  
    assert any("5-final-nopylint" in p for p in sys.path)
