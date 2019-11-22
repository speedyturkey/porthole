import unittest
from porthole.app import default_session
from porthole.models import AutomatedReport, AutomatedReportContact, AutomatedReportRecipient
from porthole.models import ReportLog, ReportLogDetail


class TestReportModels(unittest.TestCase):
    def test_create_report_and_recipients(self):
        report = AutomatedReport(report_name="this_is_a_test", active=1)
        contact_1 = AutomatedReportContact(last_name="LLL", first_name="FFF", email_address="fff.lll@example.com")
        contact_2 = AutomatedReportContact(last_name="LLL2", first_name="FFF2", email_address="fff.lll.2@example.com")
        default_session.add(report)
        default_session.add(contact_1)
        default_session.add(contact_2)
        to_recipient = AutomatedReportRecipient(report=report, contact=contact_1, recipient_type="to")
        cc_recipient = AutomatedReportRecipient(report=report, contact=contact_2, recipient_type="cc")
        default_session.add(to_recipient)
        default_session.add(cc_recipient)
        default_session.commit()
        self.assertEqual(report.to_recipients, ["fff.lll@example.com"])
        self.assertEqual(report.cc_recipients, ["fff.lll.2@example.com"])
        self.assertEqual(contact_1.reports, [report])
        self.assertEqual(contact_2.reports, [report])

    def test_report_log_no_recipients_no_errors(self):
        report_log = ReportLog(report_name="this_is_a_test")
        default_session.add(report_log)
        self.assertIsNotNone(report_log.started_at)
        report_log.finalize()
        self.assertEqual(report_log.success, 1)
        self.assertIsNone(report_log.recipients)
        self.assertIsNone(report_log.error_detail)

    def test_report_log_with_recipients_no_errors(self):
        report_log = ReportLog(report_name="this_is_a_test")
        default_session.add(report_log)
        self.assertIsNotNone(report_log.started_at)
        recipients = ["fff.lll@example.com", "fff.lll.2@example.com"]
        report_log.finalize(recipients=recipients)
        default_session.commit()
        self.assertEqual(report_log.success, 1)
        self.assertEqual(report_log.recipients, "; ".join(recipients))
        self.assertIsNone(report_log.error_detail)

    def test_report_log_with_errors_no_recipients(self):
        report_log = ReportLog(report_name="this_is_a_test")
        default_session.add(report_log)
        self.assertIsNotNone(report_log.started_at)
        report_log.finalize(errors=["Uh oh!"])
        default_session.commit()
        self.assertEqual(report_log.success, 0)
        self.assertIsNone(report_log.recipients)
        self.assertIsNotNone(report_log.error_detail)
