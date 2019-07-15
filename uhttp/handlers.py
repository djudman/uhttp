from functools import partial
from pathlib import Path

from .core import Request, Response
from .shortcuts import auth_required as authenticated


class file:
    def __init__(self, filename, content_type="application/octet-stream",
                 auth_required=False, login_url=None):
        self._filename = filename
        self._content_type = content_type
        self.__read_file = authenticated(self._read_file, login_url=login_url) \
                           if auth_required else self._read_file

    def _read_file(self, request):
        config = request.app.config
        filepath = Path(config["html_root"], self._filename)
        return filepath.read_bytes()

    def __call__(self, request: Request):
        data = self.__read_file(request)
        return Response(data, headers=[('Content-Type', self._content_type)])


html = partial(file, content_type="text/html")
