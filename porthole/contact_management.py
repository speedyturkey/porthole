"""
1. Add report by name
    - first check that report does not exist.
2. Add contact by email + name
3. Add recipient by report name, email, and recipient type
    - create report if report does not exist
    - create contact if contact does not exist
4. Activate report
5. Deactivate report
6. Remove recipient from report
    - Check that recipient exists.

"""
import os
import sqlalchemy as sa
from porthole import ConnectionManager
from porthole.models import metadata, automated_reports, automated_report_contacts, automated_report_recipients


class AutomatedReportContactManager(object):
    def __init__(self, database: str):
        self.database = database

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

    def update_record(self, table: sa.Table, conditions, data: dict):
        # TODO this needs a "where"
        # consider using "expressions" similar to record exists...
        # maybe pull that out into a separate method?
        self.execute_statement(table.update().values(**data))

    def record_exists(self, table: sa.Table, field_value_dict):
        expressions = [
            getattr(table.c, field) == value for field, value in field_value_dict.items()
        ]
        select = sa.sql.select([
            sa.exists().where(sa.and_(*expressions))
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
            return
        self.create_record(
            table=automated_reports,
            data={
                'report_name': report_name,
                'active': active
            }
        )

    def activate_report(self, report_name):
        pass

    def deactivate_report(self, report_name):
        pass

    def report_is_active(self, report_name):
        pass

    def contact_exists(self, email_address: str):
        return self.record_exists(automated_report_contacts, {'email_address': email_address})

    def add_contact(self, last_name: str = None, first_name: str = None, email_address: str = None):
        if self.contact_exists(email_address):
            return
        self.create_record(
            table=automated_report_contacts,
            data={
                'last_name': last_name,
                'first_name': first_name,
                'email_address': email_address
            }
        )

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
            return None
        self.create_record(
            table=automated_report_recipients,
            data={
                'report_id': self.get_record_id(automated_reports, 'report_name', report_name),
                'contact_id': self.get_record_id(automated_report_contacts, 'email_address', email_address),
                'recipient_type': recipient_type
            }
        )


def setup_test_db():
    with ConnectionManager("Test") as cm:
        metadata.create_all(cm.engine)
        cm.commit()


def teardown_test_db():
    try:
        os.unlink('test.db')
    except FileNotFoundError:
        pass


def test():
    manager = AutomatedReportContactManager("Test")
    manager.add_report("baz", 1)
    manager.add_contact("McMonagle", "William", "william.mcmonagle@ankura.com")
    manager.add_contact(email_address="speedyturkey@gmail.com")
    manager.add_report_recipient("baz", "speedyturkey@gmail.com", "to")
    manager.add_report_recipient("baz", "william.mcmonagle@ankura.com", "cc")
