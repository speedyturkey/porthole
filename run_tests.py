import os, sys
import unittest
from porthole import config, ConnectionManager, RelatedRecord, ChildRecord
from porthole.models import metadata
from tests.fixtures import test_metadata, create_fixtures
from tests.test_ConnectionManager import TestConnectionManager
from tests.test_SimpleWorkflow import TestSimpleWorkflow
from tests.test_RelatedRecord import TestRelatedRecord
from tests.test_GenericReport import TestGenericReport
from tests.test_Queries import TestQueries
# Query Handlers
# Time Helper
# XLSX

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

def setup_test_db():
    db = config['Default']['database']
    cm = ConnectionManager(db)
    cm.connect()
    metadata.create_all(cm.engine)
    test_metadata.create_all(cm.engine)
    create_fixtures(cm)
    cm.close()

def teardown_test_db():
    try:
        os.unlink('test.db')
    except FileNotFoundError:
        pass

def main():
    # blockPrint()

    # Select all of your test classes here.
    test_classes_to_run = [
                            TestConnectionManager,
                            TestSimpleWorkflow,
                            TestRelatedRecord,
                            TestGenericReport,
                            TestQueries
                            ]

    # Setup
    loader = unittest.TestLoader()
    suites_list = []
    # Process and load test suites
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)
    # Test all of the things!
    executive_test_suite = unittest.TestSuite(suites_list)
    unittest.TextTestRunner(verbosity=1).run(executive_test_suite)

    # enablePrint()


if __name__ == '__main__':
    setup_test_db()
    main()
    # teardown_test_db()
