
class NotFoundError(Exception):
    pass


class BadRequestError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


def handle_not_found(e):
    return {'message': str(e)}, 404


def handle_bad_request(e):
    return {'message': str(e)}, 400


def handle_unauthorized(e):
    return {'message': str(e)}, 401
