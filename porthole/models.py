from sqlalchemy import MetaData, ForeignKey, Table, Column, func
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from .app import config
from . import TimeHelper

try:
    schema = config[config["Default"]["database"]]["schema"]
except:
    schema = None

metadata = MetaData(schema=schema)


Base = declarative_base(metadata=metadata)


class AutomatedReportRecipient(Base):
    __tablename__ = "automated_report_recipients"
    recipient_id = Column("recipient_id", Integer, primary_key=True)
    report_id = Column("report_id", Integer, ForeignKey("automated_reports.report_id"), nullable=False)
    contact_id = Column("contact_id", Integer, ForeignKey("automated_report_contacts.contact_id"), nullable=False)
    recipient_type = Column("recipient_type", String(10), nullable=False)
    created_at = Column("created_at", DateTime, server_default=func.now())
    updated_at = Column("updated_at", DateTime, onupdate=func.now())

    report = relationship("AutomatedReport", backref=backref("report_recipients", cascade="all, delete-orphan"))
    contact = relationship("AutomatedReportContact", backref=backref("receives_reports", cascade="all, delete-orphan"))


class AutomatedReport(Base):
    __tablename__ = "automated_reports"
    report_id = Column("report_id", Integer, primary_key=True)
    report_name = Column("report_name", String(64), nullable=False, unique=True)
    active = Column("active", Integer)
    created_at = Column("created_at", DateTime, server_default=func.now())
    updated_at = Column("updated_at", DateTime, onupdate=func.now())
    report_description = Column("report_description", String(255))
    schedule_minute = Column("schedule_minute", String(32))
    schedule_hour = Column("schedule_hour", String(32))
    schedule_day_of_week = Column("schedule_day_of_week", String(32))
    schedule_day_of_month = Column("schedule_day_of_month", String(32))
    schedule_month_of_year = Column("schedule_month_of_year", String(32))

    contacts = association_proxy("report_recipients", "contact")

    def _get_recipients(self, recipient_type):
        return [
            recipient.contact.email_address
            for recipient in self.report_recipients
            if recipient.recipient_type == recipient_type
        ]

    @property
    def to_recipients(self):
        return self._get_recipients("to")

    @property
    def cc_recipients(self):
        return self._get_recipients("cc")


class AutomatedReportContact(Base):
    __tablename__ = "automated_report_contacts"
    contact_id = Column("contact_id", Integer, primary_key=True)
    last_name = Column("last_name", String(64))
    first_name = Column("first_name", String(64))
    email_address = Column("email_address", String(64))
    created_at = Column("created_at", DateTime, server_default=func.now())
    updated_at = Column("updated_at", DateTime, onupdate=func.now())

    reports = association_proxy("receives_reports", "report")


class ReportLog(Base):
    __tablename__ = "report_logs"
    id = Column("id", Integer, primary_key=True)
    report_name = Column("report_name", String(64), nullable=False)
    started_at = Column("started_at", DateTime)
    completed_at = Column("completed_at", DateTime)
    success = Column("success", Boolean)
    error_detail = Column("error_detail", String(255))
    recipients = Column("recipients", Text)
    created_at = Column("created_at", DateTime, server_default=func.now())
    updated_at = Column("updated_at", DateTime, onupdate=func.now())

    def __init__(self, report_name, started_at=None):
        self.report_name = report_name
        self.started_at = started_at or TimeHelper.now(string=False)

    def finalize(self, recipients=None, errors=None):
        recipients = "; ".join(recipients) if recipients else None
        if errors:
            self.error_detail = "; ".join([str(log.exc_text) for log in errors if hasattr(log, 'exc_text')])[:255]
            self.success = 0
        else:
            self.success = 1
            self.recipients = recipients
        self.completed_at = TimeHelper.now(string=False)


class ReportLogDetail(Base):
    __tablename__ = "report_log_details"
    id = Column("id", Integer, primary_key=True)
    report_log_id = Column("report_log_id", Integer, ForeignKey("report_logs.id"))
    level_number = Column("level_number", Integer)
    level_name = Column("level_name", String(64))
    logger = Column("logger", String(64))
    msg = Column("msg", Text)
    traceback = Column("traceback", Text)
    created_at = Column("created_at", DateTime, server_default=func.now())
    updated_at = Column("updated_at", DateTime, onupdate=func.now())
