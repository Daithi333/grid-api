from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from error import BadRequestError
from services.views import ViewService

views = Blueprint('views', __name__, url_prefix='/views')


@views.post("")
@jwt_required()
def add_view():
    file_id = request.json.get('fileId')
    name = request.json.get('name')
    fields = request.json.get('fields', [])
    filters_data = request.json.get('filters', [])

    if not file_id or not name:
        raise BadRequestError(message='name and file id required')

    if not fields and not filters_data:
        raise BadRequestError(message='view expected to have fields and filter data')

    return ViewService.create(file_id, name, fields, filters_data)


@views.get("")
@jwt_required()
def get_views():
    file_id = request.args.get('fileId')
    if not file_id:
        raise BadRequestError(message='file id not found in request')

    view_id = request.args.get('id')
    if view_id:
        return ViewService.get(id_=view_id)
    else:
        lookups_ = ViewService.list(file_id=file_id)
        return jsonify(lookups_)


@views.delete("")
@jwt_required()
def delete_view():
    view_id = request.args.get('id')
    if not view_id:
        raise BadRequestError(message='id not found in request')

    success = ViewService.delete(id_=view_id)
    return {'success': success}
