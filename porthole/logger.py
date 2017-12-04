import logging
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
        # Get config values
        log_to_file = config['Logging'].getboolean('log_to_file')
        default_logfile = config['Logging'].get('logfile')

        # Create Logger, Formatter, and StreamHandler
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(  fmt=fmt,
                                        datefmt=datefmt)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        if log_to_file:
            logfile = logfile or default_logfile
            file_handler = logging.FileHandler(logfile)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        self.logger = logger
        self.logger.level = logging.INFO

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
