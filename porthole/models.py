from .app import config
from sqlalchemy import MetaData, ForeignKey, Table, Column, Integer, String, DateTime, Boolean, func

schema = config[config['Default']['database']]['schema']
metadata = MetaData(schema=schema)

automated_reports = Table('automated_reports', metadata,
                Column('report_id', Integer, primary_key=True),
                Column('report_name', String(64), nullable=False),
                Column('active', Integer),
                Column('created_at', DateTime, server_default=func.now()),
                Column('updated_at', DateTime, onupdate=func.now()),
            )

automated_report_contacts = Table('automated_report_contacts', metadata,
                Column('contact_id', Integer, primary_key=True),
                Column('last_name', String(64)),
                Column('first_name', String(64)),
                Column('email_address', String(64)),
                Column('created_at', DateTime, server_default=func.now()),
                Column('updated_at', DateTime, onupdate=func.now()),
            )

automated_report_recipients = Table('automated_report_recipients', metadata,
                Column('recipient_id', Integer, primary_key=True),
                Column('report_id', Integer, ForeignKey(automated_reports.c.report_id),
                                                        nullable=False),
                Column('contact_id', Integer, ForeignKey(automated_report_contacts.c.contact_id),
                                                        nullable=False),
                Column('recipient_type', String(10), nullable=False),
                Column('created_at', DateTime, server_default=func.now()),
                Column('updated_at', DateTime, onupdate=func.now()),
            )

report_logs = Table('report_logs', metadata,
                Column('id', Integer, primary_key=True),
                Column('report_name', String(64), nullable=False),
                Column('started_at', DateTime),
                Column('completed_at', DateTime),
                Column('success', Boolean),
                Column('error_detail', String(255)),
                Column('created_at', DateTime, server_default=func.now()),
                Column('updated_at', DateTime, onupdate=func.now()),
            )
