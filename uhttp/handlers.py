from pathlib import Path

from .core import Request, Response
from .shortcuts import _check_auth_token


class html:
    def __init__(self, filename, auth_required=False):
        self._filename = filename
        self._auth_required = auth_required

    def __call__(self, request: Request):
        if self._auth_required:
            _check_auth_token(request)
        config = request.app.config
        filepath = Path(config["html_root"], self._filename)
        data = filepath.read_bytes()
        return Response(data, headers=[('Content-Type', 'text/html')])
