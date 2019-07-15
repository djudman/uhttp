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
    def __init__(self, method, filename):
        self._method = method
        self._filename = filename

    def __call__(self, request: Request):
        config = request.app.config
        filepath = Path(config["html_root"], self._filename)
        data = filepath.read_bytes()
        return Response(data, headers=[('Content-Type', 'text/html')])

