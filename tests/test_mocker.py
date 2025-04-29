from raspberry_pi.mock_sensor import read

def test_mock_sensor_returns_dict_with_floats():
    data = read()
    assert isinstance(data, dict)
    assert "temperature" in data
    assert "humidity" in data
    assert isinstance(data["temperature"], float)
    assert isinstance(data["humidity"], float)
