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


class View(Base):
    __tablename__ = "view"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file.id'))
    name = Column(String)
    _fields = Column(String)

    filters = relationship('Filter', backref="view")

    @property
    def fields(self) -> List[str]:
        return json.loads(self._fields)

    @fields.setter
    def fields(self, fields: List[str]):
        self._fields = json.dumps(fields)


class Filter(Base):
    __tablename__ = "filter"

    id = Column(Integer, primary_key=True)
    view_id = Column(Integer, ForeignKey('view.id'))
    field = Column(String)
    filter_type = Column(String)
    operator = Column(String, nullable=True)

    conditions = relationship('Condition', backref="filter")


class Condition(Base):
    __tablename__ = "condition"

    id = Column(Integer, primary_key=True)
    filter_id = Column(Integer, ForeignKey('filter.id'))
    operator = Column(String)
    value = Column(String, nullable=True)


class Lookup(Base):
    __tablename__ = "lookup"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    file_id = Column(Integer, ForeignKey('file.id'))
    field = Column(String)
    lookup_file_id = Column(Integer, ForeignKey('file.id'))
    lookup_field = Column(String)
    operator = Column(String)


# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


def get_session():
    session = Session()
    yield session
    session.close()
