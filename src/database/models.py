import json
from typing import List

from sqlalchemy import Integer, Column, String, LargeBinary, ForeignKey, DateTime, func, Boolean, ForeignKeyConstraint
from sqlalchemy.orm import declarative_base, relationship

from database.column_types import (
    ENUM_FILTER_TYPE, ENUM_CHANGE_TYPE, ENUM_LOOKUP_OPERATOR,
    ENUM_CONDITION_OPERATOR, ENUM_FILTER_OPERATOR, ENUM_APPROVAL_STATUS, ENUM_ROLE, UUID_STRING
)
from database.util import generate_uuid

DeclarativeBase = declarative_base()


class Base(DeclarativeBase):
    __abstract__ = True

    id = Column(UUID_STRING, primary_key=True, default=generate_uuid)


class File(Base):
    __tablename__ = "file"

    name = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    blob = Column(LargeBinary, nullable=False)
    _data_types = Column(String, nullable=False)

    views = relationship("View", back_populates="file", cascade='all, delete')
    lookups = relationship(
        "Lookup", back_populates="file", primaryjoin="File.id==Lookup.file_id", cascade='all, delete'
    )
    transactions = relationship("Transaction", back_populates="file", cascade='all, delete')
    permissions = relationship("Permission", back_populates="file", cascade='all, delete')

    @property
    def data_types(self) -> dict:
        return json.loads(self._data_types)

    @data_types.setter
    def data_types(self, data_types: dict):
        self._data_types = json.dumps(data_types)


class View(Base):
    __tablename__ = "view"

    file_id = Column(UUID_STRING, ForeignKey('file.id'), nullable=False)
    name = Column(String, nullable=False)
    _fields = Column(String, nullable=False)

    filters = relationship('Filter', back_populates="view", cascade='all, delete')
    file = relationship("File", back_populates="views")

    @property
    def fields(self) -> List[str]:
        return json.loads(self._fields)

    @fields.setter
    def fields(self, fields: List[str]):
        self._fields = json.dumps(fields)


class Filter(Base):
    __tablename__ = "filter"

    view_id = Column(UUID_STRING, ForeignKey('view.id'), nullable=False)
    field = Column(String, nullable=False)
    filter_type = Column(ENUM_FILTER_TYPE, nullable=False)
    operator = Column(ENUM_FILTER_OPERATOR, nullable=True)

    conditions = relationship('Condition', back_populates="filter", cascade='all, delete')
    view = relationship("View", back_populates="filters")


class Condition(Base):
    __tablename__ = "condition"

    filter_id = Column(UUID_STRING, ForeignKey('filter.id'), nullable=False)
    operator = Column(ENUM_CONDITION_OPERATOR, nullable=False)
    value = Column(String, nullable=True)

    filter = relationship("Filter", back_populates="conditions")


class Lookup(Base):
    __tablename__ = "lookup"

    name = Column(String, nullable=False)
    file_id = Column(UUID_STRING, ForeignKey('file.id'), nullable=False)
    field = Column(String, nullable=False)
    lookup_file_id = Column(UUID_STRING, ForeignKey('file.id'), nullable=False)
    lookup_field = Column(String, nullable=False)
    operator = Column(ENUM_LOOKUP_OPERATOR, nullable=False)

    file = relationship("File", foreign_keys=[file_id])
    lookup_file = relationship('File', foreign_keys=[lookup_file_id])

    __table_args__ = (
        ForeignKeyConstraint([file_id], ['file.id']),
        ForeignKeyConstraint([lookup_file_id], ['file.id'])
    )


class Transaction(Base):
    __tablename__ = "transaction"

    file_id = Column(UUID_STRING, ForeignKey('file.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id = Column(UUID_STRING, ForeignKey('user.id'), nullable=False)
    status = Column(ENUM_APPROVAL_STATUS, nullable=False)
    notes = Column(String)
    approved_at = Column(DateTime(timezone=True), onupdate=func.now())
    approver_id = Column(UUID_STRING, ForeignKey('user.id'))

    changes = relationship('Change', back_populates="transaction", cascade='all, delete')
    file = relationship('File', back_populates="transactions")
    user = relationship('User', foreign_keys=[user_id])
    approver = relationship('User', foreign_keys=[approver_id])

    __table_args__ = (
        ForeignKeyConstraint([user_id], ['user.id']),
        ForeignKeyConstraint([approver_id], ['user.id'])
    )


class Change(Base):
    __tablename__ = "change"

    transaction_id = Column(UUID_STRING, ForeignKey('transaction.id'), nullable=False)
    change_type = Column(ENUM_CHANGE_TYPE, nullable=False)
    row_number = Column(Integer, nullable=False)
    _before = Column(String)
    _after = Column(String)

    @property
    def before(self) -> dict:
        return json.loads(self._before) if self._before else None

    @before.setter
    def before(self, before: dict):
        self._before = json.dumps(before)

    @property
    def after(self) -> dict:
        return json.loads(self._after) if self._after else None

    @after.setter
    def after(self, after: dict):
        self._after = json.dumps(after)

    transaction = relationship("Transaction", back_populates="changes")


class User(Base):
    __tablename__ = "user"

    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    temp_password = Column(Boolean, nullable=False, default=False)

    permissions = relationship("Permission", back_populates="user", cascade='all, delete')


class Permission(Base):
    __tablename__ = "permission"

    file_id = Column(UUID_STRING, ForeignKey('file.id'), nullable=False)
    user_id = Column(UUID_STRING, ForeignKey('user.id'), nullable=False)
    role = Column(ENUM_ROLE, nullable=False)

    file = relationship("File", back_populates="permissions")
    user = relationship('User', back_populates="permissions")
