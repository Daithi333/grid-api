from typing import List

from context import db_session
from database.models import Lookup
from enums import LookupOperator
from error import NotFoundError


class LookupService:
    @classmethod
    def get(cls, id_: str, internal: bool = False) -> Lookup or dict:
        session = db_session.get()
        lookup = session.query(Lookup).filter_by(id=id_).one_or_none()
        if not lookup:
            raise NotFoundError(message=f'File {id_} not found')

        return lookup if internal else cls._lookup_to_dict(lookup)

    @classmethod
    def list(cls, file_id: str) -> List[dict]:
        session = db_session.get()
        lookups = session.query(Lookup).filter_by(file_id=file_id).all()
        return [cls._lookup_to_dict(l) for l in lookups]

    @classmethod
    def create(cls, file_id: str, name: str, field: str, lookup_file_id: str, lookup_field: str, operator: str) -> dict:
        session = db_session.get()
        lookup = Lookup(
            name=name, file_id=file_id, field=field, lookup_file_id=lookup_file_id,
            lookup_field=lookup_field, operator=LookupOperator(operator)
        )
        session.add(lookup)
        session.commit()
        session.refresh(lookup)
        return cls._lookup_to_dict(lookup)

    @classmethod
    def update(cls, id_: str):
        raise NotImplementedError

    @classmethod
    def delete(cls, id_: str) -> bool:
        session = db_session.get()
        lookup = cls.get(id_=id_, internal=True)
        session.delete(lookup)
        session.commit()
        return True

    @classmethod
    def _lookup_to_dict(cls, lookup: Lookup) -> dict:
        return {
            'id': lookup.id,
            'name': lookup.name,
            'fileId': lookup.file_id,
            'field': lookup.field,
            'lookupFileId': lookup.lookup_file_id,
            'lookupField': lookup.lookup_field,
            'operator': lookup.operator.value
        }
