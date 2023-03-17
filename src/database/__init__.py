import logging
from contextvars import ContextVar

from sqlalchemy.orm import Session

from config import Config
from .db import SqliteDatabase, PostgresDatabase

logger = logging.getLogger(__name__)

connect_args = {}
kwargs = {}

if Config.DB_ENGINE == 'sqlite':
    connect_args = {"check_same_thread": False}
    db = SqliteDatabase(Config.DB_URL, connect_args=connect_args)
    logger.info('Initialised SqLite Database')

elif Config.DB_ENGINE == 'postgresql':
    kwargs = {
        'pool_size': Config.DB_POOL_SIZE,
        'max_overflow': Config.DB_MAX_OVERFLOW,
        'pool_pre_ping': True
    }
    db = PostgresDatabase(Config.DB_URL, connect_args={}, **kwargs)
    logger.info('Initialised PostgreSQL Database')

else:
    raise ValueError(f'Unknown Database Engine provided: {Config.DB_ENGINE}')

# db.drop_schema()
# db.create_schema()

db_session: ContextVar[Session] = ContextVar("db_session")


def init_db_session():
    session = db.get_session()
    db_session.set(session)
    logger.debug('Initialised Database Session')


def teardown_db_session():
    session = db_session.get()
    session.close()
    logger.debug('Closed Database Session')
