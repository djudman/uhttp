import json
import io
import unittest

from uhttp import Request, WsgiApplication
from uhttp.auth import login

from uhttp.auth.jwt import verify_token
from uhttp.auth.session import verify_session


class TestLogin(unittest.TestCase):
    def test_login(self):
        data = json.dumps({"username": "root", "password": "root"}).encode()
        wsgi_input = io.BytesIO(data)
        env = {
            "wsgi.input": wsgi_input,
            "CONTENT_LENGTH": len(data),
        }
        request = Request(env)
        config = {
            "secret": "secret",
            "admins": [
                ("root", "4813494d137e1631bba301d5acab6e7bb7aa74ce1185d456565ef51d737677b2")
            ],
        }
        request.app = WsgiApplication('.', config=config)
        request.read()
        response = login(request)
        header, payload = verify_token(response.body.decode(), "secret")
        session_id = payload["sid"]
        admins = config["admins"]
        username = verify_session(session_id, admins)
        self.assertEqual(username, "root")

