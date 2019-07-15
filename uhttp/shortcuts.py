from .core import Request, Response
from .errors import InvalidAuthToken


def _check_auth_token(request: Request):
    token = request.http_variables.get("HTTP_AUTH_TOKEN")
    if token not in request.app.tokens:
        raise InvalidAuthToken(token)


class auth_required:
    def __init__(self, method):
        self._method = method

    def __call__(self, request: Request):
        _check_auth_token(request)
        return self._method(request)
