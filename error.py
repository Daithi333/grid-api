
class NotFoundError(Exception):
    pass


class BadRequestError(Exception):
    pass


def handle_not_found(e):
    return {'message': str(e)}, 404


def handle_bad_request(e):
    return {'message': str(e)}, 400
