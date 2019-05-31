import json
import traceback
from time import time
from urllib.parse import parse_qsl

from .router import UrlRouter
from .logging import create_logger


class Request:
    def __init__(self, wsgi_environ):
        self.create_time = time()
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
        if not self.body and self.input and self.content_length > 0:
            self.body = self.input.read(self.content_length) # TODO: Whether can input be closed?
        return self.body

    def json(self):
        if not self.body:
            self.read()
        data = self.body.decode()
        return json.loads(data)

    def __to_dict__(self):
        body = (self.body and self.body.decode()) or self.read()  # TODO: to check `Content-Type` header. If it is `application/octet-stream`, then to convert data to base64.
        data = {
            'create_time': self.create_time,
            'body': body,
        }
        for name, value in self._wsgi_environ.items():
            if isinstance(value, str) or isinstance(value, int):
                data[name] = value
        return data

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return json.dumps(self.__to_dict__())

    # def __repr__(self):
    #     return f'Request({self._wsgi_environ})'


class Response:
    statuses = {
        200: 'OK',
        301: 'Moved Permanently',
        302: 'Found',
        404: 'Not Found',
        500: 'Internal Server Error',
    }

    def __init__(self, body, status_code=200, headers=None, *, exception=None):
        self.create_time = time()
        self.body = body if body else b''
        if isinstance(self.body, str):
            self.body = self.body.encode()
        elif isinstance(self.body, bytes):
            pass
        else:
            raise Exception('Parameter `body` must have `str` or `bytes` type.')
        content_length = len(self.body)
        response_headers = []
        if content_length > 0:
            response_headers.append(('Content-Length', str(content_length)))
        if headers:
            for name, value in headers:
                response_headers.append((name, value))
        else:
            response_headers.append(('Content-Type', 'text/plain'))
        self.headers = response_headers
        status_message = self.statuses.get(status_code, 'Unknown')
        self.status_code = status_code
        self.status = f'{status_code} {status_message}'
        self.exception = exception

    def __to_dict__(self):
        body = self.body.decode()  # TODO: to check `Content-Type` header. If it is `application/octet-stream`, then to convert data to base64.
        data = {
            'create_time': self.create_time,
            'body': body,
            'headers': self.headers,
            'status': self.status,
        }
        if self.exception:
            tb = self.exception.__traceback__
            data['exception'] = ''.join(traceback.format_tb(tb))
        return data

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return json.dumps(self.__to_dict__())

    # def __repr__(self):
    #     return f'Response({self.body}, {self.status_code}, {self.headers}, exception={self.exception})'

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
        response = None
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
                response = Response(body=b'Not found', status_code=404)
        except Exception as e:
            response = Response(body=b'Internal server error', status_code=500, exception=e)
        finally:
            self.log_request(request, response)
        return response.status, response.headers, response.body

    def log(self, *, level='info', message=None, data=None):
        level = level.lower()
        log_entry = {
            'ts': time(),
            'level': level.lower(),
        }
        if message is not None:
            if not isinstance(message, str):
                raise Exception('Invalid type for parameter `message`. Expected `string`')
            log_entry['message'] = message
        if data is not None:
            if not isinstance(data, dict):
                raise Exception('Invalid type for parameter `data`. Expected `dict`')
            log_entry.update(data)
        print(json.dumps(log_entry))

    def log_request(self, request, response):
        message = {
            'ts': time(),
            'request': request.__to_dict__(),
            'response': response.__to_dict__(),
        }
        first_digit = response.status_code // 100
        if response.exception:
            level = 'fatal'
        elif first_digit == 5:
            level = 'error'
        elif first_digit == 4:
            level = 'warning'
        else:
            level = 'info'
        message['level'] = level
        log_function = getattr(self.logger, level)
        log_function(json.dumps(message))

    def __call__(self, environ, start_response):
        status, response_headers, response_body = self.wsgi_request(environ)
        start_response(status, response_headers)
        return [response_body]
