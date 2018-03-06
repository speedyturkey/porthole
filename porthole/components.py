import os, sys
from sqlalchemy import select
from . import TimeHelper
from .app import config
from .models import (metadata,
                    automated_reports,
                    automated_report_contacts,
                    automated_report_recipients,
                    report_logs)
from .mailer import Mailer
from .related_record import RelatedRecord
from .queries import QueryGenerator
from .xlsx import WorkbookBuilder
from .logger import PortholeLogger

logger = PortholeLogger(name=__name__)


class Loggable(object):
    """
    Inherit from this class to implement basic error logging. If derived class
    overrides __init__, it must invoke Loggable.__init__() or super().__init__().
    Args:
        log_to  (list): Specify where logged errors should go. Intended to route
            errors from several different types of Loggable objects to one
            place.
    Usage

    class Component(Loggable):
        def __init__(self, log_to=[]):
            super().__init__(log_to=log_to)

    class Report(object):
        def __init__(self):
            self.error_log = []
            self.component = Component(log_to=self.error_log)
    """
    def __init__(self, log_to=[]):
        self.error_log = log_to

    def log_error(self, msg=None):
        """
        Args:
            msg (str) Optional. Appends msg and exception context to error_log
                list as an attribute of the object.
        """
        if not hasattr(self, 'error_log'):
            self.error_log = []
        error_value = sys.exc_info()[1]
        log_record = str(error_value) + ': ' + str(error_value.__doc__)
        if msg:
            log_record = msg + ': ' + log_record
        self.error_log.append(log_record)


class ReportWriter(Loggable):
    """
    The purpose of this class is to use the QueryGenerator and WorkbookBuilder
    together to make an Excel file and populate it with data.
    """
    #TODO: Think of a better name for this class.

    def __init__(self, report_title, log_to=[]):
        self.report_title = report_title
        self.report_file = None
        self.file_path = config['Default'].get('base_file_path')
        self.workbook_builder = None
        self.record_count = 0
        super().__init__(log_to=log_to)

    def build_file(self):
        """
        Loads file and path information and creates XLSX Writer Workbook object.
        Default file is named with convention yyyy-mm-dd - Report Name.xlsx
        """
        try:
            # Construct the file path and create the workbook.
            report_file_name = "{} - {}.xlsx".format(TimeHelper.today(), self.report_title)
            self.report_file = os.path.join(self.file_path, report_file_name)
            self.workbook_builder = WorkbookBuilder(filename=self.report_file)
        except:
            error = "Unable to build file for {}".format(self.report_title)
            logger.error(error)
            self.log_error(error)

    def close_workbook(self):
        """
        Closes workbook object after creation is complete.
        Should always be executed before sending file.
        """
        if self.workbook_builder:
            self.workbook_builder.workbook.close()

    def execute_query(self, cm, query={}, sql=None, increment_counter=True):
        """
        Args:
            cm              (ConnectionManager):
                            Object which contains connection to desired database.
            sheet_name      (str): The name of the worksheet to be created.
            query           (dict): Optional. May contain filename and params for a query
                                to be executed. If included, filename is required.
                    filename      (str): Name of file to be read without extension.
                    params        (dict): Optional. Contains parameter names and values,
                                if applicable. Should only be included along with
                                query_file containing parameter placeholders.
            sql             (str or sqlalchemy.sql.selectable.Select statement):
                                Optional. A SQL query ready for execution.

        Executes SQL and returns QueryResult object, containing data and metadata.
        """
        filename = query.get('filename')
        params = query.get('params')
        q = QueryGenerator(cm=cm, filename=filename, params=params, sql=sql)
        try:
            results = q.execute()
            if increment_counter:
                self.record_count += results.result_count
            return results
        except:
            error = "Unable to execute query {}".format(query.get('filename'))
            logger.error(error)
            self.log_error(error)

    def make_worksheet(self, sheet_name, query_results):
        "Adds worksheet to workbook using provided query results."
        try:
            self.workbook_builder.add_worksheet(sheet_name=sheet_name,
                                                field_names=query_results.field_names,
                                                sheet_data=query_results.result_data
                                            )
        except:
            error = "Unable to add worksheet {}".format(sheet_name)
            logger.error(error)
            self.log_error(error)

    def create_worksheet_from_query(self, cm, sheet_name, query={}, sql=None):
        """
        Args:
            cm              (ConnectionManager):
                            Object which contains connection to desired database.
            sheet_name      (str): The name of the worksheet to be created.
            query           (dict): Optional. May contain filename and params for a query
                                to be executed. If included, filename is required.
                    filename      (str): Name of file to be read without extension.
                    params        (dict): Optional. Contains parameter names and values,
                                if applicable. Should only be included along with
                                query_file containing parameter placeholders.
            sql             (str or sqlalchemy.sql.selectable.Select statement):
                                Optional. A SQL query ready for execution.

        Executes a query and uses results to add worksheet to ReportWriter.workbook_builder.
        """
        results = self.execute_query(cm=cm, query=query, sql=sql)
        self.make_worksheet(sheet_name=sheet_name, query_results=results)


