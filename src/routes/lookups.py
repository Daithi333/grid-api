from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from error import BadRequestError
from services import LookupService

lookups = Blueprint('lookups', __name__, url_prefix='/lookups')


@lookups.post("")
@jwt_required()
def add_lookup():
    file_id = request.json.get('fileId')
    field = request.json.get('lookupField')
    name = request.json.get('name')
    lookup_file_id = request.json.get('lookupFileId')
    lookup_field = request.json.get('lookupField')
    operator = request.json.get('operator')

    if not any([file_id, field, name, lookup_file_id, lookup_field, operator]):
        raise BadRequestError(message='some lookup fields were missing')

    return LookupService.create(file_id, name, field, lookup_file_id, lookup_field, operator)


@lookups.get("")
@jwt_required()
def get_lookups():
    file_id = request.args.get('fileId')
    if not file_id:
        raise BadRequestError(message='file id not found in request')

    lookup_id = request.args.get('id')

    transaction_id = request.args.get('id')
    if transaction_id:
        return LookupService.get(id_=lookup_id)
    else:
        lookups_ = LookupService.list(file_id=file_id)
        return jsonify(lookups_)


@lookups.delete("")
@jwt_required()
def delete_lookup():
    lookup_id = request.args.get('id')
    if not lookup_id:
        raise BadRequestError(message='id not found in request')

    success = LookupService.delete(id_=lookup_id)
    return {'success': success}
