import sys
import unittest
from random import randint, choice
from porthole import ResultFilter




class TestResultFilter(unittest.TestCase):

    def setUp(self):
        self.fields = ['Name', 'Number']
        self.names = ['Foo', 'Bar', 'Bodoni']
        self.data = [[choice(self.names), randint(0,100)] for _ in range(0,100)]

    def test_filter(self):
        test_filter = ResultFilter(headers=self.fields, data=self.data, filter_by='Name')
        test_filter.filter()
        name_set = set(self.names)
        key_set = set(test_filter.keys)
        self.assertEqual(name_set, key_set)

    def test_header_contains_filter_by_field(self):
        with self.assertRaisesRegex(ValueError, "filter_by value") as context:
            test_filter = ResultFilter(headers=self.fields, data=self.data, filter_by='Baz')

    def test_filter_iteration(self):
        test_filter = ResultFilter(headers=self.fields, data=self.data, filter_by='Name')
        test_filter.filter()
        for key, data in test_filter:
            self.assertTrue(key in self.names)
