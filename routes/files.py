import io

from flask import Blueprint, request, jsonify, send_file

from database import db
from database.models import File
from services.file_data import FileData

files = Blueprint('files', __name__, url_prefix='/files')


@files.post("")
def add_file():
    file = request.files.get('file')
    if not file:
        return {'message': 'file not found in request'}, 400
    content_type_full = file.content_type
    content_type = content_type_full.split('.')[0]
    if content_type not in ['application/vnd']:
        return {'message': f'unsupported file type {content_type!r}'}, 400

    session = next(db.get_session())
    file_bytes = file.read()
    data_types = FileData.get_data_types(file_bytes)
    file_ = File(blob=file_bytes, name=file.filename, content_type=content_type_full, data_types=data_types)
    session.add(file_)
    session.commit()
    session.refresh(file_)

    return _file_to_dict(file_)


@files.put("")
def update_file():
    file_id = request.args.get('id')
    if not file_id:
        return {'message': 'id not provided in request'}, 400

    file = request.files.get('file')
    if not file:
        return {'message': 'file not found in request'}, 400

    content_type_full = file.content_type
    content_type = content_type_full.split('.')[0]
    if content_type not in ['application/vnd']:
        return {'message': f'unsupported file type {content_type!r}'}, 400

    session = next(db.get_session())
    file_ = session.query(File).filter_by(id=file_id).one_or_none()
    if not file_:
        return {'message': f'file {file_id!r} not found'}, 404

    file_.blob = file.read()
    file_.name = file.filename
    file_.content_type = content_type_full

    for t in file_.transactions:
        session.delete(t)

    session.commit()

    return {"id": file_.id}


@files.get("")
def get_files():
    session = next(db.get_session())

    file_id = request.args.get('id')

    if file_id:
        file = session.query(File).filter_by(id=file_id).one_or_none()
        if not file:
            return {'message': f'file {file_id!r} not found'}, 404

        return _file_to_dict(file)

    files_ = session.query(File).all()
    return jsonify([_file_to_dict(f) for f in files_])


def _file_to_dict(file: File):
    return {'id': file.id, 'name': file.name, 'content_type': file.content_type, 'size_bytes ': len(file.blob)}


@files.delete("")
def delete_file():
    file_id = request.args.get('id')
    if not file_id:
        return {'message': 'id not provided in request'}, 400

    with next(db.get_session()) as session:
        session.query(File).filter_by(id=file_id).delete()
        session.commit()
    return {'success': True}


@files.get("/download")
def download_file():
    file_id = request.args.get('id')
    if not file_id:
        return {'message': 'id not provided in request'}, 400

    with next(db.get_session()) as session:
        file = session.query(File).filter_by(id=file_id).one()

    blob = io.BytesIO(file.blob)
    return send_file(blob, mimetype=file.content_type, as_attachment=True, download_name=file.name)


@files.get("/data")
def get_file_data():
    file_id = request.args.get('id')
    if not file_id:
        return {'message': 'file id not found in request'}, 400

    session = next(db.get_session())
    file = session.query(File).filter_by(id=file_id).one_or_none()
    if not file:
        return {'message': f'file {file_id} not found'}, 404

    return FileData.get_data(file)
