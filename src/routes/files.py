from flask import Blueprint, request, jsonify, send_file

from error import BadRequestError
from services import FileDataService, FileService

files = Blueprint('files', __name__, url_prefix='/files')


@files.post("")
def add_file():
    file = request.files.get('file')
    if not file:
        raise BadRequestError(message='file not found in request')

    filename = file.filename
    content_type = file.content_type
    file_bytes = file.read()
    data_types = FileDataService.get_data_types(file_bytes)
    return FileService.create(file_bytes, filename, content_type, data_types)


@files.put("")
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
    return FileService.update(file_id, file_bytes, filename, content_type, data_types)


@files.get("")
def get_files():
    file_id = request.args.get('id')
    if file_id:
        return FileService.get(id_=file_id)
    else:
        files_ = FileService.list()
        return jsonify(files_)


@files.delete("")
def delete_file():
    file_id = request.args.get('id')
    if not file_id:
        raise BadRequestError(message='id not found in request')

    success = FileService.delete(id_=file_id)
    return {'success': success}


@files.get("/download")
def download_file():
    file_id = request.args.get('id')
    if not file_id:
        raise BadRequestError(message='id not found in request')

    blob, filename, content_type = FileService.download(id_=file_id)
    return send_file(blob, mimetype=content_type, as_attachment=True, download_name=filename)


@files.get("/data")
def get_file_data():
    file_id = request.args.get('id')
    if not file_id:
        raise BadRequestError(message='id not found in request')

    return FileDataService.get_data(id_=file_id)
