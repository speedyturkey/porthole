from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Boolean, ForeignKey, func
from porthole import config
from porthole.models import automated_reports, automated_report_contacts, automated_report_recipients


schema = config[config['Default']['database']]['schema']
test_metadata = MetaData(schema=schema)

flarp = Table('flarp', test_metadata,
                Column('flarp_id', Integer, primary_key=True),
                Column('foo', String(255)),
                Column('bar', Integer),
                Column('created_at', DateTime, server_default=func.now()),
                Column('updated_at', DateTime, onupdate=func.now()),
            )

flarp_data = [
        {'foo': 'Some text', 'bar' : 17},
        {'foo': 'More text', 'bar' : 94},
        {'foo': 'Bees?', 'bar' : 3},
        {'foo': 'This is a record.', 'bar' : 52},
        ]

florp = Table('florp', test_metadata,
                Column('id', Integer, primary_key=True),
                Column('baz', String(255)),
                Column('flarp_id', Integer, ForeignKey(flarp.c.flarp_id),
                                                        nullable=False),
                Column('created_at', DateTime, server_default=func.now()),
                Column('updated_at', DateTime, onupdate=func.now()),
            )

automated_reports_data = [
        {'report_name': 'test_report_active', 'active': 1},
        {'report_name': 'test_report_inactive', 'active': 0},
        ]

contact_data = [
        {'last_name': 'LAST', 'first_name': 'FIRST', 'email_address': 'speedyturkey@gmail.com'}
        ]

recipient_data = [
        {'contact_id': 1, 'report_id': 1, 'recipient_type': 'to'}
        ]

def create_fixtures(cm):
    cm.conn.execute(flarp.insert(), flarp_data)
    cm.conn.execute(automated_reports.insert(), automated_reports_data)
    cm.conn.execute(automated_report_contacts.insert(), contact_data)
    cm.conn.execute(automated_report_recipients.insert(), recipient_data)
