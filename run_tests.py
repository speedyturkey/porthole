import os
import unittest
from porthole import config, ConnectionManager
from porthole.models import metadata
from tests.fixtures import test_metadata, create_fixtures


def setup_test_db():
    db = config['Default']['database']
    if config[db]['rdbms'] == 'sqlite':
        cm = ConnectionManager(db)
        cm.connect()
        metadata.create_all(cm.engine)
        test_metadata.create_all(cm.engine)
        create_fixtures(cm)
        cm.close()
    if config[db]['rdbms'] == 'mysql':
        with ConnectionManager(db) as cm:
            metadata.create_all(cm.engine)
            test_metadata.create_all(cm.engine)
            create_fixtures(cm)


def teardown_test_db():
    db = config['Default']['database']
    try:
        os.unlink('test.db')
    except FileNotFoundError:
        pass
    if config[db]['rdbms'] == 'mysql':
        with ConnectionManager(db) as cm:
            metadata.drop_all(cm.engine)
            test_metadata.drop_all(cm.engine)


def main():
    suite = unittest.defaultTestLoader.discover(start_dir="tests")
    unittest.TextTestRunner(verbosity=1).run(suite)


if __name__ == '__main__':
    setup_test_db()
    main()
    teardown_test_db()
