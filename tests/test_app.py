import unittest
import os
import threading
import sys
from os.path import realpath, dirname
from uhttp.core import WsgiApplication
from uhttp.client import make_request


class TestWebServer(threading.Thread):
    def __init__(self, app, ready, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.ready = ready

    def run(self):
        from wsgiref.simple_server import make_server
        server = make_server('127.0.0.1', 8000, self.app)
        self.ready.set()
        server.handle_request()
        server.server_close()


def test_handler_empty(request):
    return b''


def test_handler_error(request):
    raise Exception('test')


class TestWsgiApp(unittest.TestCase):
    def setUp(self):
        self.devnull = open(os.devnull, 'w')
        sys.stdout = sys.stderr = self.devnull
        app = WsgiApplication(
        src_root=realpath(dirname(__file__)),
            urls=(
                ('GET', '^/empty$', test_handler_empty),
                ('GET', '^/error$', test_handler_error),
            )
        )
        ready = threading.Event()
        self.server = TestWebServer(app, ready)
        self.server.start()
        ready.wait()

    def tearDown(self):
        self.server.join()
        self.devnull.close()

    def test_empty_response(self):
        response = make_request('http://127.0.0.1:8000/empty')
        self.assertEqual(response, b'')

    def test_server_error(self):
        response = make_request('http://127.0.0.1:8000/error')
        self.assertEqual(response, b'Internal server error')

    def test_not_found(self):
        response = make_request('http://127.0.0.1:8000/notfound')
        self.assertEqual(response, b'Not found')
