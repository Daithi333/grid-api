from config import Config
from database.db import Database

connect_args = {}
kwargs = {}

if Config.DB_ENGINE == 'sqlite':
    connect_args = {"check_same_thread": False}
else:
    kwargs = {'pool_size': Config.DB_POOL_SIZE, 'pool_pre_ping': True}

db = Database(Config.DB_URL, connect_args=connect_args, **kwargs)
# db.drop_all()
# db.create_all()
