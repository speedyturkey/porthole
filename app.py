from porthole.Config import config
from porthole.ConnectionManager import ConnectionManager
from porthole.ExcelGenerator import WorkbookGenerator, WorksheetGenerator

cm = ConnectionManager(db='Test')
cm.connect()
# cm.cursor.execute('select * from flarp')
# print(cm.cursor.fetchall())
# cm.commit()
# cm.close()

workbook = WorkbookGenerator('/Users/williammcmonagle/VW/test.xlsx')
wb = workbook.create_workbook()
field_names = ['Field1', 'Field2']
data = [['Foo1', 'Bar1'], ['Foo2', 'Bar2']]
ws = WorksheetGenerator(sheet_name='Sheet99', field_names = field_names, sheet_data = data)
ws.header_format = wb.add_format({'bold': True})
ws.add_worksheet_to_workbook(wb)
wb.close()
