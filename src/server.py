import logging

from gunicorn.app.base import BaseApplication
from gunicorn.instrument.statsd import Statsd

from logger import FORMAT, DATE_FORMAT

ACCESS_FORMAT = '%(m)s %(U)s %(s)s'
GUNICORN_LEVEL = 'INFO'


class ExcelApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def init(self, parser, opts, args):
        pass

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


class GunicornErrorLogHandler(logging.StreamHandler):
    pass


class GunicornAccessLogHandler(logging.StreamHandler):
    def emit(self, record):
        record.metadata = {
            "host": record.args["h"],
            "method": record.args["m"],
            "url": record.args["f"],
            "path": record.args["U"],
            "status_code": record.args["s"]
        }

        msg = self.format(record)

        self.stream.write(msg + self.terminator)
        self.flush()


class CustomGunicornLogger(Statsd):

    def setup(self, cfg):
        super().setup(cfg)

        error_log_handler = GunicornErrorLogHandler()
        error_log_handler.setFormatter(logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT))
        self.error_log.handlers = [error_log_handler]

        access_log_handler = GunicornAccessLogHandler()
        access_log_handler.setFormatter(logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT))
        self.access_log.handlers = [access_log_handler]