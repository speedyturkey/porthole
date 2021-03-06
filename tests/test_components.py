import os, unittest
from porthole import ConnectionManager, config
from porthole.components import ReportWriter

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
