import sys
from time import time
from os.path import dirname, realpath

sys.path.append(dirname(dirname(dirname(realpath(__file__)))))

from uhttp import WsgiApplication


def default_handler(request):
    path = request.app.config["path"]
    return f"Invalid path `{request.path}`. Try `/{path}`\n"


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
        config={"path": "time"},
    )
    run_app(app, "Time app started on port 8000...\n"
                 "Just do request like `curl -X GET --http1.1 "
                 "http://127.0.0.1:8000/time` and you will get the "
                 "current time as response\n")
