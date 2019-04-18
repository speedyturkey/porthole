import datetime
import xlsxwriter


class WorkbookBuilder(object):
    """
    Allows for creation of Excel workbooks containing arbitrary worksheets
    using the xlsxwriter library.
    """

    DEFAULT_COL_WIDTH = 10
    MAX_COLUMN_WIDTH = 50
    DEFAULT_HEADER_PARAMS = {'bold': True}

    def __init__(self, filename=None):
        self.filename = filename
        self.default_header_format = None
        self.formats = {}
        self.workbook_options = {
            'constant_memory': True,
            'default_date_format': 'mm/dd/yy'}
        self.workbook = None
        if filename:
            self.create_workbook()

    def create_workbook(self):
        """Given filename, workbook options, and head format, create workbook."""
        workbook = xlsxwriter.Workbook(self.filename, self.workbook_options)
        self.default_header_format = workbook.add_format(WorkbookBuilder.DEFAULT_HEADER_PARAMS)
        self.workbook = workbook

    def close_workbook(self):
        """An exception may be raised if workbook is not closed explicitly."""
        self.workbook.close()

    def add_format(self, format_name, format_params):
        """Creates new format object and adds it to this workbook's available formats."""
        if format_name in self.formats:
            raise IndexError(f"Workbook already contains format object < {format_name} >")
        self.formats[format_name] = self.workbook.add_format(format_params)

    def add_worksheet(
            self, sheet_name, field_names, sheet_data,
            format_axis=None, format_rules=None, row_start=0, col_start=0,
            autofit_columns=True, column_width=None, freeze_first_row=False,
            header_format=None, show_autofilter=False
    ):
        """
        :param sheet_name: Worksheet name as string.
        :param field_names: List of column names to be written as headers.
        :param sheet_data: List of lists containing data to write to the worksheet.
        :param format_axis: Optional, default None. Allowed values include `0` or `'row'`, or `1` or `column`.
        :param format_rules: Optional, default None. Dictionary of parameters for format rules to be applied.
        :param row_start: Optional, default value of 0 (first row). Set the row to start writing from.
        :param col_start: Optional, default value of 0 (first column). Set the column to start writing from.
        :param autofit_columns: Optional, default value of False. Select whether columns should be "auto-fitted".
        :param column_width: Optional, default of None. Specify a uniform column width.
        :param freeze_first_row: Optional, default False. Freezes first row when scrolling.
        :param header_format: Optional, default None. Apply specified format name to header row.
        :param show_autofilter: Optional, default False. Show autofilter on first row.

        Add worksheet to the workbook. This method assumes that each inner list (row) has the same number of elements.
        """
        if autofit_columns and column_width:
            raise ValueError("Cannot both auto-fit columns and set a uniform column width.")
        worksheet = self.workbook.add_worksheet(sheet_name)
        cell_formats = create_cell_formats(sheet_data, format_axis, format_rules)

        e_row = row_start
        e_col = col_start

        # Write field names in first row.
        for i, field_name in enumerate(field_names):
            worksheet.write(
                e_row,
                e_col + i,
                field_name,
                self.formats.get(header_format, self.default_header_format)
            )

        # Increment row counter for incoming data.
        e_row += 1

        # Write the data.
        for value_row, format_row in zip(sheet_data, cell_formats):
            for x, (val, fmt) in enumerate(zip(value_row, format_row)):
                worksheet.write(e_row, e_col + x, val, self.formats.get(fmt))
            e_row += 1

        col_widths = self.calculate_column_widths(field_names, sheet_data, autofit_columns, column_width)
        for i, width in enumerate(col_widths):
            worksheet.set_column(i, i, width)
        if freeze_first_row:
            worksheet.freeze_panes(1, 0)
        if show_autofilter:
            worksheet.autofilter(0, 0, 0, len(field_names) - 1)

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


def apply_column_rule(row, rule):
    """
    Given a cell value and a rule, return a format name. See `create_cell_formats` for more detail.
    """
    rule_type = rule['type']
    if rule_type == 'all':
        return rule['format']
    if rule_type == 'boolean':
        if rule['function'](row):
            return rule['format']
        else:
            return None
    if rule_type == 'conditional':
        return rule['function'](row)
    raise ValueError(f"Column rule type <{rule['type']}> not supported")


def create_column_formats(data, format_rules):
    """
    Iterate through provided data and apply format rules, returning format names corresponding to each data element.
    """
    result = []
    for row in data:
        row_formats = [
            apply_column_rule(row, format_rules[col_name]) if col_name in format_rules else None
            for col_name in row.keys()
        ]
        result.append(row_formats)
    return result


def create_row_formats(data, format_rules):
    raise NotImplementedError("Formatting rows has not yet been implemented, but will be included in a future release.")


def create_cell_formats(data, format_axis=None, format_rules=None):
    """
    Apply format rules (if provided) to data and return format names corresponding to each data element. Format rules
    should contain the names of a specific format object, not the format object itself or paramteters to construct one.
    All format names referenced should be added separately using the `WorkbookBuilder.add_format` method.

    :param data: The results of a query, or other data structure, to be written to a new worksheet.
    :type data: List of RowDict objects, e.g. `QueryResult.result_data`
    :param format_axis: The axis along which to apply the provided format rules - formats can be applied to rows,
        or to columns, but not both.
    :type format_axis: Integer, string, or None.
    :param format_rules: The rule(s) to apply to the data. Available format and options are as follows:

    Columns - Keys are field names as strings. Values are dictionaries representing the rule to apply for that specific
        column. These dictionaries must contain `type`, and may contain `format` and/or `function`.

    Possible values for `type` include:
        all: format the entire column using the provided format name.
        boolean: format any values with the provided format name, which test as True using a provided `function`,
            The functions should accept a RowDict and return True or False.
        conditional: format any values with one or more provided format names. The provided `function` should accept
            cell values and return the format name (or None).

    Sample usage:

    format_rules = {
        'salary': {'type': 'all', 'format': 'money'},
        'age': {'type': 'boolean', 'format': 'bold_red', 'function': lambda row: row['field'] % 2 == 0},
    }

    :type format_rules: Dictionary, with keys representing column names (if applying column rules).
    :return: List of lists of strings, where each is the name of the format object to be applied to that data
        element, or None if no format is to be applied.
    """
    if format_axis not in (None, 0, 1, 'row', 'column'):
        raise ValueError("Must provide valid format axis: 0 or 'row', 1 or 'column'.")
    if format_axis in (1, 'column'):
        return create_column_formats(data, format_rules)
    if format_axis in (0, 'row'):
        return create_row_formats(data, format_rules)
    return [[None] * len(row) for row in data]
