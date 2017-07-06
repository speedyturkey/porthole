from .app import config
from .mailer import Mailer

class ReportWriter(object):
    """
    The purpose of this class is to use the QueryGenerator and WorkbookBuilder
    together to make an Excel file and populate it with data.
    """
    #TODO: Think of a better name for this class.

    def __init__(self, report_title, error_logger=None):
        self.report_title = report_title
        self.filename = None
        self.file_path = config['Default'].get('base_file_path')
        self.record_count = 0
        self.error_logger = error_logger

    def log_error(self, msg):
        if self.error_logger:
            self.error_logger.log_error(msg)
        else:
            print(msg)

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
            self.log_error("Unable to build file")

    def close_workbook(self):
        """
        Closes workbook object after creation is complete.
        Should always be executed before sending file.
        """
        if self.workbook_builder:
            self.workbook_builder.workbook.close()

    def execute_query(self, cm, query_file=None, query_params=None, sql=None, increment_counter=True):
        """
        Args:
            cm              (ConnectionManager): Object which contains connection to desired database.
            query_file      (str): Optional. Name of file to be read without extension.
            query_params    (dict): Optional. Contains parameter names and values if applicable.
                                Should only be included along with query_file containing
                                parameter placeholders.
            sql             (str or sqlalchemy.sql.selectable.Select statement):
                                Optional. A SQL query ready for execution.
            increment_counter (boolean): Defaults to True. Increments GenericReport.record_count
                                with number of records in returned result set.

        Executes SQL and returns QueryResult object, containing data and metadata.
        """
        q = QueryGenerator(cm=cm, filename=query_file, params=query_params, sql=sql)
        try:
            results = q.execute()
            if increment_counter:
                self.record_count += results.result_count
            return results
        except:
            self.log_error("Unable to execute query.")

    def make_worksheet(self, sheet_name, query_results):
        "Adds worksheet to workbook using provided query results."
        try:
            self.workbook_builder.add_worksheet(sheet_name=sheet_name,
                                                field_names=query_results.field_names,
                                                sheet_data=query_results.result_data
                                            )
        except:
            self.log_error("Unable to add worksheet {}".format(sheet_name))

    def create_worksheet_from_query(self, cm, sheet_name, query_file=None, query_params=None, sql=None):
        """
        Args:
            sheet_name      (str): The name of the worksheet to be created.
            query_file      (str): Optional. Name of file to be read without extension.
            query_params    (dict): Optional. Contains parameter names and values if applicable.
                                Should only be included along with query_file containing
                                parameter placeholders.
            sql             (str or sqlalchemy.sql.selectable.Select statement):
                                Optional. A SQL query ready for execution.
            cm              (ConnectionManager): Object which contains connection to desired database.

        Executes a query and uses results to add worksheet to ReportWriter.workbook_builder.
        """
        results = self.execute_query(cm=cm, query_file=query_file, query_params=query_params, sql=sql)
        self.make_worksheet(sheet_name=sheet_name, query_results=results)


class ReportErrorLogger(object):

    def __init__(self, report_title):
        self.report_title = report_title
        self.notification_recipient = config['Default'].get('notification_recipient')
        self.buffer = []
        self.notified = False

    def log_error(self, msg):
        error_value = sys.exc_info()[1]
        log_record = msg + '; ' + str(error_value) + ': ' + str(error_value.__doc__)
        self.buffer.append(log_record)

    def flush(self):
        if self.should_flush():
            self.send_buffer_by_email()
            self.buffer[:] = []

    def should_flush(self):
        return len(self.buffer) > 0

    def send_buffer_by_email(self):
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
        for i, error in enumerate(self.buffer, 1):
            msg += str(i) + '. ' + error + '\n'
        return msg


class DatabaseLogger(object):
    """
    Don't want to log if report not active,
    or if logging is not enabled.
    """
    def __init__(self):
        pass

    def create_record(self):
        pass

    def finalize_record(self):
        pass

class ReportActiveChecker(object):

    def __init__(self, db, report_name):
        self.db = db
        self.report_name = report_name
        self.active = False
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
            results = self.execute_query(sql=statement, increment_counter=False)
            if results.result_data[0][0] == 1:
                self.active = True
            else:
                self.active = False
        except IndexError:
            self.log_error_detail("Report does not exist.")
            raise Exception("Report does not exist.")