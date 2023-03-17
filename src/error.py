
class APIError(Exception):
    def __init__(self, message):
        self.message = message

    def as_dict(self):
        return self.__dict__


class NotFoundError(APIError):
    pass


class BadRequestError(APIError):
    pass


class UnauthorizedError(APIError):
    pass


def handle_not_found(e):
    return e.as_dict(), 404


def handle_bad_request(e):
    return e.as_dict(), 400


def handle_unauthorized(e):
    return e.as_dict(), 401
