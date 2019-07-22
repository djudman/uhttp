import json
import hashlib

from ..core import Request, Response
from .jwt import create_token
from .session import create_session


def login(request: Request):
    data = json.loads(request.body)
    username = data["username"]
    password = data["password"]
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    config = request.app.config
    admins = config["admins"]
    for admin_username, admin_password_hash in admins:
        if admin_username == username and admin_password_hash == password_hash:
            sid = create_session(admin_username, admin_password_hash)
            jwt_token = create_token({"sid": sid}, config["secret"])
            headers = [
                ("Set-Cookie", f"token={jwt_token}; Secure; SameSite=Strict;"),
            ]
            return Response(jwt_token, headers=headers)
