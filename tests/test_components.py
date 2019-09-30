import os, unittest
from porthole import ConnectionManager, config, QueryExecutor
from porthole.components import ReportWriter, ReportActiveChecker, RecipientsChecker, DatabaseLogger

TEST_QUERY = "select count(*) from {}.flarp;"
default_db = config['Default'].get('database')


class TestReportWriter(unittest.TestCase):
    def setUp(self):
        self.cm = ConnectionManager(default_db)
        self.cm.connect()

    def tearDown(self):
        self.cm.close()

    def test_create_workbook(self):
        writer = ReportWriter("Test Report")
        writer.build_file()
        writer.close_workbook()
        self.assertIsNotNone(writer.workbook_builder)
        self.assertTrue(os.path.isfile(writer.report_file))
        os.unlink(writer.report_file)

    def test_create_worksheet(self):
        writer = ReportWriter("Test Report 2")
        writer.build_file()
        self.assertEqual(writer.record_count, 0)
        test_query = TEST_QUERY.format(self.cm.schema)
        writer.create_worksheet_from_query(self.cm, "sheet1", sql=test_query)
        writer.close_workbook()
        self.assertTrue(writer.record_count > 0)
        self.assertTrue(writer.logger.error_buffer.empty)

    def test_invalid_sheet_name_raises_error(self):
        """Should log an error if attempt to add worksheet with invalid name"""
        writer = ReportWriter("Test Report 3")
        writer.build_file()
        test_query = TEST_QUERY.format(self.cm.schema)
        writer.create_worksheet_from_query(self.cm, "sheet/1", sql=test_query)
        writer.close_workbook()
        self.assertFalse(writer.logger.error_buffer.empty)


class TestReportActiveChecker(unittest.TestCase):

    def setUp(self):
        self.cm = ConnectionManager(default_db)
        self.cm.connect()

    def tearDown(self):
        self.cm.close()

    def test_active(self):
        active_checker = ReportActiveChecker(self.cm, 'test_report_active')
        inactive_checker = ReportActiveChecker(self.cm, 'test_report_inactive')
        self.assertTrue(active_checker)
        self.assertFalse(inactive_checker)


class TestRecipientsChecker(unittest.TestCase):

    def setUp(self):
        self.cm = ConnectionManager(default_db)
        self.cm.connect()

    def tearDown(self):
        self.cm.close()

    def test_get_recipients(self):
        checker = RecipientsChecker(cm=self.cm, report_name='test_report_active')
        checker.assertFalse(checker.to_recipients)
        checker.assertFalse(checker.cc_recipients)
        checker.get_recipients()
        checker.assertTrue(checker.to_recipients)
        checker.assertTrue(checker.cc_recipients)


class TestDBLogger(unittest.TestCase):

    def setUp(self):
        self.cm = ConnectionManager(default_db)
        self.cm.connect()

    def tearDown(self):
        self.cm.close()

    def test_create_and_finalize(self):
        db_logger = DatabaseLogger(cm=self.cm, report_name="TestDBLogger")
        db_logger.create_record()
        self.assertIsInstance(db_logger.report_log.primary_key, int)
        self.assertTrue(db_logger.report_log.inserted)
        self.assertFalse(db_logger.report_log.updated)
        db_logger.finalize_record()
        self.assertTrue(db_logger.report_log.updated)

    def test_log_recipients(self):
        test_recipients = ["recipient1@example.com", "recipient2@example.com"]
        db_logger = DatabaseLogger(cm=self.cm, report_name="TestDBLogger")
        db_logger.create_record()
        db_logger.finalize_record(test_recipients)
        sql = f"select recipients from {self.cm.schema}.report_logs where id = {db_logger.report_log.primary_key}"
        with QueryExecutor(default_db) as qe:
            result = qe.execute_query(sql=sql)
        self.assertEqual(result.result_data[0]['recipients'], "; ".join(test_recipients))
