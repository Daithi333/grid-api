import inspect
from functools import wraps
from typing import List

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from context import init_user_id, current_user_id, db_session
from database.models import Permission
from error import UnauthorizedError


def jwt_user_required():
    """Same as the default 'jwt_required' but sets the user id in context variable """
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            user_id = str(identity.get('id'))
            init_user_id(user_id)
            return func(*args, **kwargs)

        return decorator

    return wrapper


def enforce_permission(file_id_key: str, required_roles: List[str]):
    """
    Enforce access to a file based on user's role. Decorated function should be passed the file id as a kwarg.
    :param file_id_key: The string name of the kwarg containing the file id
    :param required_roles: Which roles (Role ENUM) the user should have to access the decorated function
    :return:
    """
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            file_id = kwargs[file_id_key]
            user_id = current_user_id.get()
            session = db_session.get()
            permission = (
                session.query(Permission)
                .filter_by(file_id=file_id, user_id=user_id)
                .one_or_none()
            )
            if not permission:
                raise UnauthorizedError('User not permitted to perform action')

            if not any([r for r in ['*', permission.role.name] if r in required_roles]):
                raise UnauthorizedError('Role not permitted to perform action')

            if 'user_role' in inspect.signature(func).parameters:
                kwargs['user_role'] = permission.role

            return func(*args, **kwargs)

        return decorator

    return wrapper
