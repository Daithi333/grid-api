import logging

from config import Config
from .db import Database

logger = logging.getLogger(__name__)

connect_args = {}
kwargs = {}

if Config.DB_ENGINE == 'sqlite':
    connect_args = {"check_same_thread": False}

elif Config.DB_ENGINE == 'postgresql':
    kwargs = {
        'pool_size': Config.DB_POOL_SIZE,
        'max_overflow': Config.DB_MAX_OVERFLOW,
        'pool_pre_ping': True
    }

else:
    raise ValueError(f'Unknown Database Engine provided: {Config.DB_ENGINE}')

db = Database(Config.DB_URL, connect_args={}, **kwargs)

logger.info(f'Initialised {Config.DB_ENGINE} Database')
