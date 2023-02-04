import io

from flask import Blueprint, request, jsonify, send_file

from database import db
from database.models import File
from services.file_data import FileData
from models.data_filter import RowFilter, DataFilter

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

    # with open('stats.xlsx', 'rb') as input_file:
    #     blob = input_file.read()

    session = next(db.get_session())
    file_ = File(blob=file.read(), name=file.filename, content_type=content_type_full)
    session.add(file_)
    session.commit()
    session.refresh(file_)

    return {"id": file_.id}


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

    file.blob = file.read()
    file_.name = file.filename
    file_.content_type = content_type_full
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

    # with open(f'out_{file.name}', "wb") as output_file:
    #     output_file.write(file.blob)
    # return {'success': True}


@files.get("/data")
def get_file_data():
    file_id = request.args.get('id')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    if not file_id:
        return {'message': 'file id not found in request'}, 400

    return FileData.get_data(file_id, limit, offset)


@files.get("/filter-data")
def get_filtered_data():
    data = request.get_json()
    file_id = data.get('id')
    if not file_id:
        return {'message': 'file id not found in request'}, 400

    limit = int(data.get('limit', 100))
    offset = int(data.get('offset', 0))

    filter_data = data.get('filter')
    if not filter_data:
        return {'message': 'filter not found in request'}, 400

    cols_data = filter_data.get('columns')
    if cols_data is None or cols_data is None:
        return {'message': 'Provided filter requires columns'}, 400
    rows_data = filter_data.get('rows')
    if rows_data is None:
        return {'message': 'Provided filter requires rows '}, 400

    row_filters = [RowFilter(**r) for r in rows_data]
    row_filters.sort(key=lambda x: x.index)
    data_filter = DataFilter(columns=cols_data, rows=row_filters)

    return FileData.get_filtered_data(file_id, limit, offset, data_filter)
