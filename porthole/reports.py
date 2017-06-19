#!/usr/bin/env python
# encoding: utf-8
"""
GenericReport.py
Created on 01/26/17.
This module contains functionality to simplify the creation of new automated reports.
Features include creation of Excel worksheets from query results, emailing of results,
and database logging.
"""

import sys
import os.path
from sqlalchemy import select
from .app import config
from .models import (metadata,
                    automated_reports,
                    automated_report_contacts,
                    automated_report_recipients,
                    report_logs)
from .connection_manager import ConnectionManager
from .related_record import RelatedRecord
from .mailer import Mailer
from .queries import QueryGenerator, QueryReader
from .xlsx import WorkbookBuilder
from . import TimeHelper


class GenericReport():
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
                                        query={'name': 'test_query'},
                                        sheet_name='Sheet1'
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
    def __init__(self, report_title, report_name, logging_enabled=True):
        # -----------------------------------------
        # Assign arguments to instance attributes.
        # -----------------------------------------
        self.report_title = report_title
        self.report_name = report_name
        self.logging_enabled = logging_enabled
        # -----------------------------------------
        # Setup configuration variables and defaults.
        # By default, reports will be sent even if there are no results.
        # This behavior can be overridden for individual reports. Record count
        # initialized at 0, but incremented by execute_query.
        # -----------------------------------------
        self.send_if_blank = True
        self.record_count = 0
        self.workbook = None
        self.attachments = []
        self.error_detail = []
        self.to_recipients = []
        self.cc_recipients = []
        self.email_sent = False
        self.file_path = config['Default'].get('base_file_path')
        self.default_db = config['Default'].get('database')
        self.notification_recipient = config['Default'].get('notification_recipient')
        self.default_cm = ConnectionManager(self.default_db)
        self.default_cm.connect()
        self.active = self.check_if_active()
        self.create_log_record()

    def __del__(self):
        try:
            self.default_cm.close()
        except:
            pass

    def log_error_detail(self, error_context):
        """Provided a description of when error was raised, assembles error message for log
        and appends the message."""
        error_value = sys.exc_info()[1]
        error_message = error_context + '; ' + str(error_value) + ': ' + str(error_value.__doc__)
        self.error_detail.append(error_message)

    def check_if_active(self):
        """Queries database to determine if the 'active' attribute for this report
        is set to 1 (active) or 0 (inactive).
        """
        statement = select([automated_reports.c.active])\
                        .where(automated_reports.c.report_name==self.report_name)
        q = QueryGenerator(cm=self.default_cm, sql=statement)
        try:
            results = q.execute()
            if results.result_data[0][0] == 1:
                return True
            else:
                return False
        except IndexError:
            self.log_error_detail("Report does not exist.")
            raise Exception("Report does not exist.")

    def create_log_record(self):
        """Inserts new log record into default report logging table
        using RelatedRecord and saves instance of RelatedRecord for updating
        later on with results of report execution.
        """
        if self.active and self.logging_enabled:
            report_log = RelatedRecord(self.default_cm, 'report_logs')
            report_log.insert({'report_name': self.report_name,
                                'started_at': TimeHelper.now(string=False)})
            self.report_log = report_log

    def finalize_log_record(self):
        "Update log at conclusion of report execution to indicate success/failure."
        if self.logging_enabled:
            if self.error_detail:
                errors = "; ".join(self.error_detail).replace("'", "")
                data_to_update = {'completed_at': TimeHelper.now(string=False),
                                    'success': 0,
                                    'error_detail': errors}
            else:
                data_to_update = {'completed_at': TimeHelper.now(string=False),
                                    'success': 1}
        self.report_log.update(data_to_update)

    def build_file(self):
        """Loads file and path information and creates XLSX Writer Workbook object.
        Default file is named with convention yyyy-mm-dd - Report Name.xlsx
        """
        # Construct the file path.
        try:
            report_file_name = "{} - {}.xlsx".format(TimeHelper.today(), self.report_title)
            self.report_file = os.path.join(self.file_path, report_file_name)
            # Create the workbook.
            self.workbook_builder = WorkbookBuilder(filename=self.report_file)
        except:
            self.log_error_detail("Unable to build file")

    def close_workbook(self):
        """Closes workbook object after creation is complete.
        Should always be executed before sending file."""
        if self.workbook_builder:
            self.workbook_builder.workbook.close()
        if self.report_file:
            self.attachments.append(self.report_file)

    def execute_query(self, sql, cm=None, increment_counter=True):
        """
        Executes SQL and returns QueryResult object,
        containing data and metadata.
        """
        if cm is None:
            cm = self.default_cm
        q = QueryGenerator(cm=cm, sql=sql)
        try:
            results = q.execute()
            if increment_counter:
                self.record_count += results.result_count
            return results
        except:
            self.log_error_detail("Unable to execute query.")

    def make_worksheet(self, sheet_name, query_results):
        "Adds worksheet to workbook using provided query results."
        try:
            self.workbook_builder.add_worksheet(sheet_name=sheet_name,
                                                field_names=query_results.field_names,
                                                sheet_data=query_results.result_data
                                            )
        except:
            self.log_error_detail("Unable to add worksheet {}".format(sheet_name))

    def read_query(self, query):
        """
        Uses QueryReader to read .sql file and parameterize query as necessary.

        Args:
            query (dict):   Should contain filename (str) and params (dict, optional).
        """
        filename = query.get('filename')
        params = query.get('params')
        reader = QueryReader(filename=filename, params=params)
        return reader

    def create_worksheet_from_query(self, query, sheet_name, read_required=False, cm=None):
        """
        Args:
            query           (str,
                            dict, or
                            sqlalchemy.sql.selectable.Select): A SQL query ready
                                for execution, or a dict containing information
                                necessary to read and/or parameterize a query.
            sheet_name      (str): The name of the resulting worksheet.
            read_required   (bool): Defaults to False. Set to true if passing a
                                query which must be read and/or parameterized
                                from file. If true, query parameter should be
                                a dict.
            cm              (ConnectionManager): Defaults to None, in which case
                                default ConnectionManager is used.

        """
        if cm is None:
            cm = self.default_cm
        if read_required:
            reader = self.read_query(query)
            sql = reader.sql
        else:
            sql = query
        results = self.execute_query(cm=cm, sql=sql)
        self.make_worksheet(sheet_name=sheet_name, query_results=results)

    def get_recipients(self):
        "Performs lookup in database for report recipients based on report name."
        statement = select([automated_report_contacts.c.email_address,
                            automated_report_recipients.c.recipient_type])\
                        .select_from(automated_reports\
                        .join(automated_report_recipients)\
                        .join(automated_report_contacts))\
                        .where(automated_reports.c.report_name==self.report_name)
        results = self.execute_query(statement, increment_counter=False)

        for recipient in results.result_data:
            if recipient.recipient_type == 'to':
                self.to_recipients.append(recipient.email_address)
            else:
                self.cc_recipients.append(recipient.email_address)

        if not self.to_recipients:
            raise KeyError("No primary recipient found for the provided report.")

    def build_email(self):
        "Instantiates Mailer object using provided parameters."
        if not self.to_recipients:
            self.get_recipients()
        email = Mailer()
        email.recipients = self.to_recipients
        email.cc_recipients = self.cc_recipients
        email.subject = self.subject
        email.message = self.message
        email.attachments = self.attachments
        self.email = email

    def check_whether_to_send_email(self):
        "Determines whether email should be sent based given errors, settings, and result count."
        if self.error_detail:
            return False
        elif not self.send_if_blank and self.record_count == 0:
            return False
        else:
            return True

    def send_email(self):
        "Executes the send_email method of the Mailer."
        try:
            self.email.send_email()
            self.email_sent = True
        except:
            self.log_error_detail("Unable to send email")

    def build_and_send_email(self):
        """If email should be sent, builds email object and sends email."""
        if self.check_whether_to_send_email():
            self.build_email()
            self.send_email()

    def send_failure_notification(self):
        "Sends failure notification to identified recipients, including logged errors."

        message = """Execution of the following report failed: {}

The following errors were logged:
""".format(self.report_title)

        for i, error in enumerate(self.error_detail, 1):
            message += str(i) + '. ' + error + '\n'

        email = Mailer()
        email.recipients = [self.notification_recipient]
        email.cc_recipients = ['']
        email.subject = "Report Failure: {}".format(self.report_title)
        email.message = message
        email.attachments = []
        email.send_email()
        self.failure_notification_sent = True

    def execute(self):
        """
        After instantiation and setup, and after
        any query results have been added to the workbook,
        this method executes and finalizes the report,
        ensures errors are handled, and performs cleanup.
        """
        self.close_workbook()
        if self.active:
            self.build_and_send_email()
            self.finalize_log_record()
        self.default_cm.close()
        if self.error_detail:
            self.send_failure_notification()

if __name__ == '__main__':
    pass
