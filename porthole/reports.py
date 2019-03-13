import os
from inspect import getfullargspec
from argparse import ArgumentParser
from .alerts import Alert
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
from .uploaders import S3Uploader

logger = PortholeLogger(name=__name__)


class BasicReport(Loggable):
    """
    A basic report with bare minimum functionality.

    Keyword arguments
    :report_title: Used in the filename of the resulting report.

    """
    def __init__(self, report_title, debug_mode=False, text_format='plain'):
        # -----------------------------------------
        # Assign arguments to instance attributes.
        # -----------------------------------------
        self.report_title = report_title
        self.attachments = []
        self.report_writer = None
        self.error_log = []
        self.to_recipients = []
        self.cc_recipients = []
        self.email = None
        self.subject = None
        self.message = None
        self.debug_mode = debug_mode
        self.text_format = text_format
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
                                    query=None,
                                    sql=None,
                                    query_kwargs=None,
                                    worksheet_kwargs=None):
        """Delegates functionality to ReportWriter."""
        if db is None:
            db = self.default_db
        cm = self.add_conn(db)
        self.report_writer.create_worksheet_from_query(
            cm=cm,
            sheet_name=sheet_name,
            query=query,
            sql=sql,
            query_kwargs=query_kwargs,
            worksheet_kwargs=worksheet_kwargs
        )

    def make_worksheet(self, sheet_name, query_results, **kwargs):
        """Delegates functionality to ReportWriter."""
        self.report_writer.make_worksheet(
            sheet_name=sheet_name,
            query_results=query_results,
            **kwargs
        )

    def build_email(self):
        """Instantiates Mailer object using provided parameters."""
        email = Mailer(
            recipients=self.to_recipients,
            cc_recipients=self.cc_recipients,
            debug_mode=self.debug_mode,
            text_format=self.text_format
        )
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

    def check_whether_to_publish(self):
        """Determines whether email should be sent based given errors and settings."""
        if self.error_log:
            return False
        else:
            return True

    def build_and_send_email(self):
        """If email should be sent, builds email object and sends email."""
        if self.check_whether_to_publish():
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
        notifier = ReportErrorNotifier(
            report_title=self.report_title,
            error_log=self.error_log
        )
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
    def __init__(self, report_title, report_name, logging_enabled=True, send_if_blank=True,
                 publish_to='email', debug_mode=False, text_format='plain'):
        # -----------------------------------------
        # Assign arguments to instance attributes.
        # -----------------------------------------
        super().__init__(report_title=report_title, debug_mode=debug_mode, text_format=text_format)
        self.report_name = report_name
        self.logging_enabled = logging_enabled
        self.send_if_blank = send_if_blank
        if publish_to.lower() not in ['s3', 'email', 'both']:
            raise ValueError("Reports can only be published to s3 or email.")
        self.publish_to = publish_to.lower()
        self.db_logger = None
        self.active = None
        self.uploaded_to_s3 = False
        self.check_if_active()
        if self.active and self.logging_enabled:
            self.initialize_db_logger()

    @property
    def record_count(self):
        if self.report_writer:
            return self.report_writer.record_count
        else:
            return 0

    def initialize_db_logger(self):
        self.db_logger = DatabaseLogger(
            cm=self.get_conn(self.default_db),
            report_name=self.report_name,
            log_to=self.error_log
        )
        self.db_logger.create_record()

    def check_if_active(self):
        self.active = ReportActiveChecker(
            cm=self.get_conn(self.default_db),
            report_name=self.report_name,
            log_to=self.error_log
        )

    def get_recipients(self):
        """Performs lookup in database for report recipients based on report name."""

        checker = RecipientsChecker(
            cm=self.get_conn(self.default_db),
            report_name=self.report_name,
            log_to=self.error_log
        )
        self.to_recipients, self.cc_recipients = checker.get_recipients()

    def check_whether_to_publish(self):
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
            if self.check_whether_to_publish():
                self.publish()
            if self.db_logger is not None:
                self.db_logger.finalize_record()
        if self.error_log:
            self.send_failure_notification()
        self.conns.close_all()

    def publish(self):
        if self.publish_to == 'email':
            self.build_and_send_email()
        elif self.publish_to == 's3':
            self.upload_to_s3()
        elif self.publish_to == 'both':
            self.build_and_send_email()
            self.upload_to_s3()

    def upload_to_s3(self):
        try:
            uploader = S3Uploader(debug_mode=self.debug_mode)
            uploaded = []
            for attachment in self.attachments:
                success = uploader.upload_file(key=os.path.basename(attachment), filename=attachment)
                uploaded.append(success)
            self.uploaded_to_s3 = all(uploaded)
        except:
            self.log_error_detail("Unable to upload to S3")


class ReportRunner(ArgumentParser):
    def __init__(self, report_map=None):
        super().__init__(description="Runs the report designated by the -r or --report parameter. To see a list of available reports, use -l or --list.")
        self.add_argument("-l", "--list", action='store_true', dest='list', help="show a list of available reports")
        self.add_argument("-r", "--report", dest='report', help="name of report to run")
        self.add_argument("-d", "--debug", action='store_true', dest='debug_mode', help="run the requested report in debug mode, if defined")
        self.add_argument("-p", "--ping", action='store_true', dest='ping', help="this is used for health checking.")
        self.args, _ = super().parse_known_args()
        self.report_map = report_map if report_map is not None else {}

    def handle_args(self):
        if self.args.list:
            self.list_reports()
        elif self.args.report:
            self.run_report()

    def list_reports(self):
        print("The following reports are available to run:")
        for report in self.report_map.keys():
            print(report)

    def run_report(self):
        report_name = self.args.report
        report_function = self.report_map.get(report_name)
        if report_function:
            if 'debug_mode' in getfullargspec(report_function).args:
                logger.info(f"Received call to run {report_name} in debug mode.")
                report_function(debug_mode=self.args.debug)
            else:
                logger.info(f"Received call to run {report_name}")
                report_function()
        else:
            self.send_unmapped_report_alert()
            error_message = "Report Runner is unable to run: {}. There is no report function mapped to this name".format(report_name)
            logger.error(error_message)
            raise ValueError(error_message)

    def send_unmapped_report_alert(self):
        alert = Alert(
            subject=f"Attempt to execute unmapped report <{self.args.report}>",
            message="Check to ensure report mapping is correct.",
            recipients=[config['Admin']['admin_email']]
        )
        alert.send()


if __name__ == '__main__':
    pass
