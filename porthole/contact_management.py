import sqlalchemy as sa
from porthole import ConnectionManager
from .logger import PortholeLogger
from porthole.models import automated_reports, automated_report_contacts, automated_report_recipients


class AutomatedReportContactManager(object):
    def __init__(self, database: str):
        self.database = database
        self.logger = PortholeLogger(name=__name__)

    def execute_statement(self, statement: sa.sql.base.Executable):
        with ConnectionManager(self.database) as cm:
            proxy = cm.conn.execute(statement)
            if proxy.cursor:
                result = proxy.fetchall()
            else:
                result = None
        return result

    def create_record(self, table: sa.Table, data: dict):
        self.execute_statement(table.insert().values(**data))

    def update_record(self, table: sa.Table, conditions: dict, data: dict):
        expression = self.compile_binary_expression(table, conditions)
        self.execute_statement(table.update().where(expression).values(**data))

    def delete_record(self, table: sa.Table, conditions: dict):
        expression = self.compile_binary_expression(table, conditions)
        self.execute_statement(table.delete().where(expression))

    @staticmethod
    def compile_binary_expression(table: sa.Table, field_value_dict: dict):
        expressions = [
            getattr(table.c, field) == value for field, value in field_value_dict.items()
        ]
        return sa.and_(*expressions)

    def record_exists(self, table: sa.Table, field_value_dict):
        expression = self.compile_binary_expression(table, field_value_dict)
        select = sa.sql.select([
            sa.exists().where(expression)
        ])
        try:
            return self.execute_statement(select)[0][0]
        except IndexError:
            return False

    def get_record_id(self, table: sa.Table, field, value):
        select = sa.sql.select(
            [table]
        ).where(
            getattr(table.c, field) == value
        )
        try:
            return self.execute_statement(select)[0][0]
        except IndexError:
            return None

    def report_exists(self, report_name):
        return self.record_exists(automated_reports, {'report_name': report_name})

    def add_report(self, report_name: str, active: int = 1):
        if self.report_exists(report_name):
            self.logger.warning(f"{report_name} already exists")
            return None
        self.create_record(
            table=automated_reports,
            data={
                'report_name': report_name,
                'active': active
            }
        )
        self.logger.info(f"Report '{report_name}' created successfully")

    def report_is_active(self, report_name):
        return self.record_exists(automated_reports, {'report_name': report_name, 'active': 1})

    def activate_report(self, report_name):
        if self.report_is_active(report_name):
            self.logger.warning(f"Report '{report_name}' is already active")
            return None
        self.update_record(automated_reports, {'report_name': report_name}, {'active': 1})
        self.logger.info(f"Report '{report_name}' is now active")

    def deactivate_report(self, report_name):
        if not self.report_is_active(report_name):
            self.logger.warning(f"Report '{report_name}' is already inactive")
            return None
        self.update_record(automated_reports, {'report_name': report_name}, {'active': 0})
        self.logger.info(f"Report '{report_name}' is now inactive")

    def contact_exists(self, email_address: str):
        return self.record_exists(automated_report_contacts, {'email_address': email_address})

    def add_contact(self, last_name: str = None, first_name: str = None, email_address: str = None):
        if self.contact_exists(email_address):
            self.logger.warning(f"Contact {last_name}, {first_name} ({email_address}) already exists ")
            return None
        self.create_record(
            table=automated_report_contacts,
            data={
                'last_name': last_name,
                'first_name': first_name,
                'email_address': email_address
            }
        )
        self.logger.info(f"Contact {last_name}, {first_name} ({email_address}) created successfully")

    def report_recipient_exists(self, report_name: str, email_address: str):
        return self.record_exists(
            table=automated_report_recipients,
            field_value_dict={
                'report_id': self.get_record_id(automated_reports, "report_name", report_name),
                'contact_id': self.get_record_id(automated_report_contacts, "email_address", email_address)
            }
        )

    def add_report_recipient(self, report_name: str, email_address: str, recipient_type: str):
        if recipient_type not in ['to', 'cc']:
            raise ValueError("Recipient type must be either `to` or `cc`.")
        if self.report_recipient_exists(report_name, email_address):
            self.logger.warning(f"Recipient '{email_address}' already exists for report '{report_name}'")
            return None
        self.create_record(
            table=automated_report_recipients,
            data={
                'report_id': self.get_record_id(automated_reports, 'report_name', report_name),
                'contact_id': self.get_record_id(automated_report_contacts, 'email_address', email_address),
                'recipient_type': recipient_type
            }
        )
        self.logger.info(f"{recipient_type} recipient '{email_address}' added successfully to report '{report_name}'")

    def remove_report_recipient(self, report_name: str, email_address: str):
        if not self.report_recipient_exists(report_name, email_address):
            self.logger.warning(f"Recipient '{email_address}' does not exist for report '{report_name}'")
            return None
        self.delete_record(
            table=automated_report_recipients,
            conditions={
                'report_id': self.get_record_id(automated_reports, 'report_name', report_name),
                'contact_id': self.get_record_id(automated_report_contacts, 'email_address', email_address),
            }
        )
        self.logger.info(f"Recipient '{email_address}' removed successfully from report '{report_name}'")
