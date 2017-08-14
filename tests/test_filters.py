import sys
import unittest
from random import randint, choice
from porthole import QueryResult, ResultFilter




class TestResultFilter(unittest.TestCase):

    def setUp(self):
        self.fields = ['Name', 'Number']
        self.names = ['Foo', 'Bar', 'Bodoni']
        self.data = [[choice(self.names), randint(0,100)] for _ in range(0,100)]
        self.result = QueryResult(field_names=self.fields, result_data=self.data)

    def test_filter(self):
        test_filter = ResultFilter(result_to_filter=self.result, filter_by='Name')
        test_filter.filter()
        name_set = set(self.names)
        key_set = set(test_filter.keys)
        filtered_data_keys = set(test_filter.filtered_data.keys())
        filtered_result_keys = set(test_filter.filtered_results.keys())
        self.assertEqual(name_set, key_set)
        self.assertEqual(filtered_data_keys, filtered_result_keys)

    def test_header_contains_filter_by_field(self):
        with self.assertRaisesRegex(ValueError, "filter_by value") as context:
            test_filter = ResultFilter(result_to_filter=self.result, filter_by='Baz')

    def test_filter_iteration(self):
        test_filter = ResultFilter(result_to_filter=self.result, filter_by='Name')
        test_filter.filter()
        for key, data in test_filter:
            self.assertTrue(key in self.names)
