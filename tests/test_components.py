from porthole.report_components import ReportWriter

class TestReportWriter(unittest.TestCase):

    def test_create_workbook(self):
        writer = ReportWriter("Test Report")
        writer.build_file()
        self.assertIsNotNone(writer.workbook_builder)
        self.assertTrue(os.path.isfile(writer.report_file))

    def test_create_worksheet(self):
        report = GenericReport(
                                report_name='test_report_active'
                                , report_title = 'Test Report - Active'
                                )
        report.build_file()
        self.assertEqual(report.record_count, 0)
        report.create_worksheet_from_query(sql=TEST_QUERY,
                                            sheet_name='Sheet1')
        report.close_workbook()
        self.assertTrue(report.record_count > 0)
        self.assertTrue(report.error_detail == [])
        report.finalize_log_record()

    def test_invalid_sheet_name_raises_error(self):
        "Should log an error if attempt to add worksheet with invalid name"
        report = GenericReport(
                                report_name='test_report_active'
                                , report_title = 'Test Report - Active'
                                )
        report.build_file()
        report.create_worksheet_from_query(query_file='test_report_query',
                                            sheet_name='Sheet/1')
        report.close_workbook()
        self.assertFalse(report.error_detail == [])
        report.finalize_log_record()
