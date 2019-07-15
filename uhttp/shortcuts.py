from .core import Request, Response, HTTPFound
from .errors import InvalidAuthToken


def auth_required(method=None, *, login_url=None):
    def wrap(original_handler):
        def handler(request):
            token = request.http_variables.get("HTTP_AUTH_TOKEN")
            if token in request.app.tokens:
                return original_handler(request)
            if login_url:
                return HTTPFound(login_url)
            raise InvalidAuthToken(token)
        return handler

    return wrap if method is None else wrap(method)
