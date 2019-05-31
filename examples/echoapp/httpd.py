from os.path import dirname, realpath
from uhttp import WsgiApplication


def handle_request(request):
    return f'{request.path}\n'


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    app = WsgiApplication(
        src_root=realpath(dirname(__file__)),
        urls=(
            ('GET', '^.*$', handle_request),
        )
    )
    server = make_server('127.0.0.1', 8000, app)
    print(
        'Echo app started on port 8000...\n'
        'Just do request like `curl -X GET --http1.1 http://127.0.0.1:8000/foo` and you will get `/foo` as response\n'
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
