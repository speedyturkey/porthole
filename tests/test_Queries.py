import os, unittest, json
from datetime import date
from collections import OrderedDict
from porthole import QueryGenerator, QueryReader, QueryResult, QueryExecutor
from porthole.queries import RowDict


class TestQueries(unittest.TestCase):

    def test_queryresult(self):
        """Instantiate JSONWriter and write to file"""
        filename = 'test.json'
        result = QueryResult(field_names=headers, result_data=data)
        result.write_to_json(filename)
        with open(filename) as json_data:
            d = json.load(json_data)
        self.assertIn('Name', d[0])
        self.assertEqual(d[0]['DOB'], '1988-04-24')
        os.unlink(filename)

    def test_queryresult_map(self):
        result = QueryResult(field_names=headers, result_data=data)
        with self.assertRaises(AssertionError):
            result.map_function_to_field('NOTEXIST', lambda txt: txt.upper())
        result.map_function_to_field('Name', lambda txt: txt.upper())
        self.assertEqual('BILLY', result.result_data[0]['Name'])

        def lower_name(row):
            row['Name'] = row['Name'].lower()

        result.apply(lower_name)
        self.assertEqual('billy', result.result_data[0]['Name'])
        self.assertEqual('erika', result.result_data[1]['Name'])

    def test_queryreader_no_params(self):
        """A QueryReader can be instantiated when no parameters are required."""
        s = QueryReader(filename='tests/test_query_no_params')
        self.assertTrue(s.raw_sql, s.sql)
        self.assertIsNotNone(s.sql)

    def test_queryreader_params(self):
        """A QueryReader can be instantiated when all required parameters are provided."""
        s = QueryReader(filename='tests/test_query_with_params', params = {'foo': 'value1', 'b_ar': 'value2', 'Baz': 'value3'})
        self.assertNotEqual(s.raw_sql, s.sql)
        self.assertIsNotNone(s.raw_sql)
        self.assertIsNotNone(s.sql)

    def test_queryreader_missing_param(self):
        """A QueryReader instantiated with missing parameters raises a NameError."""
        with self.assertRaises(NameError):
            s = QueryReader(filename='tests/test_query_with_params', params = {'foo': 'value1'})

    def test_queryreader_validate(self):
        """The QueryReader.validate() method raises a NameError when parameters are missing."""
        s = QueryReader()
        s.sql = "select * from table where foo = #{flarp}"
        with self.assertRaises(NameError):
            s.validate()

    def test_QueryExecutor(self):
        executor = QueryExecutor(db='Test')
        executor.create_database_connection()
        self.assertFalse(executor.cm.conn.closed)
        result1 = executor.execute_query(sql='select * from flarp;')
        self.assertIsInstance(result1, QueryResult)
        executor.close_database_connection()
        self.assertTrue(executor.cm.conn.closed)
        with QueryExecutor(db='Test') as qe:
            self.assertFalse(qe.cm.conn.closed)
            result2 = qe.execute_query(sql='select * from flarp;')
            self.assertIsInstance(result2, QueryResult)


class TestRowDict(unittest.TestCase):

    def test_init(self):
        test_obj_1 = RowDict(data=OrderedDict(zip(headers, row1)))
        test_obj_2 = RowDict(fields=headers, values=row1)
        self.assertEqual(len(test_obj_1), 2)
        self.assertEqual(test_obj_1, test_obj_2)
        for header in headers:
            self.assertIn(header, test_obj_1)
        for value in row1:
            self.assertIn(value, test_obj_1.values())
        zipped = zip(test_obj_1, row1)
        for one, the_other in zipped:
            self.assertEqual(one, the_other)

    def test_iteration(self):
        test_row = RowDict(fields=headers, values=row1)
        self.assertEqual(headers, list(test_row.keys()))
        self.assertEqual(row1, list(test_row.values()))
        for value in test_row:
            self.assertIn(value, row1)
        items = test_row.items()
        zipped_key_values = zip(test_row.keys(), test_row.values())
        for one, the_other in zip(items, zipped_key_values):
            self.assertEqual(one, the_other)

    def test_behavior(self):
        test_row = RowDict(fields=headers, values=row1)
        test_row['Foo'] = 'Bar'
        self.assertIn('Foo', test_row)
        self.assertIn('Bar', test_row.values())
        self.assertEqual(headers + ['Foo'], list(test_row.keys()))


headers = ['Name', 'DOB']
row1 = ['Billy', date(1988, 4, 24)]
row2 = ['Erika', date(1988, 9, 20)]
data = [row1, row2]
