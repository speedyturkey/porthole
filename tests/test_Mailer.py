import unittest
from porthole import Mailer, config


class TestMailer(unittest.TestCase):
    def test_default_construction(self):
        global_debug = config.getboolean('Debug', 'debug_mode')
        mailer = Mailer()
        self.assertEqual(global_debug, mailer.debug_mode)
        self.assertEqual(mailer.recipients, [])
        self.assertEqual(mailer.cc_recipients, [])

    def test_runtime_debug(self):
        config.set('Debug', 'debug_mode', 'False')
        mailer = Mailer(debug_mode=True)
        self.assertTrue(mailer.debug_mode)
        self.assertNotEquals(config['Debug']['debug_mode'], mailer.debug_mode)
