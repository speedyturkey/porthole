from porthole import config
from porthole.app import Session
from porthole.connections import ConnectionPool
from porthole.components import (
    PortholeLogger,
)
from porthole.models import AutomatedReport, ReportLog


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
        self.active = None
        self.success = None
        self.session = Session()
        self.report_record = None
        self.initialize_report_record()
        disable_report_logs = config['Logging'].getboolean('disable_report_logs', False)
        should_log = self.logging_enabled and not disable_report_logs
        if self.active and should_log:
            self.report_log = ReportLog(report_name=self.task_name)
        else:
            self.report_log = None

    def get_conn(self, db):
        return self.conns.pool.get(db)

    def add_conn(self, db):
        return self.conns.add_connection(db)

    def initialize_report_record(self):
        self.report_record = self.session.query(AutomatedReport).filter_by(report_name=self.task_name).one()
        self.active = self.report_record.active

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
            if self.report_log is not None:
                self.report_log.finalize(errors=self.logger.error_buffer.buffer[:])
            self.conns.close_all()
            if err is not None:
                raise err
