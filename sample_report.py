from porthole import config, BasicReport, GenericReport

def basic_report():
    report = BasicReport(report_title='Basic Report Sample')
    report.build_file()
    report.create_worksheet_from_query( sheet_name='Sheet1',
                                        query={'filename': 'sample_query'}
                                    )
    report.to_recipients.append(config['Default']['notification_recipient'])
    report.subject = 'Sample Report - Basic'
    report.message = 'Please see attached for the Basic Sample Report.'
    report.execute()


def generic_report():
    report = GenericReport(report_name='sample_report', report_title='Generic Sample Report')
    report.build_file()
    report.create_worksheet_from_query( sheet_name='Sheet1',
                                        query={'filename': 'sample_query'}
                                    )
    report.subject = 'Sample Report - Generic'
    report.message = 'Please see attached for the Generic Sample Report.'
    report.execute()

if __name__ == '__main__':
    basic_report()
    generic_report()
