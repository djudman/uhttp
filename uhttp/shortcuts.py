from .core import Request, Response, HTTPFound
from .errors import InvalidAuthToken


class auth_required:
    def __init__(self, method, login_url=None):
        self._method = method
        self._login_url = login_url

    def __call__(self, request: Request):
        token = request.http_variables.get("HTTP_AUTH_TOKEN")
        if token in request.app.tokens:
            return self._method(request)
        if self._login_url:
            return HTTPFound(self._login_url)
        raise InvalidAuthToken(token)
