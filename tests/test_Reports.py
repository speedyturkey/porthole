"""
Need to try forcing different kinds of errors,
and checking error_detail.
Test failure notification is sent on failure.
Test email is not sent on failure.
"""

from types import MethodType
import unittest
from porthole import config, BasicReport, GenericReport, ReportRunner


def mocked_send_email(self):
    print("(Mock) email sent.")
    self.email_sent = True


def mocked_send_failure_notification(self):
    print("(Mock) failure notification sent.")
    self.failure_notification_sent = True


class TestBasicReport(unittest.TestCase):
    def test_basic_functionality(self):
        report = BasicReport(report_title='Basic Report - Test')
        report.send_email = MethodType(mocked_send_email, report)
        report.build_file()
        report.create_worksheet_from_query(sheet_name='Sheet1',
                                            sql=TEST_QUERY)
        report.to_recipients.append(config['Default']['notification_recipient'])
        report.subject = 'Basic Report - Test'
        report.message = 'Basic Report Test'
        report.execute()

    def test_debug_mode_integration(self):
        config.set('Debug', 'debug_mode', 'False')
        report = BasicReport(report_title='Basic Report - Test', debug_mode=True)
        report.send_email = MethodType(mocked_send_email, report)
        report.build_file()
        report.create_worksheet_from_query(
            sheet_name='Sheet1',
            sql=TEST_QUERY
        )
        report.to_recipients.append(config['Default']['notification_recipient'])
        report.subject = 'Basic Report - Test'
        report.message = 'Basic Report Test'
        report.execute()
        self.assertTrue(report.debug_mode)
        self.assertTrue(report.email.debug_mode)
        config.set('Debug', 'debug_mode', 'True')


class TestGenericReport(unittest.TestCase):

    def test_logging(self):
        report = GenericReport(
            report_name='test_report_active',
            report_title='Test Report - Active'
        )
        self.assertFalse(report.email_sent)
        self.assertIsNotNone(report.db_logger)

    def test_disable_logging(self):
        report = GenericReport(
            report_name='test_report_active',
            report_title='Test Report - Active',
            logging_enabled=False
        )
        self.assertFalse(hasattr(report, 'report_log'))
        self.assertIsNone(report.db_logger)

    def test_send_email(self):
        report = GenericReport(
            report_name='test_report_active',
            report_title='Test Report - Active'
        )
        report.send_email = MethodType(mocked_send_email, report)
        report.get_recipients()
        report.subject = "test_send_email"
        report.message = "test_send_email"
        report.build_and_send_email()
        self.assertTrue(report.email_sent)
        report.db_logger.finalize_record()
        report.conns.close_all()

    def test_send_if_blank(self):
        report = GenericReport(
            report_name='test_report_active',
            report_title='Test Report - Active'
        )
        report.send_if_blank = False
        report.build_file()
        report.send_email = MethodType(mocked_send_email, report)
        report.get_recipients()
        report.subject = "test_send_if_blank"
        report.message = "test_send_if_blank"
        report.build_and_send_email()
        self.assertEqual(report.record_count, 0)
        self.assertEqual(report.report_writer.record_count, 0)
        self.assertFalse(report.email_sent)
        report.report_writer.record_count += 1
        report.build_and_send_email()
        self.assertTrue(report.email_sent)
        report.db_logger.finalize_record()
        report.conns.close_all()

    def test_non_existent_report_raises_error(self):
        """Should log an error if attempt to instantiate report that doesn't exist"""
        with self.assertRaises(Exception) as context:
            report = GenericReport(
                report_name='does_not_exist',
                report_title='Does Not Exist'
            )
        self.assertTrue("Report <does_not_exist> was not found" in str(context.exception))

    def test_non_existent_query_raises_error(self):
        """Should raise an error if attempt to run query that doesn't exist"""
        report = GenericReport(
            report_name='test_report_active',
            report_title='Test Report - Active',
            logger_name="test_non_existent_query_raises_error"
        )
        report.build_file()
        report.create_worksheet_from_query(
            query={'filename': 'does_not_exist'},
            sheet_name='Sheet1'
        )

        self.assertFalse(report.logger.error_buffer.empty)
        report.db_logger.finalize_record()

    def test_send_failure_notification_on_error(self):
        """On error, should send failure notification and should not send report."""
        report = GenericReport(
            report_name='test_report_active',
            report_title='Test Report - Active',
            logger_name="test_send_failure_notification_on_error"
        )
        report.send_failure_notification = MethodType(mocked_send_failure_notification, report)
        report.build_file()
        report.create_worksheet_from_query(
            sheet_name='Sheet1',
            sql=TEST_QUERY
        )
        report.logger.error("Forced error")
        report.subject = "test_send_failure_notification_on_error"
        report.message = "test_send_failure_notification_on_error"
        report.execute()
        self.assertFalse(report.email_sent)
        self.assertTrue(report.failure_notification_sent)

    def test_report_recipients(self):
        report = GenericReport(
            report_name='test_report_active',
            report_title='Test Report - Active'
        )
        report.get_recipients()
        self.assertTrue(report.to_recipients[0] == 'speedyturkey@gmail.com')
        self.assertTrue(report.cc_recipients[0] == 'DaStump@example.com')
        self.assertTrue(len(report.all_recipients) == 2)


class TestReportRunner(unittest.TestCase):
    def test_list_arg(self):
        parsed = ReportRunner().parse_args()
        self.assertFalse(parsed.list)
        parsed = ReportRunner().parse_args(['-l'])
        self.assertTrue(parsed.list)
        parsed = ReportRunner().parse_args(['--list'])
        self.assertTrue(parsed.list)

    def test_report_arg(self):
        report = 'test_report'
        parsed = ReportRunner().parse_args()
        self.assertIsNone(parsed.report)
        parsed = ReportRunner().parse_args(['-r', report])
        self.assertEqual(report, parsed.report)
        parsed = ReportRunner().parse_args(['--report', report])
        self.assertEqual(report, parsed.report)

    def test_debug_mode_arg(self):
        parsed = ReportRunner().parse_args()
        self.assertFalse(parsed.debug_mode)
        parsed = ReportRunner().parse_args(['-d'])
        self.assertTrue(parsed.debug_mode)
        parsed = ReportRunner().parse_args(['--debug'])
        self.assertTrue(parsed.debug_mode)


TEST_QUERY = "select count(*) from sys.flarp;"


def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGenericReport)
    unittest.TextTestRunner(verbosity=3).run(suite)


if __name__ == '__main__':
    unittest.main()
