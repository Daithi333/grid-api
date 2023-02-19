from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from database.models import DeclarativeBase


class Database:
    engine: Engine = None
    session_maker: sessionmaker = None

    def __init__(self, url: str, **kwargs):
        self.engine = create_engine(url, **kwargs)
        self.session_maker = sessionmaker(self.engine)

    def get_session(self):
        session = self.session_maker()
        yield session
        session.close()

    def create_all(self):
        DeclarativeBase.metadata.create_all(self.engine)

    def drop_all(self):
        DeclarativeBase.metadata.drop_all(self.engine)
