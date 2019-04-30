import json
from time import time
from urllib.parse import parse_qsl

from .router import UrlRouter
from .logging import create_logger


class Request:
    def __init__(self, wsgi_environ):
        self.init_time = time()
        self.body = None
        self._wsgi_environ = wsgi_environ

        content_length = wsgi_environ.get('CONTENT_LENGTH', 0)  # value of this variable depends on web server. Sometimes it may be '' (an empty string).
        self.content_length = int(content_length) if content_length else 0
        self.user_agent = wsgi_environ.get('HTTP_USER_AGENT')
        self.path = wsgi_environ.get('PATH_INFO', '/')
        self.query_string = wsgi_environ.get('QUERY_STRING')
        self.raw_uri = wsgi_environ.get('RAW_URI')
        self.method = wsgi_environ.get('REQUEST_METHOD', 'GET')
        self.server_protocol = wsgi_environ.get('SERVER_PROTOCOL')
        self.input = wsgi_environ.get('wsgi.input')

        self.GET = {}
        if self.query_string:
            for name, value in parse_qsl(self.query_string):
                self.GET[name] = value

    def read(self):
        data = None
        if self.input and self.content_length > 0:
            data = self.input.read(self.content_length) # TODO: Whether can input be closed?
        if not data and self.body:
            return self.body
        self.body = data
        return data

    def json(self):
        if not self.body:
            self.read()
        data = self.body.decode()
        return json.loads(data)


class Response:
    statuses = {
        200: 'OK',
        301: 'Moved Permanently',
        302: 'Found',
        404: 'Not Found',
        500: 'Internal Server Error',
    }

    def __init__(self, body, status_code=200, headers=None, *, exception=None):
        self.init_time = time()
        self.body = body if body else b''
        if headers is None:
            headers = [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(self.body))),
            ]
        self.headers = headers
        if isinstance(self.body, str):
            self.body = self.body.encode() 
        status_message = self.statuses.get(status_code, 'Unknown')
        self.status_code = status_code
        self.status = '{0} {1}'.format(status_code, status_message)
        self.exception = exception


class HTTPFound(Response):
    def __init__(self, redirect_url):
        headers = [('Location', redirect_url)]
        super().__init__(b'', 302, headers)


class WsgiApplication:
    def __init__(self, src_root, *, urls=None, config=None):
        if config is None:
            config = {}
        self.config = config
        self.router = UrlRouter(src_root, config)
        self.logger = create_logger()
        if urls:
            for method, path, handler in urls:
                self.router.add_route(path, handler, method=method)

    def wsgi_request(self, wsgi_environ):
        request = None
        try:
            request = Request(wsgi_environ)
            request.read()
            handler = self.router.get_handler(request.path, request.method)
            if handler:
                request.app = self
                response = handler(request)
                if isinstance(response, dict):
                    response = Response(body=json.dumps(response))
                elif isinstance(response, str) or isinstance(response, bytes):
                    response = Response(body=response)
                if not isinstance(response, Response):
                    raise Exception(f'Invalid response type `{str(type(response))}`. Expected types: `str` / `bytes` / `dict` / `Response`')
            else:
                response = Response(body=b'Page not found', status_code=404)
        except Exception as e:
            response = Response(body=b'Internal server error', status_code=500, exception=e)
        finally:
            self.log_request(request, response)
        return response.status, response.headers, response.body

    def log_request(self, request, response):
        if response.exception:
            print(response.exception)

    def __call__(self, environ, start_response):
        status, response_headers, response_body = self.wsgi_request(environ)
        start_response(status, response_headers)
        return [response_body]
