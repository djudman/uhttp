from .main import handle_request


def urls(config):
    secret = config['secret']
    return (
        ('GET', f'^/{secret}$', handle_request)
    )
