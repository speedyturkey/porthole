import os, sys
import unittest
from porthole import config, ConnectionManager
from porthole.models import metadata
from tests.fixtures import test_metadata, create_fixtures
from tests.test_AutomatedReportContactManager import TestAutomatedReportContactManager
from tests.test_ConnectionManager import TestConnectionManager
from tests.test_Mailer import TestMailer
from tests.test_SimpleWorkflow import TestSimpleWorkflow
from tests.test_RelatedRecord import TestRelatedRecord
from tests.test_Reports import TestBasicReport, TestGenericReport, TestReportRunner
from tests.test_Queries import TestQueries, TestRowDict
from tests.test_components import TestReportWriter, TestReportActiveChecker
from tests.test_filters import TestResultFilter
# Query Handlers
# Time Helper
from tests.test_WorkbookBuilder import TestWorkbookBuilder

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')


# Restore
def enablePrint():
    sys.stdout = sys.__stdout__


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
    # blockPrint()

    # Select all of your test classes here.
    test_classes_to_run = [
        # TestAutomatedReportContactManager,
        # TestConnectionManager,
        # TestSimpleWorkflow,
        # TestRelatedRecord,
        # TestBasicReport,
        TestGenericReport,
        # TestMailer,
        # TestReportRunner,
        # TestQueries,
        # TestRowDict,
        # TestReportWriter,
        # TestReportActiveChecker,
        # TestResultFilter,
        # TestWorkbookBuilder
    ]

    # Setup
    loader = unittest.TestLoader()
    # # Process and load test suites
    suites_list = [loader.loadTestsFromTestCase(test_class) for test_class in test_classes_to_run]
    # Test all of the things!
    executive_test_suite = unittest.TestSuite(suites_list)
    unittest.TextTestRunner(verbosity=1).run(executive_test_suite)

    # enablePrint()


if __name__ == '__main__':
    setup_test_db()
    main()
    teardown_test_db()
