import unittest
from sqlalchemy.exc import StatementError
from porthole import config
from porthole import ConnectionManager


class TestConnectionManager(unittest.TestCase):

    def test_raise_error_if_no_db(self):
        """Raise an error if no db is provided"""
        cm = ConnectionManager()
        with self.assertRaisesRegex(ValueError, "db attribute not set"):
            cm.connect()

    def test_allow_valid_rdbms_types(self):
        """Raise an error if an unsupported RDBMS is specified."""
        cm = ConnectionManager()
        cm.db = 'Fake_DB'
        cm.config.add_section('Fake_DB')
        cm.config.set('Fake_DB', 'rdbms', 'fakedb')
        cm.unpack_params()
        with self.assertRaisesRegex(ValueError, "Unsupported RDBMS"):
            cm.connect()

    def test_close_connection_successfully(self):
        # TODO This test only works if the 'Test' db is defined in config.ini.
        # TODO Should instead create a test db fixture of some kind.
        cm = ConnectionManager(db='Test')
        cm.connect()
        cm.conn.close()
        with self.assertRaisesRegex(StatementError, "ResourceClosedError"):
            cm.conn.execute("select * from test;")

    def test_context_manager(self):
        with ConnectionManager(db='Test') as cm:
            self.assertFalse(cm.closed())
            cm.conn.execute("select * from flarp;")
        self.assertTrue(cm.closed())
