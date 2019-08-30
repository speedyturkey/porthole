from porthole import config
from porthole.connections import ConnectionPool
from porthole.components import (
    DatabaseLogger,
    PortholeLogger,
    ReportActiveChecker
)


class DataTask:
    """
    DataTask is meant to be used when you would like to run some arbitrary function with basic Porthole-style
    logging and error handling. The task name must be defined in the `automated_reports` table.
    If the callable task function executes without raising an exception, successful execution will be recorded.
    If an exception is raised by the task function, a failed execution will be recorded along with the exception. The
    exception will be raised, and should therefore be handled in any application code.
    """
    def __init__(self, task_name, task_function, logging_enabled=True, log_to_db=False):
        if not callable(task_function):
            raise TypeError(
                f"DataTask <{task_name}> requires a callable task function, but <{task_function}> is not callable."
            )
        self.task_name = task_name
        self.task_function = task_function
        self.logging_enabled = logging_enabled
        self.logger = PortholeLogger(
            task_name,
            log_to_db=log_to_db
        )
        self.default_db = config['Default'].get('database')
        self.conns = ConnectionPool(dbs=[self.default_db], logger=self.logger)
        self.db_logger = None
        self.active = None
        self.success = None
        self.check_if_active()
        if self.active and self.logging_enabled:
            self.initialize_db_logger()

    def get_conn(self, db):
        return self.conns.pool.get(db)

    def add_conn(self, db):
        return self.conns.add_connection(db)

    def initialize_db_logger(self):
        self.db_logger = DatabaseLogger(
            cm=self.get_conn(self.default_db),
            report_name=self.task_name,
            logger=self.logger
        )
        self.db_logger.create_record()

    def check_if_active(self):
        self.active = ReportActiveChecker(
            cm=self.get_conn(self.default_db),
            report_name=self.task_name,
            logger=self.logger
        )

    def execute(self):
        err = None
        try:
            if self.active:
                self.task_function()
                self.success = True
        except Exception as e:
            err = e
            self.success = False
            self.logger.exception(e)
        finally:
            if self.db_logger is not None:
                self.db_logger.finalize_record()
            self.conns.close_all()
            if err is not None:
                raise err
