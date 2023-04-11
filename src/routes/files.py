from flask import Blueprint, request, jsonify, send_file

from context import current_user_id
from decorators import jwt_user_required
from error import BadRequestError
from services import FileDataService, FileService, PermissionService

files = Blueprint('files', __name__, url_prefix='/files')


@files.post("")
@jwt_user_required()
def add_file():
    file = request.files.get('file')
    if not file:
        raise BadRequestError(message='file not found in request')

    filename = file.filename
    content_type = file.content_type
    file_bytes = file.read()
    data_types = FileDataService.get_data_types(file_bytes)
    file_ = FileService.create(file_bytes, filename, content_type, data_types)
    user_id = current_user_id.get()
    PermissionService.create(file_id=file_['id'], user_id=user_id, role='OWNER')
    return file_


@files.put("")
@jwt_user_required()
def update_file():
    file_id = request.args.get('id')
    if not file_id:
        raise BadRequestError(message='id not found in request')

    file = request.files.get('file')
    if not file:
        raise BadRequestError(message='file not found in request')

    filename = file.filename
    content_type = file.content_type
    file_bytes = file.read()
    data_types = FileDataService.get_data_types(file_bytes)
    return FileService.update(
        id_=file_id,
        file_bytes=file_bytes,
        filename=filename,
        content_type=content_type,
        data_types=data_types
    )


@files.get("")
@jwt_user_required()
def get_files():
    file_id = request.args.get('id')
    if file_id:
        return FileService.get(file_id)
    else:
        files_ = FileService.list()
        return jsonify(files_)


@files.delete("")
@jwt_user_required()
def delete_file():
    file_id = request.args.get('id')
    if not file_id:
        raise BadRequestError(message='id not found in request')

    success = FileService.delete(id_=file_id)
    return {'success': success}


@files.get("/download")
@jwt_user_required()
def download_file():
    file_id = request.args.get('id')
    if not file_id:
        raise BadRequestError(message='id not found in request')

    blob, filename, content_type = FileService.download(id_=file_id)
    return send_file(blob, mimetype=content_type, as_attachment=True, download_name=filename)


@files.get("/data")
@jwt_user_required()
def get_file_data():
    file_id = request.args.get('id')
    if not file_id:
        raise BadRequestError(message='id not found in request')

    return FileDataService.get_data(id_=file_id)
