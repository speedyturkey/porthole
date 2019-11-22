import os
from . import TimeHelper
from .app import config
from .connections import ConnectionManager
from .mailer import Mailer
from .queries import QueryGenerator
from .xlsx import WorkbookBuilder
from .logger import PortholeLogger


class ReportWriter:
    """
    The purpose of this class is to use the QueryGenerator and WorkbookBuilder
    together to make an Excel file and populate it with data.
    """
    def __init__(self, report_title, logger=None):
        self.report_title = report_title
        self.report_file = None
        self.file_path = config['Default'].get('base_file_path')
        self.workbook_builder = None
        self.record_count = 0
        self.logger = logger or PortholeLogger(report_title)

    def build_file(self):
        """
        Loads file and path information and creates XLSX Writer Workbook object.
        Default file is named with convention yyyy-mm-dd - Report Name.xlsx
        """
        try:
            # Construct the file path and create the workbook.
            local_timezone = config['Default'].get('local_timezone') or 'UTC'
            today = TimeHelper.today(timezone=local_timezone)
            report_file_name = f"{today} - {self.report_title}.xlsx"
            self.report_file = os.path.join(self.file_path, report_file_name)
            self.workbook_builder = WorkbookBuilder(filename=self.report_file)
        except:
            error = "Unable to build file for {}".format(self.report_title)
            self.logger.exception(error)

    def close_workbook(self):
        """
        Closes workbook object after creation is complete.
        Should always be executed before sending file.
        """
        if self.workbook_builder:
            self.workbook_builder.workbook.close()

    def add_format(self, format_name, format_params):
        self.workbook_builder.add_format(format_name, format_params)

    def execute_query(self, cm, query=None, sql=None, increment_counter=True):
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
        if query is None:
            query = {}
        filename = query.get('filename')
        params = query.get('params')
        q = QueryGenerator(cm=cm, filename=filename, params=params, sql=sql, logger=self.logger)
        try:
            results = q.execute()
            if increment_counter:
                self.record_count += results.result_count
            return results
        except:
            error = "Unable to execute query {}".format(query.get('filename'))
            self.logger.exception(error)

    def make_worksheet(self, sheet_name, query_results, **kwargs):
        """Adds worksheet to workbook using provided query results."""
        try:
            self.workbook_builder.add_worksheet(
                sheet_name=sheet_name,
                field_names=query_results.field_names,
                sheet_data=query_results.result_data,
                **kwargs
            )
        except:
            error = "Unable to add worksheet {}".format(sheet_name)
            self.logger.exception(error)

    def create_worksheet_from_query(self, cm, sheet_name, query=None, sql=None, query_kwargs=None, worksheet_kwargs=None):
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
            query_kwargs    (dict): Optional. Dictionary of keyword arguments to pass to `execute_query`.
            worksheet_kwargs (dict): Optional. Dictionary of keyword arguments to pass to `make_worksheet`

        Executes a query and uses results to add worksheet to ReportWriter.workbook_builder.
        """
        if query is None:
            query = {}
        if query_kwargs is None:
            query_kwargs = {}
        if worksheet_kwargs is None:
            worksheet_kwargs = {}
        results = self.execute_query(cm=cm, query=query, sql=sql, **query_kwargs)
        self.make_worksheet(sheet_name=sheet_name, query_results=results, **worksheet_kwargs)


class ReportErrorNotifier:

    def __init__(self, report_title, error_buffer):
        self.report_title = report_title
        self.notification_recipient = config['Default'].get('notification_recipient')
        self.error_buffer = error_buffer
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
        for i, error in enumerate(self.error_buffer, 1):
            msg += str(i) + '. ' + str(error) + '\n'
        return msg
