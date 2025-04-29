import os, sys, time, pytest
from pathlib import Path
from importlib.util import spec_from_loader, module_from_spec

@pytest.fixture(autouse=True)
def fake_env(monkeypatch):
    monkeypatch.setenv("POLL_INTERVAL", "0")
    monkeypatch.setenv("DEVICE_ID", "DYNAMIC_TEST_ID")
    monkeypatch.setenv("SERIAL_PORT", "/dev/fakeport")
    monkeypatch.setenv("SERIAL_BAUDRATE", "9600")
    monkeypatch.setenv("DOTENV_CONFIGURED", "1")
    yield

def load_agent_real(monkeypatch):
    src_path = Path(__file__).parent.parent / "raspberry_pi" / "agent.py"
    src = src_path.read_text().replace("USE_MOCK = True", "USE_MOCK = False")
    class FakeSerial:
        def __init__(self, port, baud, timeout):
            assert port == "/dev/fakeport" and baud == 9600
            self._buf = [b"garbage\n", b"T=bad\n", b"T=25.34C H=60.65%\n"]
        def readline(self):
            return self._buf.pop(0)
        def write(self, data):
            pass
    fake_serial = type(sys)("serial")
    fake_serial.Serial = FakeSerial
    monkeypatch.setitem(sys.modules, "serial", fake_serial)
    monkeypatch.setattr(time, "sleep", lambda s: None)
    path = str(src_path.resolve())
    code_obj = compile(src, path, "exec")
    mod = module_from_spec(spec_from_loader("raspberry_pi.agent", loader=None))
    mod.__file__ = path
    sys.modules["raspberry_pi.agent"] = mod
    exec(code_obj, mod.__dict__)
    return mod

def test_real_read_sensor_covers_all_branches(monkeypatch):
    agent_real = load_agent_real(monkeypatch)
    data = agent_real.read_sensor()
    assert data == {"temperature": 25.34, "humidity": 60.65}

def test_main_loop_dynamic_exit_and_prints(monkeypatch, capsys):
    agent_real = load_agent_real(monkeypatch)
    calls = []
    monkeypatch.setattr(agent_real, "insert_metric", lambda p: calls.append(p))
    monkeypatch.setattr(agent_real, "read_sensor", lambda: {"temperature": 1.23, "humidity": 4.56})
    monkeypatch.setattr(time, "sleep", lambda _: (_ for _ in ()).throw(KeyboardInterrupt()))
    with pytest.raises(SystemExit) as exc:
        agent_real.main()
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "Pi replied:" in out
    assert "temp=1.23" in out
    assert "humidity=4.56" in out
    assert calls and calls[0]["temperature"] == 1.23

def test_invalid_line_parsing_loop(monkeypatch):
    agent_real = load_agent_real(monkeypatch)
    class Fake2:
        def __init__(self, *args, **kwargs):
            self._buf = [b"T=notvalid\n", b"T=10.0C H=20.0%\n"]
        def readline(self):
            return self._buf.pop(0)
        def write(self, d):
           pass
    agent_real.ser = Fake2()        
    data = agent_real.read_sensor()
    assert data == {"temperature": 10.0, "humidity": 20.0}