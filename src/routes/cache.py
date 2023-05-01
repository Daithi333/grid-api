from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from services.file_data import file_cache

cache = Blueprint('cache', __name__, url_prefix='/cache')


@cache.get("")
@jwt_required()
def get_cache_summary():
    return file_cache.summary()


@cache.get("/keys")
@jwt_required()
def get_cache_keys():
    return file_cache.keys()


@cache.delete("")
@jwt_required()
def clear_from_cache():
    file_id = request.args.get('id')
    if file_id:
        success = file_cache.remove(id_=file_id)
        message = f'File {file_id} cleared from file cache' if success else 'File not in cache'
    else:
        success = file_cache.clear()
        message = 'File cache cleared'

    return {'success': success, 'message': message}
