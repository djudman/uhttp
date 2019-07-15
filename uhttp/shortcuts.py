from pathlib import Path

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


class html:
    def __init__(self, method, filename, auth_required=False):
        self._method = method
        self._filename = filename
        self._auth_required = auth_required

    def __call__(self, request: Request):
        if self._auth_required:
            _check_auth_token(request)
        config = request.app.config
        filepath = Path(config["html_root"], self._filename)
        data = filepath.read_bytes()
        return Response(data, headers=[('Content-Type', 'text/html')])

