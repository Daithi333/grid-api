from typing import List

from database import db_session
from database.models import Permission
from enums import Role
from error import NotFoundError, BadRequestError
from services import UserService


class PermissionService:

    @classmethod
    def get(cls, id_: str = None, file_id: str = None, user_id: str = None, internal: bool = False) -> Permission or dict:
        filters = {}
        if id_:
            filters['id'] = id_
        elif file_id and user_id:
            filters['file_id'] = file_id
            filters['user_id'] = user_id
        else:
            raise BadRequestError('Get permission requires with the id or file id and user id')

        session = db_session.get()
        permission = session.query(Permission).filter_by(**filters).one_or_none()
        if not permission:
            raise NotFoundError(f'Permission not found for user {user_id!r} and file {file_id!r}')

        return permission if internal else cls._permission_to_dict(permission)

    @classmethod
    def list(cls, file_id: str = None, user_id: str = None) -> List[dict]:
        filters = {}
        if file_id:
            filters['file_id'] = file_id
        if user_id:
            filters['user_id'] = user_id

        session = db_session.get()
        permissions = session.query(Permission).filter_by(**filters).all()
        return [cls._permission_to_dict(p) for p in permissions]

    @classmethod
    def create(cls, file_id: str, role: str, user_id: str = None, user_email: str = None) -> dict:
        if user_id is None and user_email is None:
            raise BadRequestError('User id or email not provided')

        user = UserService.get(id_=user_id, email=user_email)
        if not user:
            raise NotFoundError('User is not recognised')

        try:
            role = Role[role]
        except KeyError:
            raise BadRequestError(f'Invalid role provided: {role!r}')

        try:
            cls.get(file_id, user.id)
            user_str = user_email if user_email is not None else user_id
            raise BadRequestError(f'User {user_str!r} already has role {role.name!r} for file {file_id!r}')
        except NotFoundError:
            pass  # doesn't exist so proceed

        session = db_session.get()
        permission = Permission(
            file_id=file_id,
            user_id=user.id,
            role=role
        )
        session.add(permission)
        session.commit()
        return cls._permission_to_dict(permission)

    @classmethod
    def update(cls, id_: str, role: Role) -> dict:
        session = db_session.get()
        permission = cls.get(id_=id_, internal=True)
        permission.role = role
        session.commit()
        return cls._permission_to_dict(permission)

    @classmethod
    def delete(cls, id_: str):
        session = db_session.get()
        permission = cls.get(id_=id_, internal=True)
        session.delete(permission)
        session.commit()
        return True

    @classmethod
    def _permission_to_dict(cls, permission: Permission) -> dict:
        return {
            'id': permission.id,
            'fileId': permission.file_id,
            'role': permission.role.name,
            'user': {
                'id': permission.user.id,
                'firstname': permission.user.firstname,
                'lastname': permission.user.lastname,
                'email': permission.user.email
            }
        }
