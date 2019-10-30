import unittest
# from porthole.contact_management import AutomatedReportContactManager


# class TestAutomatedReportContactManager(unittest.TestCase):
#     def test_add(self):
#         manager = AutomatedReportContactManager("Test")
#         self.assertFalse(
#             manager.report_exists("Foo")
#         )
#         self.assertFalse(
#             manager.contact_exists("chip.dipson@maximumfun.org")
#         )
#         self.assertFalse(
#             manager.contact_exists("dip.dobson@maximumfun.org")
#         )
#         self.assertFalse(
#             manager.report_recipient_exists("Foo", "chip.dipson@maximumfun.org")
#         )
#         self.assertFalse(
#             manager.report_recipient_exists("Foo", "dip.dobson@maximumfun.org")
#         )
#         manager.add_report("Foo")
#         manager.add_contact("Chip", "Dipson", "chip.dipson@maximumfun.org")
#         manager.add_contact("Dip", "Dobson", "dip.dobson@maximumfun.org")
#         manager.add_report_recipient("Foo", "chip.dipson@maximumfun.org", "to")
#         manager.add_report_recipient("Foo", "dip.dobson@maximumfun.org", "cc")
#         self.assertTrue(
#             manager.report_exists("Foo")
#         )
#         self.assertTrue(
#             manager.report_is_active("Foo")
#         )
#         self.assertTrue(
#             manager.contact_exists("chip.dipson@maximumfun.org")
#         )
#         self.assertTrue(
#             manager.contact_exists("dip.dobson@maximumfun.org")
#         )
#         self.assertTrue(
#             manager.report_recipient_exists("Foo", "chip.dipson@maximumfun.org")
#         )
#         self.assertTrue(
#             manager.report_recipient_exists("Foo", "dip.dobson@maximumfun.org")
#         )
#         manager.add_report("Bar", 0)
#         self.assertFalse(
#             manager.report_is_active("Bar")
#         )
#         manager.deactivate_report("Foo")
#         self.assertFalse(
#             manager.report_is_active("Foo")
#         )
#         manager.activate_report("Bar")
#         self.assertTrue(
#             manager.report_is_active("Bar")
#         )
#         manager.remove_report_recipient("Foo", "dip.dobson@maximumfun.org")
#         self.assertFalse(
#             manager.report_recipient_exists("Foo", "dip.dobson@maximumfun.org")
#         )
#
