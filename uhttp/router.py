import importlib
import os
import re
from os.path import join, exists


class UrlRouter:
    def __init__(self, src_root, config=None):
        if config is None:
            config = {}
        if not isinstance(config, dict):
            raise Exception('Invalid config. Non-empty dict is expected.')
        self.config = config
        url_files = []
        if not exists(src_root):
            raise Exception(f'Invalid source root: `{src_root}`')
        for dirpath, _, files in os.walk(src_root):
            paths = [join(dirpath, filename) for filename in files if filename == 'urls.py']
            url_files.extend(paths)
        url_files.sort()
        self.handlers = []
        for filename in url_files:
            urls = self.import_urls(filename)
            for method, regex, handler in urls:
                handler_info = (method, re.compile(regex), handler)
                self.handlers.append(handler_info)

    def import_urls(self, filename):
        spec = importlib.util.spec_from_file_location('urls', filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        urls = module.urls(self.config)
        return urls

    def get_handler(self, url_path, http_method):
        for method, regex_object, handler in self.handlers:
            if method == http_method and regex_object.search(url_path):
                return handler

    def add_route(self, path, callable_handler, *, method='GET'):
        self.handlers.append((method, re.compile(path), callable_handler))
