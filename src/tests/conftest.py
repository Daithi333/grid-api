import os

import pytest

os.environ['DB_ENGINE'] = 'sqlite'
os.environ['DB_URL'] = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def client():
    from app import app
    return app.test_client()
