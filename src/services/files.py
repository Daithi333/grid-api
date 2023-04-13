import io
from typing import List

from context import db_session, current_user_id
from database.models import File, Permission
from decorators import enforce_permission
from error import NotFoundError, BadRequestError
from services import file_cache


class FileService:
    @classmethod
    @enforce_permission(file_id_key='id_', required_roles=['*'])
    def get(cls, id_: str, internal: bool = False) -> File or dict:
        """
        Get a file. Must pass id_ as kwarg for permission enforcement
        """
        session = db_session.get()
        file = session.query(File).filter_by(id=id_).one_or_none()
        if not file:
            raise NotFoundError(message=f'File {id_!r} not found')

        return file if internal else cls._file_to_dict(file)

    @classmethod
    def list(cls) -> List[dict]:
        session = db_session.get()
        user_id = current_user_id.get()
        files = (
            session.query(File)
            .join(Permission, Permission.file_id == File.id)
            .filter(Permission.user_id == user_id)
            .all()
        )
        return [cls._file_to_dict(f) for f in files]

    @classmethod
    def create(cls, file_bytes: bytes, filename: str, content_type: str, data_types: dict) -> dict:
        if any(f['name'] == filename for f in cls.list()):
            raise BadRequestError(f'Filename {filename!r} already in use')

        session = db_session.get()
        file = File(blob=file_bytes, name=filename, content_type=content_type, data_types=data_types)
        session.add(file)
        session.commit()
        session.refresh(file)
        return cls._file_to_dict(file)

    @classmethod
    @enforce_permission(file_id_key='id_', required_roles=['OWNER'])
    def update(cls, id_: str, file_bytes: bytes, filename: str, content_type: str, data_types: dict):
        session = db_session.get()
        file = cls.get(id_=id_, internal=True)

        if file.name != filename:
            # TODO - check file columns as well
            raise BadRequestError('Replacement does not match existing file')

        file.blob = file_bytes
        file.name = filename
        file.content_type = content_type
        file.data_types = data_types

        for t in file.transactions:
            session.delete(t)

        session.commit()
        file_cache.remove(id_)  # remove old version of file data from cache
        return cls._file_to_dict(file)

    @classmethod
    @enforce_permission(file_id_key='id_', required_roles=['OWNER'])
    def delete(cls, id_: str) -> bool:
        session = db_session.get()
        file = cls.get(id_=id_, internal=True)
        session.delete(file)
        session.commit()
        return True

    @classmethod
    @enforce_permission(file_id_key='id_', required_roles=['*'])
    def download(cls, id_: str) -> (bytes, str, str):
        file = cls.get(id_=id_, internal=True)
        blob = io.BytesIO(file.blob)
        return blob, file.name, file.content_type

    @classmethod
    def _file_to_dict(cls, file: File):
        return {
            'id': file.id,
            'name': file.name,
            'content_type': file.content_type,
            'size_bytes ': len(file.blob)
        }

    @classmethod
    def validate_content_type(cls, content_type):
        content_type_short = content_type.split('.')[0]
        if content_type_short not in ['application/vnd']:
            raise BadRequestError(message=f'unsupported file type {content_type_short!r}')
