from sqlite3.dbapi2 import OperationalError

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from database.models import DeclarativeBase


class Database:
    engine: Engine = None
    session_maker: sessionmaker = None

    def __init__(self, url: str, **kwargs):
        self.engine = self._create_engine(url, **kwargs)
        self.session_maker = sessionmaker(self.engine)

    def get_session(self):
        session = self.session_maker()
        yield session
        session.close()

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
            engine = create_engine(db_uri, **kwargs)
            cls._create_schema(engine)
            return engine

    @classmethod
    def _create_schema(cls, engine):
        DeclarativeBase.metadata.create_all(engine)

    @classmethod
    def _drop_schema(cls, engine):
        DeclarativeBase.metadata.drop_all(engine)