class DatabaseLogger(Loggable):
    """
    Don't want to log if report not active,
    or if logging is not enabled.
    """
    def __init__(self, cm, report_name, log_to=[], log_table='report_logs'):
        self.cm = cm
        self.report_name = report_name
        self.log_table = log_table
        super().__init__(log_to=log_to)

    def create_record(self):
        """
        Inserts new log record into default report logging table
        using RelatedRecord and saves instance of RelatedRecord for updating
        later on with results of report execution.
        """
        report_log = RelatedRecord(self.cm, self.log_table)
        try:
            report_log.insert({'report_name': self.report_name,
                                'started_at': TimeHelper.now(string=False)})
        except:
            self.log_error("Unable to create log record.")
        self.report_log = report_log

    def finalize_record(self, errors=None):
        """Update log at conclusion of report execution to indicate success/failure."""
        if errors:
            data_to_update = {'completed_at': TimeHelper.now(string=False),
                                'success': 0,
                                'error_detail': errors}
        else:
            data_to_update = {'completed_at': TimeHelper.now(string=False),
                                'success': 1}
        try:
            self.report_log.update(data_to_update)
        except:
            self.log_error("Unable to finalize log record.")


class ReportActiveChecker(Loggable):

    def __init__(self, cm, report_name, log_to=[]):
        self.cm = cm
        self.report_name = report_name
        self.active = False
        super().__init__(log_to=log_to)
        self.check_if_active()

    def __bool__(self):
        return self.active

    def check_if_active(self):
        """Queries database to determine if the 'active' attribute for this report
        is set to 1 (active) or 0 (inactive).
        """
        statement = select([automated_reports.c.active])\
                        .where(automated_reports.c.report_name==self.report_name)
        try:
            q = QueryGenerator(cm=self.cm, sql=statement)
            results = q.execute()
            if results.result_data[0]['active'] == 1:
                self.active = True
            else:
                self.active = False
        except IndexError:
            error = "Report {} does not exist".format(self.report_name)
            logger.error(error)
            self.log_error(error)
            raise Exception(error)


class RecipientsChecker(Loggable):
    def __init__(self, cm, report_name, log_to=[]):
        self.cm = cm
        self.report_name = report_name
        self.to_recipients = []
        self.cc_recipients = []
        super().__init__(log_to=log_to)

    def get_recipients(self):
        """Performs lookup in database for report recipients based on report name."""
        statement = select([automated_report_contacts.c.email_address,
                            automated_report_recipients.c.recipient_type])\
                        .select_from(automated_reports\
                        .join(automated_report_recipients)\
                        .join(automated_report_contacts))\
                        .where(automated_reports.c.report_name==self.report_name)
        try:
            q = QueryGenerator(cm=self.cm, sql=statement)
            results = q.execute()
            for recipient in results.row_proxies:
                if recipient.recipient_type == 'to':
                    self.to_recipients.append(recipient.email_address)
                else:
                    self.cc_recipients.append(recipient.email_address)
        except:
            error = "Error getting recipients for {}".format(self.report_name)
            logger.error(error)
            self.log_error(error)
        if not self.to_recipients:
            error = "No primary recipient found for {}".format(self.report_name)
            logger.error(error)
            raise KeyError("No primary recipient found for {}".format(self.report_name))
        return self.to_recipients, self.cc_recipients


class ReportErrorNotifier(object):

    def __init__(self, report_title, error_log):
        self.report_title = report_title
        self.notification_recipient = config['Default'].get('notification_recipient')
        self.error_log = error_log
        self.notified = False

    def send_log_by_email(self):
        email = Mailer()
        email.recipients = [self.notification_recipient]
        email.cc_recipients = ['']
        email.subject = "Report Failure: {}".format(self.report_title)
        email.message = self.construct_message()
        email.attachments = []
        email.send_email()
        self.notified = True

    def construct_message(self):
        msg = """Execution of the following report failed: {}

The following errors were logged:\n""".format(self.report_title)
        msg = msg.format(self.report_title)
        for i, error in enumerate(self.error_log, 1):
            msg += str(i) + '. ' + error + '\n'
        return msg
