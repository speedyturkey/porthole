from porthole import GenericReport

report = GenericReport(report_name='sample_report', report_title='Sample Report')
report.build_file()
report.create_worksheet_from_query( sheet_name='Sheet1',
                                    query={'filename': 'sample_query'}
                                )
report.subject = 'Sample Report'
report.message = 'Please see attached for the Sample Report.'
report.execute()
