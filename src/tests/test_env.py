import os

os.environ['DB_ENGINE'] = 'sqlite'
os.environ['DB_URL'] = 'sqlite:///:memory:'
os.environ['JWT_SECRET_KEY'] = 'test-secret'
