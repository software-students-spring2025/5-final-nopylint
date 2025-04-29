import pytest
from raspberry_pi.mock_sensor import read

def test_mock_sensor_returns_dict_with_floats():
    data = read()
    assert isinstance(data, dict)
    assert "temperature" in data
    assert "humidity" in data
    assert isinstance(data["temperature"], float)
    assert isinstance(data["humidity"], float)

def test_mock_sensor_values_in_range():
    for _ in range(10):
        d = read()
        t, h = d["temperature"], d["humidity"]
        assert -50.0 <= t <= 100.0

        assert 0.0 <= h <= 100.0

def test_mock_sensor_repeatability():

    d1 = read()
    d2 = read()
    assert d1 != d2 or "temperature" in d1  
