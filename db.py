import json
import os
from typing import List

from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(PROJECT_ROOT, 'demo-db.sqlite')
engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})

Base = declarative_base()
Session = sessionmaker(engine)


class File(Base):
    __tablename__ = "file"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    content_type = Column(String)
    blob = Column(LargeBinary)


class Filter(Base):
    __tablename__ = "filter"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    _columns = Column(String)

    rows = relationship('FilterRow', backref="filter")

    @property
    def columns(self) -> List[str]:
        return json.loads(self._columns)

    @columns.setter
    def columns(self, columns: List[str]):
        self._columns = json.dumps(columns)


class FilterRow(Base):
    __tablename__ = "filter_row"

    id = Column(Integer, primary_key=True)
    filter_id = Column(Integer, ForeignKey('filter.id'))
    column = Column(String)
    operator = Column(String)
    value = Column(String)
    index = Column(Integer)


# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


def get_session():
    session = Session()
    yield session
    session.close()
