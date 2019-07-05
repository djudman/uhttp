import os
import sys
from os.path import dirname, realpath

sys.path.append(dirname(dirname(dirname(realpath(__file__)))))

from uhttp.core import WsgiApplication


def run_app(app: WsgiApplication, welcome_message=""):
    from wsgiref.simple_server import make_server
    server = make_server("127.0.0.1", 8000, app)
    print(welcome_message)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app = WsgiApplication(
        src_root=realpath(dirname(__file__)),
        urls=(
            ("GET", "^.*$", lambda request: f"{request.path}\n"),
        )
    )
    run_app(app, "Echo app started on port 8000...\nJust do request like "
                 "`curl -X GET --http1.1 http://127.0.0.1:8000/foo` and you "
                 "will get `/foo` as response\n")
