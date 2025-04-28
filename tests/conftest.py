import os
import importlib
import pytest

os.environ["USE_MOCK_DB"]       = "true"
os.environ["USE_MOCK_SENSOR"]   = "true"
os.environ["DB_NAME"]           = "testdb"
os.environ["COLLECTION_NAME"]   = "testcol"

import web_app.database.db as db_module
importlib.reload(db_module)
db_module.collection.delete_many({})

from web_app.app import create_app

@pytest.fixture(autouse=True)
def clear_db_between_tests():
    yield
    db_module.collection.delete_many({})

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()
