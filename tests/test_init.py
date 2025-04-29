import pytest
import importlib
import importlib
import web_app

def test_web_app_package():
    mod = importlib.reload(web_app)
    assert hasattr(mod, "create_app")
    assert callable(mod.create_app)

def test_web_app_package_imports():
    
    import web_app
    importlib.reload(web_app)
    assert hasattr(web_app, "create_app")
    assert callable(web_app.create_app)
