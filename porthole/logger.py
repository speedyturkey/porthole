import logging
import traceback
import warnings
from logging.handlers import TimedRotatingFileHandler
import sqlalchemy as sa
from .app import config
from .models import report_log_details


class PortholeLogger(object):
    """
    Logger class. Log to console by default with optional
    logging to file.
    Set behavior in config.ini:
        log_to_file (bool): Whether to write log to file.
        logfile (str):      Name of file to write to.
        logging_db (str):   Name of database connection to write to, if applicable.
    """

    DEFAULT_FORMAT = '%(levelname)s -- %(asctime)s -- %(name)s -- %(message)s'
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(
            self,
            name: str,
            logfile: str = None,
            log_to_db: bool = False,
            log_table: sa.table = report_log_details,
            fmt: str = DEFAULT_FORMAT,
            datefmt: str = DEFAULT_DATE_FORMAT
    ):
        self.log_format = fmt
        self.date_format = datefmt
        self.formatter = None
        log_to_file = config['Logging'].getboolean('log_to_file', False)
        self.logfile = logfile or config['Logging'].get('logfile', None)
        self.log_table = log_table

        self.rotate_logs = config['Logging'].getboolean('rotate_logs', False)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.create_formatter()
        self.add_stream_handler()
        self.error_buffer = ErrorBuffer()
        self.logger.addHandler(self.error_buffer)
        if log_to_file:
            self.add_file_handler()
        if log_to_db:
            self.add_db_handler()

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

    def add_db_handler(self):
        log_db = config['Logging'].get('logging_db')
        if not log_db:
            self.warning("log_to_db is set to true, but logging_db is not set. Will not log to database.")
            return
        handler = DBHandler(database=log_db, table=self.log_table)
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


class DBHandler(logging.Handler):
    def __init__(self, database=None, table: sa.Table = None):
        logging.Handler.__init__(self)
        self.database = database
        self.table = table

    def emit(self, record):
        if record.exc_info:
            trace = traceback.format_exc()
        else:
            trace = None
        data = {
            'level_number': record.levelno,
            'level_name': record.levelname,
            'msg': record.msg,
            'logger': record.name,
            'traceback': trace
        }
        self._log_record_to_db(data)

    def _log_record_to_db(self, log_data: dict):
        from .connections import ConnectionManager
        statement = self.table.insert().values(**log_data)
        try:
            with ConnectionManager(self.database) as cm:
                cm.conn.execute(statement)
        except Exception as e:
            warnings.warn(f"Exception when writing log to database: {e}")


class ErrorBuffer(logging.handlers.BufferingHandler):
    def __init__(self, capacity: int = 1024):
        super().__init__(capacity=capacity)
        self.setLevel(logging.ERROR)

    @property
    def empty(self):
        return len(self.buffer) == 0
