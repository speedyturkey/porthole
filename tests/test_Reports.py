"""
Need to try forcing different kinds of errors,
and checking error_detail.
Test failure notification is sent on failure.
Test email is not sent on failure.
"""

import os
import sys
import unittest
from porthole import config, BasicReport, GenericReport

class TestBasicReport(unittest.TestCase):
    def test_basic_functionality(self):
        report = BasicReport(report_title = 'Basic Report - Test')
        report.build_file()
        report.create_worksheet_from_query(sheet_name='Sheet1',
                                            sql=TEST_QUERY)
        report.to_recipients.append(config['Default']['notification_recipient'])
        report.subject = 'Basic Report - Test'
        report.message = 'Basic Report Test'
        report.execute()

class TestGenericReport(unittest.TestCase):

    def test_logging(self):
        report = GenericReport(
                                report_name='test_report_active'
                                , report_title = 'Test Report - Active'
                                )
        self.assertFalse(report.email_sent)

    def test_disable_logging(self):
        report = GenericReport(
                                report_name='test_report_active'
                                , report_title = 'Test Report - Active'
                                , logging_enabled=False
                                )
        self.assertFalse(hasattr(report, 'report_log'))

    def test_send_email(self):
        report = GenericReport(
                                report_name='test_report_active'
                                , report_title = 'Test Report - Active'
                                )
        report.get_recipients()
        report.subject = "test_send_email"
        report.message = "test_send_email"
        report.build_and_send_email()
        self.assertTrue(report.email_sent)
        report.db_logger.finalize_record()

    def test_send_if_blank(self):
        report = GenericReport(
                                report_name='test_report_active'
                                , report_title = 'Test Report - Active'
                                )
        report.send_if_blank = False
        report.get_recipients()
        report.subject = "test_send_if_blank"
        report.message = "test_send_if_blank"
        report.build_and_send_email()
        self.assertEqual(report.record_count, 0)
        self.assertFalse(report.email_sent)
        report.record_count = 1
        report.build_and_send_email()
        self.assertTrue(report.email_sent)
        report.db_logger.finalize_record()

    def test_non_existent_report_raises_error(self):
        "Should log an error if attempt to instantiate report that doesn't exist"
        with self.assertRaises(Exception) as context:
            report = GenericReport(
                                    report_name='does_not_exist'
                                    , report_title = 'Does Not Exist'
                                    )
        self.assertTrue('Report does not exist' in str(context.exception))

    def test_non_existent_query_raises_error(self):
        "Should raise an error if attempt to run query that doesn't exist"
        report = GenericReport(
                                report_name='test_report_active'
                                , report_title = 'Test Report - Active'
                                )
        report.build_file()
        report.create_worksheet_from_query(query={'filename': 'does_not_exist'},
                                            sheet_name='Sheet1')
        self.assertFalse(report.error_log == [])
        report.db_logger.finalize_record()

    def test_send_failure_notification_on_error(self):
        "On error, should send failure notification and should not send report."
        report = GenericReport(
                                report_name='test_report_active'
                                , report_title = 'Test Report - Active'
                                )
        report.build_file()
        report.create_worksheet_from_query(sheet_name='Sheet1',
                                            sql=TEST_QUERY)
        report.error_log.append("Forced error")
        report.subject = "test_send_failure_notification_on_error"
        report.message = "test_send_failure_notification_on_error"
        report.execute()
        self.assertFalse(report.email_sent)
        self.assertTrue(report.failure_notification_sent)

TEST_QUERY = "select count(*) from flarp;"

def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGenericReport)
    unittest.TextTestRunner(verbosity=3).run(suite)

if __name__ == '__main__':
    unittest.main()
