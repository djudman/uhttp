from functools import partial
from pathlib import Path

from .core import Request, Response
from .shortcuts import _check_auth_token


class file:
    def __init__(self, filename, content_type="application/octet-stream",
                 auth_required=False):
        self._filename = filename
        self._content_type = content_type
        self._auth_required = auth_required

    def __call__(self, request: Request):
        if self._auth_required:
            _check_auth_token(request)
        config = request.app.config
        filepath = Path(config["html_root"], self._filename)
        data = filepath.read_bytes()
        return Response(data, headers=[('Content-Type', self._content_type)])


html = partial(file, content_type="text/html")
