from time import time

from httpd import default_handler


def urls(config):
    path = config['path']
    return (
        ('GET', f'^/{path}$', lambda request: f'{time()}\n'),
        ('GET', '^.*$', default_handler),
    )
