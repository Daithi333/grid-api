from abc import ABC, abstractmethod
from sqlite3.dbapi2 import OperationalError

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from database.models import DeclarativeBase


class Database(ABC):
    engine: Engine = None
    SessionMaker: sessionmaker = None

    def __init__(self, url: str, **kwargs):
        self.engine = self._create_engine(url, **kwargs)
        self.SessionMaker = sessionmaker(self.engine)

    def get_session(self):
        return self.SessionMaker()

    def create_schema(self):
        DeclarativeBase.metadata.create_all(self.engine)

    def drop_schema(self):
        DeclarativeBase.metadata.drop_all(self.engine)

    @classmethod
    @abstractmethod
    def _create_engine(cls, db_uri: str, **kwargs) -> Engine:
        raise NotImplementedError


class SqliteDatabase(Database):
    @classmethod
    def _create_engine(cls, db_uri: str, **kwargs) -> Engine:
        return create_engine(db_uri, **kwargs)


class PostgresDatabase(Database):
    @classmethod
    def _create_engine(cls, db_uri: str, **kwargs) -> Engine:
        """Create engine against existing db or create the db first if it doesn't yet exist"""
        parts = db_uri.rsplit('/', 1)
        uri_start, dbname = parts[0], parts[1]
        try:
            engine = create_engine(db_uri)
            conn = engine.connect()
            conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{dbname}'"))
            conn.close()
            return create_engine(db_uri, **kwargs)

        except OperationalError:
            print(f'creating database: {dbname}')
            engine = create_engine(uri_start)
            conn = engine.connect()
            conn.execute(text(f"CREATE DATABASE {dbname}"))
            conn.close()

            engine = create_engine(db_uri, **kwargs)
            conn = engine.connect()
            conn.close()
            return create_engine(db_uri, **kwargs)
