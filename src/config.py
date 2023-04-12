import os


class Config:

    DB_ENGINE = os.environ['DB_ENGINE']

    if DB_ENGINE == 'sqlite':
        PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(PROJECT_ROOT, '../demo.db')
        DB_URL = f'sqlite:///{db_path}'

    if DB_ENGINE == 'postgresql':
        DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 10))
        DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 20))
        DB_USER = os.environ['DB_USER']
        DB_PASS = os.environ['DB_PASS']
        DB_HOST = os.environ['DB_HOST']
        DB_PORT = os.environ['DB_PORT']
        DB_NAME = os.environ['DB_NAME']
        DB_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = os.getenv('SERVER_PORT', 5000)
    CORS_ALLOW_ORIGINS = os.getenv('CORS_ALLOW_ORIGINS', '*')
    GUNICORN_WORKER_COUNT = 1  # hard-code for now due to caching issues across worker processes
    GUNICORN_WORKER_THREADS = os.getenv('GUNICORN_WORKER_THREADS', 5)
    GUNICORN_TIMEOUT = os.getenv('GUNICORN_TIMEOUT', 30)
    GUNICORN_RELOAD = os.getenv('GUNICORN_RELOAD', '0').lower() in ['1', 'true']

    LO_AVAILABLE = os.getenv('LO_AVAILABLE') in ['1', 'true']
    EXCEL_AVAILABLE = os.getenv('EXCEL_AVAILABLE') in ['1', 'true']

    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 15))
    FILE_CACHE_SIZE = int(os.getenv('CACHE_SIZE', 50))

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = float(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 1))  # hours
    JWT_REFRESH_TOKEN_EXPIRES = float(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 30))  # days
