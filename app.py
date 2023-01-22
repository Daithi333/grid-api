import io

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from db import get_session, File, View, Filter, Condition, Lookup
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


@app.put("/files")
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

    session = next(get_session())
    file_ = session.query(File).filter_by(id=file_id).one_or_none()
    if not file_:
        return {'message': f'file {file_id!r} not found'}, 404

    file.blob = file.read()
    file_.name = file.filename
    file_.content_type = content_type_full
    session.commit()

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


@app.post("/views")
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
        conditions = [Condition(**c) for c in f['conditions']]
        filter_ = Filter(field=f['field'], filter_type=f['filterType'], operator=f.get('operator'), conditions=conditions)
        filters.append(filter_)

    view = View(file_id=file_id, name=name, fields=fields, filters=filters)
    session = next(get_session())
    session.add(view)
    session.commit()
    session.refresh(view)

    return {"id": view.id}


@app.get("/views")
def get_views():
    session = next(get_session())
    file_id = request.args.get('fileId')
    if not file_id:
        return {'message': 'file_id not found in request'}, 404

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
                'filterType': f.filter_type,
                'operator': f.operator,
                'conditions': [{'operator': c.operator, 'value': c.value} for c in f.conditions]
            }
            for f in view.filters
        ]
    }


@app.delete("/views")
def delete_view():
    view_id = request.args.get('id')
    if not view_id:
        return {'message': 'id not found in request'}, 400

    session = next(get_session())
    view = session.query(View).filter_by(id=view_id).one_or_none()
    if not view:
        return {'message': f'lookup {view_id!r} not found'}, 404

    session.delete(view)
    session.commit()
    return {'success': True}


@app.post("/lookups")
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
                    lookup_file_id=lookup_file_id, lookup_field=lookup_field, operator=operator)
    session = next(get_session())
    session.add(lookup)
    session.commit()
    session.refresh(lookup)

    return {"id": lookup.id}


@app.get("/lookups")
def get_lookups():
    session = next(get_session())
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
            'operator': lookup.operator
        }


@app.delete("/lookups")
def delete_lookup():
    lookup_id = request.args.get('id')
    if not lookup_id:
        return {'message': 'id not found in request'}, 400

    session = next(get_session())
    lookup = session.query(Lookup).filter_by(id=lookup_id).one_or_none()
    if not lookup:
        return {'message': f'lookup {lookup_id!r} not found'}, 404

    session.delete(lookup)
    session.commit()
    return {'success': True}
