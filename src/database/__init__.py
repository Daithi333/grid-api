from config import Config
from .db import SqliteDatabase, PostgresDatabase

connect_args = {}
kwargs = {}

if Config.DB_ENGINE == 'sqlite':
    connect_args = {"check_same_thread": False}
    db = SqliteDatabase(Config.DB_URL, connect_args=connect_args)

elif Config.DB_ENGINE == 'postgresql':
    kwargs = {
        'pool_size': Config.DB_POOL_SIZE,
        'max_overflow': Config.DB_MAX_OVERFLOW,
        'pool_pre_ping': True
    }
    db = PostgresDatabase(Config.DB_URL, connect_args={}, **kwargs)

else:
    raise ValueError(f'Unknown Database Engine provided: {Config.DB_ENGINE}')

# db.drop_schema()
# db.create_schema()
