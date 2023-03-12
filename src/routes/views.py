from flask import Blueprint, request, jsonify

from database import db
from database.models import View, Condition, Filter
from enums import ConditionOperator, FilterType, FilterOperator

views = Blueprint('views', __name__, url_prefix='/views')


@views.post("")
def add_view():
    file_id = request.json.get('fileId')
    name = request.json.get('name')
    fields = request.json.get('fields', [])
    filters_data = request.json.get('filters', [])

    if not file_id or not name:
        return {'message': 'name and file id required'}, 400

    if not fields and not filters_data:
        return {'message': 'view expected to have columns and/or row filters'}, 400

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
    session = next(db.get_session())
    session.add(view)
    session.commit()
    session.refresh(view)

    return {"id": view.id}


@views.get("")
def get_views():
    session = next(db.get_session())
    file_id = request.args.get('fileId')
    if not file_id:
        return {'message': 'file id not found in request'}, 404

    view_id = request.args.get('id')

    if view_id:
        view = session.query(View).filter_by(id=view_id, file_id=file_id).one_or_none()
        if not view:
            return {'message': f'view {view_id} not found'}, 404

        return _view_to_dict(view)

    else:
        views = session.query(View).filter_by(file_id=file_id).all()
        return jsonify([_view_to_dict(v) for v in views])


def _view_to_dict(view: View) -> dict:
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


@views.delete("")
def delete_view():
    view_id = request.args.get('id')
    if not view_id:
        return {'message': 'id not found in request'}, 400

    session = next(db.get_session())
    view = session.query(View).filter_by(id=view_id).one_or_none()
    if not view:
        return {'message': f'lookup {view_id!r} not found'}, 404

    session.delete(view)
    session.commit()
    return {'success': True}
