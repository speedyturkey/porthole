import unittest
from porthole import DataTask


class TestDataTask(unittest.TestCase):
    def test_data_task(self):
        task = DataTask("test_report_active", lambda: 1 + 1)
        self.assertIsNone(task.success)
        task.execute()
        self.assertTrue(task.success)

    def test_failure_task(self):
        task = DataTask("test_report_active", lambda: 1/0)
        with self.assertRaises(Exception) as context:
            task.execute()
        self.assertTrue("division by zero" in str(context.exception))
        self.assertFalse(task.success)

    def test_non_callable_task(self):
        with self.assertRaises(TypeError) as context:
            _ = DataTask("test_report_active", "not a task")
        self.assertTrue("requires a callable task function" in str(context.exception))
