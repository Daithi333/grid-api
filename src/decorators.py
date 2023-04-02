from functools import wraps

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from context import init_user_id


def jwt_user_required():
    """Same as the default jwt_required but sets the user id in context variable """
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
