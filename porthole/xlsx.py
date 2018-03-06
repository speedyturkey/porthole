import datetime
import xlsxwriter

class WorkbookBuilder(object):
    """
    Allows for creation of Excel workbooks containing arbitrary worksheets
    using the xlsxwriter library.
    """

    DEFAULT_COL_WIDTH = 10
    MAX_COLUMN_WIDTH = 50

    def __init__(self, filename=None):
        self.filename = filename
        self.header_params = {'bold': True}
        self.workbook_options = {'constant_memory': True,
                                'default_date_format': 'mm/dd/yy'}
        if filename:
            self.create_workbook()

    def create_workbook(self):
        "Given filename, workbook options, and head format, create workbook."
        workbook = xlsxwriter.Workbook(self.filename, self.workbook_options)
        self.header_format = workbook.add_format(self.header_params)
        self.workbook = workbook


    def close_workbook(self):
        "An exception may be raised if workbook is not closed explicitly."
        self.workbook.close()

    def add_worksheet(self, sheet_name, field_names, sheet_data, row_start=0, col_start=0, autofit_columns=False,
                      column_width=None):
        """
        :param sheet_name: Worksheet name as string.
        :param field_names: List of column names to be written as headers.
        :param sheet_data: List of lists containing data to write to the worksheet.
        :param row_start: Optional, default value of 0 (first row). Set the row to start writing from.
        :param col_start: Optional, default value of 0 (first column). Set the column to start writing from.
        :param autofit_columns: Optional, default value of False. Select whether columns should be "auto-fitted".
        :param column_width: Optional, default of None. Specify a uniform column width.

        Add worksheet to the workbook. This method assumes that each inner list (row) has the same number of elements.
        """
        if autofit_columns and column_width:
            raise ValueError("Cannot both auto-fit columns and set a uniform column width.")
        worksheet = self.workbook.add_worksheet(sheet_name)

        e_row = row_start
        e_col = col_start

        # Write field names in first row.
        for i, field_name in enumerate(field_names):
            worksheet.write(e_row,
                            e_col + i,
                            field_name,
                            self.header_format)

        # Increment row counter for incoming data.
        e_row += 1

        # Write the data.
        for row in sheet_data:
            for x, value in enumerate(row):
                worksheet.write(e_row, e_col + x, value)
            e_row += 1

        col_widths = self.calculate_column_widths(field_names, sheet_data, autofit_columns, column_width)
        for i, width in enumerate(col_widths):
            worksheet.set_column(i, i, width)

    def calculate_column_widths(self, field_names, sheet_data, autofit_columns=False, column_width=None):
        """
        :param field_names:
        :param sheet_data:
        :param autofit_columns: Optional, default value of False. Select whether columns should be "autofitted".
        :param column_width: Optional, default of None. Specify a uniform column width.
        :return: List of column widths as integers
        """
        column_width = column_width or WorkbookBuilder.DEFAULT_COL_WIDTH
        col_widths = [column_width] * len(field_names)

        if autofit_columns is True:
            # We want the longest value in a given column, including the field name.
            headers_and_data = [field_names] + sheet_data
            for row in headers_and_data:
                for idx, value in enumerate(row):
                    if isinstance(value, datetime.datetime):
                        # datetime string representation is usually much longer (26 chars)
                        # than default date format (8 chars)
                        formatted_length = len(str(self.workbook.default_date_format.num_format))
                        compare_value = max(formatted_length, WorkbookBuilder.DEFAULT_COL_WIDTH)
                    else:
                        compare_value = len(str(value))
                    if compare_value > col_widths[idx]:
                        col_widths[idx] = compare_value * 1.15

        for i, width in enumerate(col_widths):
            if width > WorkbookBuilder.MAX_COLUMN_WIDTH:
                col_widths[i] = WorkbookBuilder.MAX_COLUMN_WIDTH

        return col_widths
