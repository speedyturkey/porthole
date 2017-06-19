import xlsxwriter

class WorkbookBuilder(object):
    """
    Allows for creation of Excel workbooks containing arbitrary worksheets
    using the xlsxwriter library.
    """
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

    def add_worksheet(self, sheet_name, field_names, sheet_data, row_start=0, col_start=0):
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
            for x in range(0, len(row)):
                worksheet.write(e_row, e_col + x, row[x])
            e_row += 1
