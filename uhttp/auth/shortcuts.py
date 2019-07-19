from .jwt import verify_token
from .session import verify_session
from ..core import Request, Response, HTTPFound
from ..errors import InvalidAuthToken


def auth_required(method=None, *, login_url=None):
    def wrap(original_handler):
        def handler(request):
            token = request.http_variables.get("HTTP_AUTH_TOKEN")
            if not token:
                token = request.http_variables.get("HTTP_COOKIE")
            if token:
                config = request.app.config
                secret = config["secret"]
                header, payload = verify_token(token, secret)
                session_id = payload["sid"]
                admins = config.get("admins", [])
                username = verify_session(session_id, admins)
                if username:
                    return original_handler(request)
            # if token isn't set or invalid, try redirect to login page
            if login_url:
                return HTTPFound(login_url)
            raise InvalidAuthToken(token)
        return handler

    return wrap if method is None else wrap(method)
