import json
import os
from unittest.mock import patch

import pytest

import tests.test_env  # noqa

from database import db
from database.models import User, File, Permission

DATA_PATH = './data'
RESULTS_PATH = './results'
TEST_EXCEL = 'test.xlsx'
TEST_LOOKUP_EXCEL = 'lookup.xlsx'
TEST_TXT = 'test.txt'


@pytest.fixture(scope="session", autouse=True)
def initialise_db():
    db.create_schema()
    yield
    db.drop_schema()


@pytest.fixture(scope="session")
def test_user(initialise_db) -> dict:
    session = db.get_session()
    user = User(
        firstname='test',
        lastname='user',
        email='testuser@mail.com',
        password_hash='abc123'
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {'id': user.id}


@pytest.fixture(scope="session")
def mock_jwt_required():
    """
    Disables the Auth check done by the '@jwt_required' decorator
    """
    with patch('flask_jwt_extended.view_decorators.verify_jwt_in_request') as mock_jwt_required:
        yield mock_jwt_required


@pytest.fixture(scope="session")
def mock_jwt_functions(test_user):
    """
    Disables the Auth check done by the custom '@jwt_user_required' decorator,
    and also sets the test user id as the 'current_user_id'
    """
    with patch('decorators.verify_jwt_in_request') as mock_verify_jwt, \
            patch('decorators.get_jwt_identity') as mock_get_jwt_identity:

        mock_get_jwt_identity.return_value = {'id': test_user['id']}
        yield mock_verify_jwt, mock_get_jwt_identity


@pytest.fixture(scope="function")
def test_file(test_user) -> dict:
    session = db.get_session()
    file = File(
        name='test.xlsx',
        blob=get_file_bytes(TEST_EXCEL),
        data_types={
            'First Name': 's',
            'Last Name': 's',
            'Age': 'n',
            'Strength': 'n',
            'Speed': 'n',
            'Intelligence': 'n',
            'Average': 'f',
            'Date Entered': 'd'
        },
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    session.add(file)
    session.commit()
    session.refresh(file)
    permission = Permission(
        user_id=test_user['id'],
        file_id=file.id,
        role='OWNER'
    )
    session.add(permission)
    session.commit()
    return {'id': file.id}


@pytest.fixture(scope="function", autouse=True)
def test_delete_files():
    """
    Delete files and child objects after each test, while preserving the db schema and test user.
    """
    yield
    session = db.get_session()
    session.query(File).delete()
    session.commit()


@pytest.fixture(scope="function")
def client():
    from app import app
    return app.test_client()


def get_file_bytes(filename: str) -> bytes:
    with open(os.path.join(DATA_PATH, filename), 'rb+') as open_file:
        return open_file.read()


def put_results(results: dict, filename: str):
    with open(os.path.join(RESULTS_PATH, filename), 'w') as json_file:
        json.dump(results, json_file, indent=2)


def get_results(filename: str) -> dict:
    with open(os.path.join(RESULTS_PATH, filename), 'r') as json_file:
        return json.load(json_file)
