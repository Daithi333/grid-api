import io

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from db import get_session, File, Filter, FilterRow
from error import NotFoundError, BadRequestError, handle_not_found, handle_bad_request
from file_data import FileData, get_cache_summary
from models.data_filter import RowFilter, DataFilter

app = Flask(__name__)
app.register_error_handler(NotFoundError, handle_not_found)
app.register_error_handler(BadRequestError, handle_bad_request)

CORS(app, resources={r"/*": {"origins": "*"}})


@app.get("/")
def read_root():
    return {"message": "ok"}


@app.post("/files")
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

    session = next(get_session())
    file_ = File(blob=file.read(), name=file.filename, content_type=content_type_full)
    session.add(file_)
    session.commit()
    session.refresh(file_)

    return {"id": file_.id}


@app.get("/files")
def list_files():
    with next(get_session()) as session:
        files = session.query(File).all()
    return jsonify([
        {'id': f.id, 'name': f.name, 'content_type': f.content_type, 'size_bytes ': len(f.blob)} for f in files
    ])


@app.get("/file")
def get_file():
    file_id = request.args.get('id')
    if not file_id:
        return {'message': 'id not provided in request'}, 400

    with next(get_session()) as session:
        file = session.query(File).filter_by(id=file_id).one()

    blob = io.BytesIO(file.blob)
    return send_file(blob, mimetype=file.content_type, as_attachment=True, download_name=file.name)

    # with open(f'out_{file.name}', "wb") as output_file:
    #     output_file.write(file.blob)
    # return {'success': True}


@app.delete("/files")
def delete_file():
    file_id = request.args.get('id')
    if not file_id:
        return {'message': 'id not provided in request'}, 400

    with next(get_session()) as session:
        session.query(File).filter_by(id=file_id).delete()
        session.commit()
    return {'success': True}


@app.get("/file/data")
def get_file_data():
    file_id = request.args.get('id')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    if not file_id:
        return {'message': 'file id not found in request'}, 400

    return FileData.get_data(file_id, limit, offset)


@app.get("/file/filter-data")
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


@app.get("/cache/summary")
def get_cache():
    return get_cache_summary()


@app.post("/filter")
def add_filter():
    name = request.json.get('name')
    columns = request.json.get('columns')
    rows_data = request.json.get('rows')

    if not name or not columns or not rows_data:
        return {'message': 'filter data missing in request'}, 400

    rows = [FilterRow(**r) for r in rows_data]
    # need to validate indices of filter rows
    filter_ = Filter(name=name, columns=columns, rows=rows)
    session = next(get_session())
    session.add(filter_)
    session.commit()
    session.refresh(filter_)

    return {"id": filter_.id}


@app.get("/filter")
def get_filter():
    filter_id = request.args.get('id')
    if not filter_id:
        return {'message': 'filter id not found in request'}, 400

    with next(get_session()) as session:
        filter_ = session.query(Filter).filter_by(id=filter_id).one_or_none()

        if not filter_:
            return {'message': f'filter {filter_id} not found'}, 404

        return {
            'id': filter_.id,
            'name': filter_.name,
            'columns': filter_.columns,
            'rows ': [
                {
                    'id': r.id, 'column': r.column, 'operator': r.operator, 'value': r.value, 'index': r.index
                } for r in filter_.rows
            ]
        }


@app.get("/filters")
def list_filters():
    with next(get_session()) as session:
        filters = session.query(Filter).all()
        return jsonify([
            {
                'id': f.id,
                'name': f.name,
                'columns': f.columns,
                'rows ': [
                    {
                        'id': r.id, 'column': r.column, 'operator': r.operator, 'value': r.value, 'index': r.index
                    } for r in f.rows
                ]
            } for f in filters
        ])


@app.delete("/filters")
def delete_filter():
    filter_id = request.args.get('id')
    if not filter_id:
        return {'message': 'id not provided in request'}, 400

    with next(get_session()) as session:
        session.query(File).filter_by(id=filter_id).delete()
        session.commit()
    return {'success': True}
