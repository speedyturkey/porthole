import logging
from logging.handlers import TimedRotatingFileHandler
from .app import config


class PortholeLogger(object):
    """
    Logger class. Log to console by default with optional
    logging to file.
    Set behavior in config.ini:
        log_to_file (bool): Whether to write log to file.
        logfile (str):      Name of file to write to.
    """

    DEFAULT_FORMAT = '%(levelname)s -- %(asctime)s -- %(name)s -- %(message)s'
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, name, logfile=None, fmt=DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT):
        self.log_format = fmt
        self.date_format = datefmt
        self.formatter = None
        log_to_file = config['Logging'].getboolean('log_to_file', False)
        self.logfile = logfile or config['Logging'].get('logfile', None)
        self.rotate_logs = config['Logging'].getboolean('rotate_logs', False)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.create_formatter()
        self.add_stream_handler()
        if log_to_file:
            self.add_file_handler()

    def create_formatter(self):
        self.formatter = logging.Formatter(
            fmt=self.log_format,
            datefmt=self.date_format
        )

    def add_stream_handler(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(stream_handler)

    def add_file_handler(self):
        if self.rotate_logs:
            self.add_rotating_file_handler()
        else:
            handler = logging.FileHandler(self.logfile)
            handler.setFormatter(self.formatter)
            self.logger.addHandler(handler)

    def add_rotating_file_handler(self):
        interval_type = config['Logging.get'].get('rotation_interval_type', 'h')
        interval_magnitude = config['Logging'].get('rotation_interval_magnitude', 1)
        backup_count = config['Logging'].get('backup_count', 0)
        handler = TimedRotatingFileHandler(
            filename=self.logfile,
            when=interval_type,
            interval=interval_magnitude,
            backupCount=backup_count
        )
        self.logger.addHandler(handler)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)

    def set_level(self, level):
        self.logger.setLevel(level)
