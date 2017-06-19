import sys
import unittest
from porthole import SimpleWorkflow

class TestSimpleWorkflow(unittest.TestCase):

    def test_execute_single_function_pass(self):
        """A single function with no parameters should be executed,
        and its success should be reported."""
        functions = [
                    {'function': true_function, 'args': {}}
                    ]
        workflow = SimpleWorkflow(functions=functions)
        workflow.run()
        self.assertTrue(workflow.completed)
        self.assertIsNone(workflow.failed_on)

    def test_execute_single_function_fail(self):
        """A single function with no parameters should be executed,
        and its failure should be reported."""
        functions = [
                    {'function': false_function, 'args': {}}
                    ]
        workflow = SimpleWorkflow(functions=functions)
        workflow.run()
        self.assertFalse(workflow.completed)
        self.assertIsNotNone(workflow.failed_on)

    def test_function_with_params_pass(self):
        """A single function with one parameter should be executed,
        and its success should be reported."""
        functions = [
                    {'function': function_with_param, 'args': {'param': True}}
                    ]
        workflow = SimpleWorkflow(functions=functions)
        workflow.run()
        self.assertTrue(workflow.completed)
        self.assertIsNone(workflow.failed_on)

    def test_function_with_params_fail(self):
        """A single function with one parameter should be executed,
        and its failure should be reported."""
        functions = [
                    {'function': function_with_param, 'args': {'param': False}}
                    ]
        workflow = SimpleWorkflow(functions=functions)
        workflow.run()
        self.assertFalse(workflow.completed)
        self.assertIsNotNone(workflow.failed_on)

    def test_multiple_functions_all_pass(self):
        """Multiple function with one parameter should be executed,
        and its success should be reported."""
        functions = [
                    {'function': function_with_param, 'args': {'param': True}},
                    {'function': other_function_with_param, 'args': {'other_param': True}}
                    ]
        workflow = SimpleWorkflow(functions=functions)
        workflow.run()
        self.assertTrue(workflow.completed)
        self.assertIsNone(workflow.failed_on)

    def test_multiple_functions_with_failure(self):
        """Multiple function with one parameter should be executed,
        and its success should be reported."""
        functions = [
                    {'function': function_with_param, 'args': {'param': True}},
                    {'function': other_function_with_param, 'args': {'other_param': False}},
                    {'function': function_with_param, 'args': {'param': True}}
                    ]
        workflow = SimpleWorkflow(functions=functions)
        workflow.run()
        self.assertFalse(workflow.completed)
        self.assertEqual(workflow.failed_on['function'].__name__, 'other_function_with_param')

    def test_exceptions_cause_overall_failure(self):
        """If one of the functions raises an exception, it should be handled and the overall
        workflow should be considered a failure."""
        functions = [
                    {'function': function_with_param, 'args': {'param': True}},
                    {'function': raise_exception, 'args': {}}
                    ]
        workflow = SimpleWorkflow(functions=functions)
        workflow.run()
        self.assertFalse(workflow.completed)

def true_function():
    return True

def false_function():
    return False

def function_with_param(param):
    if param:
        return True
    else:
        return False

def other_function_with_param(other_param):
    if other_param:
        return True
    else:
        return False

def raise_exception():
    raise Exception

def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimpleWorkflow)
    unittest.TextTestRunner(verbosity=3).run(suite)

if __name__ == '__main__':
    unittest.main()
