from .jwt import verify_token, JwtInvalidSignature
from .session import verify_session
from ..core import Request, Response, HTTPFound
from ..errors import InvalidAuthToken


def auth_required(method=None, *, login_url=None):
    def wrap(original_handler):
        def handler(request):
            try:
                token = request.http_variables.get("HTTP_AUTH_TOKEN")
                if not token:
                    token = request.http_variables.get("HTTP_COOKIE")
                if not token:
                    raise InvalidAuthToken()
                config = request.app.config
                secret = config["secret"]
                _, payload = verify_token(token, secret)
                session_id = payload["sid"]
                admins = config.get("admins", [])
                username = verify_session(session_id, admins)
                if username:
                    return original_handler(request)
                raise InvalidAuthToken(token)
            except Exception as e:
                if login_url:
                    return HTTPFound(login_url)
                raise e
        return handler

    return wrap if method is None else wrap(method)
