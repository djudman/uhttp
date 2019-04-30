from httpd import default_handler, get_current_time


def urls(config):
    path = config['path']
    return (
        ('GET', f'^/{path}$', get_current_time),
        ('GET', '^.*$', default_handler),
    )
