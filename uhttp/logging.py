import json
import logging
import sys
from logging import StreamHandler, Formatter


class DummyFormatter(Formatter):
    def format(self, record):
        return json.dumps(record.msg)


def default_logger():
    stream_handler = StreamHandler(sys.stdout)
    formatter = DummyFormatter()
    stream_handler.setFormatter(formatter)
    logger = logging.getLogger('uhttp')
    logger.setLevel('INFO')
    logger.addHandler(stream_handler)
    return logger
