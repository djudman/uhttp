from time import time
from os.path import dirname, realpath
from uhttp import WsgiApplication


def default_handler(request):
    path = request.app.config['path']
    return f'Invalid path `{request.path}`. Try `/{path}`\n'


def get_current_time(request):
    return f'{time()}\n'


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    app = WsgiApplication(
        src_root=realpath(dirname(__file__)),
        config={'path': 'time'},
    )
    server = make_server('127.0.0.1', 8000, app)
    print(
        'Time app started on port 8000...\n'
        'Just do request like `curl -X GET --http1.1 http://127.0.0.1:8000/time` and you will get the current time as response\n'
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
