import io
import os

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, LargeBinary, String
from sqlalchemy.orm import declarative_base, Session

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(PROJECT_ROOT, 'demo-db.sqlite')
engine = create_engine(f'sqlite:///{db_path}')

Base = declarative_base()


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    content_type = Column(String)
    blob = Column(LargeBinary)


Base.metadata.create_all(engine)

app = Flask(__name__)
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

    with Session(engine) as session:
        file = File(blob=file.read(), name=file.filename, content_type=content_type_full)
        session.add(file)
        session.commit()
        session.refresh(file)
        file_id = file.id

    return {"id": file_id}


@app.get("/files")
def list_files():
    with Session(engine) as session:
        files = session.query(File).all()
    return jsonify([
        {'id': f.id, 'name': f.name, 'content_type': f.content_type, 'size_bytes ': len(f.blob)} for f in files
    ])


@app.get("/file")
def get_file():
    file_id = request.args.get('id')
    if not file_id:
        return {'message': 'id not provided in request'}, 400

    with Session(engine) as session:
        file = session.query(File).filter_by(id=file_id).one()

    blob = io.BytesIO(file.blob)
    return send_file(blob, mimetype=file.content_type, as_attachment=True, download_name=file.name)

    # with open(f'out_{file.name}', "wb") as output_file:
    #     output_file.write(file.blob)
    # return {'success': True}


@app.delete("/files")
def delete_files():
    with Session(engine) as session:
        session.query(File).delete()
        session.commit()
    return {'success': True}
