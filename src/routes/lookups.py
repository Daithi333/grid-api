from flask import Blueprint, jsonify, request

from database import db
from database.models import Lookup
from enums import LookupOperator

lookups = Blueprint('lookups', __name__, url_prefix='/lookups')


@lookups.post("")
def add_lookup():
    file_id = request.json.get('fileId')
    field = request.json.get('lookupField')
    name = request.json.get('name')
    lookup_file_id = request.json.get('lookupFileId')
    lookup_field = request.json.get('lookupField')
    operator = request.json.get('operator')

    if not any([file_id, field, name, lookup_file_id, lookup_field, operator]):
        return {'message': 'some lookup fields were missing'}, 400

    lookup = Lookup(name=name, file_id=file_id, field=field,
                    lookup_file_id=lookup_file_id, lookup_field=lookup_field, operator=LookupOperator(operator))
    session = next(db.get_session())
    session.add(lookup)
    session.commit()
    session.refresh(lookup)

    return {"id": lookup.id}


@lookups.get("")
def get_lookups():
    session = next(db.get_session())
    file_id = request.args.get('fileId')
    if not file_id:
        return {'message': 'file_id not found in request'}, 404

    lookup_id = request.args.get('id')

    if lookup_id:
        lookup = session.query(Lookup).filter_by(id=lookup_id, file_id=file_id).one_or_none()
        if not lookup:
            return {'message': f'lookup {lookup_id!r} not found'}, 404

        return _lookup_to_dict(lookup)

    else:
        lookups = session.query(Lookup).filter_by(file_id=file_id).all()
        return jsonify([_lookup_to_dict(lk) for lk in lookups])


def _lookup_to_dict(lookup: Lookup) -> dict:
    return {
            'id': lookup.id,
            'name': lookup.name,
            'fileId': lookup.file_id,
            'field': lookup.field,
            'lookupFileId': lookup.lookup_file_id,
            'lookupField': lookup.lookup_field,
            'operator': lookup.operator.value
        }


@lookups.delete("")
def delete_lookup():
    lookup_id = request.args.get('id')
    if not lookup_id:
        return {'message': 'id not found in request'}, 400

    session = next(db.get_session())
    lookup = session.query(Lookup).filter_by(id=lookup_id).one_or_none()
    if not lookup:
        return {'message': f'lookup {lookup_id!r} not found'}, 404

    session.delete(lookup)
    session.commit()
    return {'success': True}
