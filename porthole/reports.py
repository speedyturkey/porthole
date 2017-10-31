from .app import config
from .connections import ConnectionPool
from .mailer import Mailer
from .components import (DatabaseLogger,
                         Loggable,
                         RecipientsChecker,
                         ReportActiveChecker,
                         ReportErrorNotifier,
                         ReportWriter)
from .logger import PortholeLogger

logger = PortholeLogger(name=__name__)


class BasicReport(Loggable):
    """
    A basic report with bare minimum functionality.

    Keyword arguments
    :report_title: Used in the filename of the resulting report.

    """
    def __init__(self, report_title):
        # -----------------------------------------
        # Assign arguments to instance attributes.
        # -----------------------------------------
        self.report_title = report_title
        self.attachments = []
        self.report_writer = None
        self.error_log = []
        self.to_recipients = []
        self.cc_recipients = []
        self.email_sent = False
        self.failure_notification_sent = False
        self.file_path = config['Default'].get('base_file_path')
        self.default_db = config['Default'].get('database')
        self.conns = ConnectionPool([self.default_db])

    def __del__(self):
        try:
            self.conns.close_all()
        except:
            pass

    def get_conn(self, db):
        return self.conns.pool.get(db)

    def add_conn(self, db):
        return self.conns.add_connection(db)

    def build_file(self):
        report_writer = ReportWriter(report_title=self.report_title, log_to=self.error_log)
        report_writer.build_file()
        self.attachments.append(report_writer.report_file)
        self.report_writer = report_writer

    def create_worksheet_from_query(self,
                                    sheet_name,
                                    db=None,
                                    query={},
                                    sql=None):
        """Delegates functionality to ReportWriter."""
        if db is None:
            db = self.default_db
        cm = self.add_conn(db)
        self.report_writer.create_worksheet_from_query(cm=cm,
                                                        sheet_name=sheet_name,
                                                        query=query,
                                                        sql=sql)

    def make_worksheet(self, sheet_name, query_results):
        """Delegates functionality to ReportWriter."""
        self.report_writer.make_worksheet(sheet_name=sheet_name,
                                            query_results=query_results)

    def build_email(self):
        """Instantiates Mailer object using provided parameters."""
        email = Mailer()
        email.recipients = self.to_recipients
        email.cc_recipients = self.cc_recipients
        email.subject = self.subject
        email.message = self.message
        email.attachments = self.attachments
        self.email = email

    def send_email(self):
        """Executes the send_email method of the Mailer."""
        try:
            self.email.send_email()
            self.email_sent = True
        except Exception as e:
            logger.exception(e)
            self.log_error("Unable to send email")

    def check_whether_to_send_email(self):
        """Determines whether email should be sent based given errors and settings."""
        if self.error_log:
            return False
        else:
            return True

    def build_and_send_email(self):
        """If email should be sent, builds email object and sends email."""
        if self.check_whether_to_send_email():
            self.build_email()
            self.send_email()

    def execute(self):
        """
        After instantiation and setup, and after
        any query results have been added to the workbook,
        this method executes and finalizes the report,
        ensures errors are handled, and performs cleanup.
        """
        if self.report_writer:
            self.report_writer.close_workbook()
        self.build_and_send_email()
        if self.error_log:
            self.send_failure_notification()
        self.conns.close_all()

    def send_failure_notification(self):
        notifier = ReportErrorNotifier( report_title=self.report_title,
                                        error_log=self.error_log)
        notifier.send_log_by_email()
        if notifier.notified:
            self.failure_notification_sent = True


class GenericReport(BasicReport, Loggable):
    """A generic report object to be used to facilitate
    easy setup and configuration of new automated reports.

    Keyword arguments
    :report_title: Used in the filename of the resulting report.
    :report_name: Uniquely identifies a report. Used for recipient lookup
        and logging.
    :logging_enabled: (Optional) Default value of True. If logging is enabled,
        the report will attempt to create a log record each time it is instantiated.
        Only disable if the report needs to be run without connection to the standard
        reporting database.

    Here is an example of sample usage:

    report = GenericReport(
                            report_name='test_report',
                            report_title='Test Report'
                            )
    report.build_file()
    report.create_worksheet_from_query(
                                        sheet_name='Sheet1',
                                        query={'filename': 'test_query'}
                                        )
    report.subject = "Today's Test Report"
    report.message = "Attached is the latest report"
    report.execute()

    Notes on sample code:
    (1) A report is not required to have an attachment,
        but an attachment is assumed.
    (2) An Excel attachment can contain any number
        of worksheets. Simply call create_worksheet_from_query
        with the appropriate query parameters and worksheet
        name, as many times as you like. Worksheet names
        must be valid and unique.
    (3) After providing a subject and message body,
        the execute method will take care of the rest,
        including email circulation, error handling,
        and notification.

    Notes on database configuration:
    (1) Reports must have a record in the automated_reports table,
        including report_name and active flag (1 or 0).
    (2) Reports also must have at least one recipient
        in the automated_report_recipients table, and at least
        one recipient must be designed with a recipient type of
        'to'. Each report can have one or more recipients with
        a recipient type of 'cc'.
    (3) Report recipient records are associated with:
        (a) automated_reports through report_id
        (b) automated_report_contacts through contact_id
    (4) If you need a recipient who is not in the
        automated_report_contacts table, add them to it.

    """
    def __init__(self, report_title, report_name, logging_enabled=True, send_if_blank=True):
        # -----------------------------------------
        # Assign arguments to instance attributes.
        # -----------------------------------------
        super().__init__(report_title=report_title)
        self.report_name = report_name
        self.logging_enabled = logging_enabled
        self.send_if_blank = send_if_blank
        self.check_if_active()
        if self.active:
            self.initialize_db_logger()

    @property
    def record_count(self):
        if self.report_writer:
            return self.report_writer.record_count
        else:
            return 0

    def initialize_db_logger(self):
        self.db_logger = DatabaseLogger( cm=self.get_conn(self.default_db),
                                         report_name=self.report_name,
                                         log_to=self.error_log)
        self.db_logger.create_record()

    def check_if_active(self):
        self.active = ReportActiveChecker(  cm=self.get_conn(self.default_db),
                                            report_name=self.report_name,
                                            log_to=self.error_log)

    def get_recipients(self):
        """Performs lookup in database for report recipients based on report name."""

        checker = RecipientsChecker( cm=self.get_conn(self.default_db),
                                     report_name=self.report_name,
                                     log_to=self.error_log)
        self.to_recipients, self.cc_recipients = checker.get_recipients()

    def check_whether_to_send_email(self):
        """Determines whether email should be sent based given errors, settings, and result count."""
        if self.error_log:
            return False
        elif not self.send_if_blank and self.record_count == 0:
            return False
        else:
            return True

    def execute(self):
        """
        After instantiation and setup, and after
        any query results have been added to the workbook,
        this method executes and finalizes the report,
        ensures errors are handled, and performs cleanup.
        """
        if self.report_writer:
            self.report_writer.close_workbook()
        if self.active:
            self.build_and_send_email()
            self.db_logger.finalize_record()
        if self.error_log:
            self.send_failure_notification()
        self.conns.close_all()




if __name__ == '__main__':
    pass
