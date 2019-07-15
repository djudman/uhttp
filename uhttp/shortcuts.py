from pathlib import Path

from .core import Request, Response
from .errors import InvalidAuthToken


class auth_required:
    def __init__(self, method):
        self._method = method

    def __call__(self, request: Request):
        token = request.http_variables.get("HTTP_AUTH_TOKEN")
        if token in request.app.tokens:
            return self._method(request)
        raise InvalidAuthToken(token)


class html:
    def __init__(self, method, filename, auth_required=False):
        self._method = method
        self._filename = filename
        self._auth_required = auth_required

    def __call__(self, request: Request):
        if self._auth_required:
            self._auth_required = False
            return auth_required(self)(request)
        config = request.app.config
        filepath = Path(config["html_root"], self._filename)
        data = filepath.read_bytes()
        return Response(data, headers=[('Content-Type', 'text/html')])

