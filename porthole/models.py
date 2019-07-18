from .app import config
from sqlalchemy import MetaData, ForeignKey, Table, Column, func
from sqlalchemy import Boolean, DateTime, Integer, String, Text

try:
    schema = config[config['Default']['database']]['schema']
except:
    schema = None

metadata = MetaData(schema=schema)

automated_reports = Table(
    'automated_reports',
    metadata,
    Column('report_id', Integer, primary_key=True),
    Column('report_name', String(64), nullable=False),
    Column('active', Integer),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, onupdate=func.now()),
    Column('report_description', String(255)),
    Column('schedule_minute', String(32)),
    Column('schedule_hour', String(32)),
    Column('schedule_day_of_week', String(32)),
    Column('schedule_day_of_month', String(32)),
    Column('schedule_month_of_year', String(32))
)

automated_report_contacts = Table(
    'automated_report_contacts',
    metadata,
    Column('contact_id', Integer, primary_key=True),
    Column('last_name', String(64)),
    Column('first_name', String(64)),
    Column('email_address', String(64)),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, onupdate=func.now()),
)

automated_report_recipients = Table(
    'automated_report_recipients',
    metadata,
    Column('recipient_id', Integer, primary_key=True),
    Column('report_id', Integer, ForeignKey(automated_reports.c.report_id), nullable=False),
    Column('contact_id', Integer, ForeignKey(automated_report_contacts.c.contact_id), nullable=False),
    Column('recipient_type', String(10), nullable=False),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, onupdate=func.now()),
)

report_logs = Table(
    'report_logs', metadata,
    Column('id', Integer, primary_key=True),
    Column('report_name', String(64), nullable=False),
    Column('started_at', DateTime),
    Column('completed_at', DateTime),
    Column('success', Boolean),
    Column('error_detail', String(255)),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, onupdate=func.now()),
)

report_log_details = Table(
    'report_log_details',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('report_log_id', Integer, ForeignKey(report_logs.c.id)),
    Column('level_number', Integer),
    Column('level_name', String(64)),
    Column('logger', String(64)),
    Column('msg', Text),
    Column('traceback', Text),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, onupdate=func.now()),
)
