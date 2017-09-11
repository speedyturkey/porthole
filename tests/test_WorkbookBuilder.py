import os
import datetime
import unittest
from porthole import config
from porthole import WorkbookBuilder

class TestWorkbookBuilder(unittest.TestCase):
    """
    report.workbook.worksheets()[0].name
    sheetname_count - count of sheets
    sheetnames - dictionary where keys are sheetnames
    fileclosed - 1 if closed, 0 otherwise
    """

    def setUp(self):
        self.test_builder = WorkbookBuilder(filename="test_builder")
        self.test_builder.create_workbook()

    def tearDown(self):
        os.remove(self.test_builder.filename)

    def test_add_worksheet(self):
        field_names = ['Field1', 'Field2']
        data = ['Foo', 'Bar']
        self.test_builder.add_worksheet("TestSheet", field_names, data)
        self.assertIn("TestSheet", self.test_builder.workbook.sheetnames)

    def test_close_workbook(self):
        self.assertFalse(self.test_builder.workbook.fileclosed)
        self.test_builder.close_workbook()
        self.assertTrue(self.test_builder.workbook.fileclosed)

    def test_autofit_columns(self):
        field_names = ['Field1', 'Field2', 'Field3']
        data = [['Foo', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', datetime.datetime.today()]]
        self.test_builder.add_worksheet("TestSheet", field_names, data)
        widths = self.test_builder.calculate_column_widths(field_names, data, autofit_columns=True)
        date_format_length = len(str(self.test_builder.workbook.default_date_format.num_format))
        self.assertEqual(widths[0], WorkbookBuilder.DEFAULT_COL_WIDTH)
        self.assertEqual(widths[1], 26 * 1.15)
        self.assertEqual(widths[2], max(date_format_length, WorkbookBuilder.DEFAULT_COL_WIDTH))
        WorkbookBuilder.DEFAULT_COL_WIDTH = 0
        widths = self.test_builder.calculate_column_widths(field_names, data, autofit_columns=True)
        self.assertEqual(widths[2], date_format_length)

