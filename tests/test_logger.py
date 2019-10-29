import unittest
from porthole import PortholeLogger


class TestLogger(unittest.TestCase):
    def test_logger_basic_setup(self):
        logger = PortholeLogger(name="test_logger_basic_setup")
        self.assertEqual("test_logger_basic_setup", logger.logger.name)
        self.assertIn(
            "stream_handler",
            [h.name for h in logger.logger.handlers]
        )
        self.assertIn(
            "error_buffer",
            [h.name for h in logger.logger.handlers]
        )
        self.assertNotIn(
            "database_handler",
            [h.name for h in logger.logger.handlers]
        )

