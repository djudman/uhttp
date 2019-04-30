import logging
import sys
from logging import StreamHandler, Formatter


class DummyFormatter(Formatter):
    def format(self, record):
        return record.msg


def create_logger(log_level='WARNING'):
    stream_handler = StreamHandler(sys.stdout)
    formatter = DummyFormatter()
    stream_handler.setFormatter(formatter)
    logger = logging.getLogger('uhttp')
    logger.setLevel(log_level)
    logger.addHandler(stream_handler)
    return logger
