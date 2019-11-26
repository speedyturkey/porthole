from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy import insert
from porthole import config
from porthole.models import AutomatedReport, AutomatedReportContact, AutomatedReportRecipient


schema = config[config['Default']['database']]['schema']
test_metadata = MetaData(schema=schema)

flarp = Table(
    'flarp',
    test_metadata,
    Column('flarp_id', Integer, primary_key=True),
    Column('foo', String(255)),
    Column('bar', Integer),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, onupdate=func.now()),
)

flarp_data = [
    {'foo': 'Some text', 'bar': 17},
    {'foo': 'More text', 'bar': 94},
    {'foo': 'Bees?', 'bar': 3},
    {'foo': 'This is a record.', 'bar': 52},
]

florp = Table(
    'florp',
    test_metadata,
    Column('id', Integer, primary_key=True),
    Column('baz', String(255)),
    Column('flarp_id', Integer, ForeignKey(flarp.c.flarp_id), nullable=False),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, onupdate=func.now()),
)

automated_reports_data = [
        {'report_name': 'test_report_active', 'active': 1},
        {'report_name': 'test_report_inactive', 'active': 0},
]

contact_data = [
        {'last_name': 'LAST', 'first_name': 'FIRST', 'email_address': 'speedyturkey@gmail.com'},
        {'last_name': 'Stumpleberry', 'first_name': 'Bargosh', 'email_address': 'DaStump@example.com'}
]

recipient_data = [
        {'contact_id': 1, 'report_id': 1, 'recipient_type': 'to'},
        {'contact_id': 2, 'report_id': 1, 'recipient_type': 'cc'}
]


def create_fixtures(cm):
    cm.conn.execute(flarp.insert(), flarp_data)
    cm.conn.execute(insert(AutomatedReport), automated_reports_data)
    cm.conn.execute(insert(AutomatedReportContact), contact_data)
    cm.conn.execute(insert(AutomatedReportRecipient), recipient_data)
