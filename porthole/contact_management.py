from sqlalchemy.orm.exc import NoResultFound
from porthole.app import Session
from .logger import PortholeLogger
from porthole.models import AutomatedReport, AutomatedReportContact, AutomatedReportRecipient


class AutomatedReportContactManager(object):
    def __init__(self, session=None):
        self.session = session or Session()
        self.logger = PortholeLogger(name=__name__)

    def get_report_by_name(self, report_name, should_exist=False):
        report = self.session.query(AutomatedReport).filter_by(report_name=report_name).one_or_none()
        if report is None and should_exist:
            raise NoResultFound(f"Report {report_name} should exist but no record was found.")
        return report

    def report_exists(self, report_name):
        report = self.get_report_by_name(report_name)
        return report is not None

    def add_report(self, report_name: str, active: int = 1):
        if self.report_exists(report_name):
            self.logger.warning(f"{report_name} already exists")
            return None
        report = AutomatedReport(report_name=report_name, active=active)
        self.session.add(report)
        self.session.commit()
        self.logger.info(f"Report '{report_name}' created successfully")

    def report_is_active(self, report_name):
        report = self.get_report_by_name(report_name, should_exist=True)
        return bool(report.active)

    def activate_report(self, report_name):
        if self.report_is_active(report_name):
            self.logger.warning(f"Report '{report_name}' is already active")
            return None
        report = self.get_report_by_name(report_name, should_exist=True)
        report.active = 1
        self.session.commit()
        self.logger.info(f"Report '{report_name}' is now active")

    def deactivate_report(self, report_name):
        if not self.report_is_active(report_name):
            self.logger.warning(f"Report '{report_name}' is already inactive")
            return None
        report = self.get_report_by_name(report_name, should_exist=True)
        report.active = 0
        self.session.commit()
        self.logger.info(f"Report '{report_name}' is now inactive")

    def get_contact_by_email_address(self, email_address, should_exist=False):
        contact = self.session.query(AutomatedReportContact).filter_by(
            email_address=email_address
        ).one_or_none()
        if contact is None and should_exist:
            raise NoResultFound(f"Contact with email {email_address} should exist but no record was found.")
        return contact

    def contact_exists(self, email_address: str):
        contact = self.get_contact_by_email_address(email_address)
        return contact is not None

    def add_contact(self, last_name: str = None, first_name: str = None, email_address: str = None):
        if self.contact_exists(email_address):
            self.logger.warning(f"Contact {last_name}, {first_name} ({email_address}) already exists ")
            return None
        contact = AutomatedReportContact(last_name=last_name, first_name=first_name, email_address=email_address)
        self.session.add(contact)
        self.session.commit()
        self.logger.info(f"Contact {last_name}, {first_name} ({email_address}) created successfully")

    def get_report_recipient(self, report_name: str, email_address: str, should_exist: bool = False):
        report = self.get_report_by_name(report_name, should_exist=True)
        contact = self.get_contact_by_email_address(email_address, should_exist=True)
        recipient = self.session.query(AutomatedReportRecipient).filter_by(
            report_id=report.report_id, contact_id=contact.contact_id
        ).one_or_none()
        if recipient is None and should_exist:
            raise NoResultFound(
                f"Recipient for report {report_name} with email {email_address} should exist but no record was found."
            )
        return recipient

    def report_recipient_exists(self, report_name: str, email_address: str):
        recipient = self.get_report_recipient(report_name, email_address)
        return recipient is not None

    def add_report_recipient(self, report_name: str, email_address: str, recipient_type: str):
        if recipient_type not in ['to', 'cc']:
            raise ValueError("Recipient type must be either `to` or `cc`.")
        if self.report_recipient_exists(report_name, email_address):
            self.logger.warning(f"Recipient '{email_address}' already exists for report '{report_name}'")
            return None
        report = self.get_report_by_name(report_name, should_exist=True)
        contact = self.get_contact_by_email_address(email_address, should_exist=True)
        recipient = AutomatedReportRecipient(
            report_id=report.report_id, contact_id=contact.contact_id, recipient_type=recipient_type
        )
        self.session.add(recipient)
        self.session.commit()
        self.logger.info(f"{recipient_type} recipient '{email_address}' added successfully to report '{report_name}'")

    def remove_report_recipient(self, report_name: str, email_address: str):
        if not self.report_recipient_exists(report_name, email_address):
            self.logger.warning(f"Recipient '{email_address}' does not exist for report '{report_name}'")
            return None
        recipient = self.get_report_recipient(report_name, email_address)
        self.session.delete(recipient)
        self.session.commit()
        self.logger.info(f"Recipient '{email_address}' removed successfully from report '{report_name}'")
