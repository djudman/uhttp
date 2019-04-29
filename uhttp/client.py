import ssl
from http.client import HTTPSConnection, HTTPConnection
from urllib.parse import urlencode, urlparse


def make_request(url, method='GET', params=None, body=None, headers=None):
    parse_result = urlparse(url)
    protocol = parse_result.scheme
    hostname = parse_result.netloc
    if protocol == 'https':
        context = ssl.SSLContext()
        conn = HTTPSConnection(hostname, context=context)
    elif protocol == 'http':
        conn = HTTPConnection(hostname)
    else:
        raise Exception('Unsupported protocol {}'.format(protocol))
    if headers is None:
        headers = {}
    if method == 'POST':
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        if params and not body:
            body = urlencode(params)
    request_url = f'{parse_result.path}?{parse_result.query}'
    conn.request(method, request_url, body, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data
