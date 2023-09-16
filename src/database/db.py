from abc import ABC

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from database.models import DeclarativeBase


class Database(ABC):
    engine: Engine = None
    SessionMaker: sessionmaker = None

    def __init__(self, url: str, **kwargs):
        if not database_exists(url):
            create_database(url)
            self.engine = create_engine(url, **kwargs)
            self.create_schema()
        else:
            self.engine = create_engine(url, **kwargs)
        self.SessionMaker = sessionmaker(self.engine)

    def get_session(self):
        return self.SessionMaker()

    def create_schema(self):
        DeclarativeBase.metadata.create_all(self.engine)

    def drop_schema(self):
        DeclarativeBase.metadata.drop_all(self.engine)
