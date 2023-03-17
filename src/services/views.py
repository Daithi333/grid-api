from typing import List

from database import db_session
from database.models import View, Condition, Filter
from enums import ConditionOperator, FilterType, FilterOperator
from error import NotFoundError


class ViewService:
    @classmethod
    def get(cls, id_: str, internal: bool = False) -> View or dict:
        session = db_session.get()
        view = session.query(View).filter_by(id=id_).one_or_none()
        if not view:
            raise NotFoundError(message=f'File {id_} not found')

        return view if internal else cls._view_to_dict(view)

    @classmethod
    def list(cls, file_id: str) -> List[dict]:
        session = db_session.get()
        views = session.query(View).filter_by(file_id=file_id).all()
        return [cls._view_to_dict(v) for v in views]

    @classmethod
    def create(cls, file_id: str, name: str, fields: List[str], filters_data: dict) -> dict:
        session = db_session.get()
        filters = []
        for f in filters_data:
            conditions = [
                Condition(operator=ConditionOperator(c['operator']), value=c.get('value'))
                for c in f['conditions']
            ]
            filter_ = Filter(
                field=f['field'],
                filter_type=FilterType(f['filterType']),
                operator=FilterOperator(f['operator']) if f.get('operator') else None,
                conditions=conditions
            )
            filters.append(filter_)

        view = View(file_id=file_id, name=name, fields=fields, filters=filters)
        session.add(view)
        session.commit()
        session.refresh(view)
        return cls._view_to_dict(view)

    @classmethod
    def update(cls, id_: str):
        raise NotImplementedError

    @classmethod
    def delete(cls, id_: str) -> bool:
        session = db_session.get()
        view = cls.get(id_=id_, internal=True)
        session.delete(view)
        session.commit()
        return True

    @classmethod
    def _view_to_dict(cls, view: View) -> dict:
        return {
            'id': view.id,
            'file_id': view.file_id,
            'name': view.name,
            'fields': view.fields,
            'filters': [
                {
                    'field': f.field,
                    'filterType': f.filter_type.value,
                    'operator': f.operator.value if f.operator else None,
                    'conditions': [
                        {'id': c.id, 'operator': c.operator.value if c.operator else None, 'value': c.value}
                        for c in f.conditions]
                }
                for f in view.filters
            ]
        }
