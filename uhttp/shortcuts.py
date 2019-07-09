from .core import Request
from .errors import InvalidAuthToken


class restricted:
    def __init__(self, method):
        self._method = method

    def __call__(self, request: Request):
        token = request.http_variables.get("HTTP_AUTH_TOKEN")
        if token in request.app.tokens:
            return self._method(request)
        raise InvalidAuthToken(token)
