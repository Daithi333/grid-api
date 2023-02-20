import os


class Config:

    DB_ENGINE = os.environ['DB_ENGINE']

    if DB_ENGINE == 'sqlite':
        PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(PROJECT_ROOT, 'demo-db.sqlite')
        DB_URL = f'sqlite:///{db_path}'

    if DB_ENGINE == 'postgresql':
        DB_USER = os.environ['DB_USER']
        DB_PASS = os.environ['DB_PASS']
        DB_HOST = os.environ['DB_HOST']
        DB_PORT = os.environ['DB_PORT']
        DB_NAME = os.environ['DB_NAME']
        DB_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

        DB_POOL_SIZE = os.getenv('DB_POOL_SIZE', 10)

    FILE_CACHE_SIZE = int(os.getenv('CACHE_SIZE', 50))
