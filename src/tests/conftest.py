import os
from io import BytesIO

import pytest

os.environ['DB_ENGINE'] = 'sqlite'
os.environ['DB_URL'] = "sqlite:///:memory:"

TEST_FILE_PATH = './data/test.xlsx'


@pytest.fixture(scope="session")
def client():
    from app import app
    return app.test_client()


@pytest.fixture(scope="session")
def test_file() -> BytesIO:
    with open(TEST_FILE_PATH, 'rb+') as open_file:
        virtual_file = BytesIO(open_file.read())
        return virtual_file
