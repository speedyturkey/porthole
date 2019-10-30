import os
import unittest
from porthole import config, ConnectionManager
from porthole.app import default_engine, Session
from porthole.models import Base
from porthole.models import metadata
from tests.fixtures import test_metadata, create_fixtures


def setup_test_db():
    db = config['Default']['database']
    if config[db]['rdbms'] == 'sqlite':
        cm = ConnectionManager(db)
        cm.connect()
        Base.metadata.create_all(default_engine)
        test_metadata.create_all(cm.engine)
        create_fixtures(cm)
        cm.close()
    if config[db]['rdbms'] == 'mysql':
        Base.metadata.create_all(default_engine)
        with ConnectionManager(db) as cm:
            test_metadata.create_all(cm.engine)
            create_fixtures(cm)


def teardown_test_db():
    db = config['Default']['database']
    try:
        os.unlink('test.db')
    except FileNotFoundError:
        pass
    Session.close_all()
    if config[db]['rdbms'] == 'mysql':
        Base.metadata.drop_all(default_engine)
        with ConnectionManager(db) as cm:
            test_metadata.drop_all(cm.engine)


def main():
    suite = unittest.defaultTestLoader.discover(start_dir="tests")
    unittest.TextTestRunner(verbosity=1).run(suite)


if __name__ == '__main__':
    teardown_test_db()
    setup_test_db()
    main()
    teardown_test_db()
