import os, unittest, json
from datetime import date
from porthole import QueryGenerator, QueryReader, QueryResult

class TestQueries(unittest.TestCase):

    def test_queryresult(self):
        "Instantiate JSONWriter and write to file"
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
        with self.assertRaises(IndexError):
            result.map_function_to_field('NOTEXIST', lambda txt: txt.upper())
        result.map_function_to_field('Name', lambda txt: txt.upper())
        self.assertEqual('BILLY', result.result_data[0][0])

    def test_queryreader_no_params(self):
        "A QueryReader can be instantiated when no paramters are required."
        s = QueryReader(filename='tests/test_query_no_params')
        self.assertTrue(s.raw_sql, s.sql)
        self.assertIsNotNone(s.sql)

    def test_queryreader_params(self):
        "A QueryReader can be instantiated when all required parameters are provided."
        s = QueryReader(filename='tests/test_query_with_params', params = {'foo': 'value1', 'bar': 'value2'})
        self.assertNotEqual(s.raw_sql, s.sql)
        self.assertIsNotNone(s.raw_sql)
        self.assertIsNotNone(s.sql)

    def test_queryreader_missing_param(self):
        "A QueryReader instantiated with missing parameters raises a NameError."
        with self.assertRaises(NameError):
            s = QueryReader(filename='tests/test_query_with_params', params = {'foo': 'value1'})

    def test_queryreader_validate(self):
        "The QueryReader.validate() method raises a NameError when parameters are missing."
        s = QueryReader()
        s.sql = "select * from table where foo = #{flarp}"
        with self.assertRaises(NameError):
            s.validate()



headers = ['Name', 'DOB']
row1 = ['Billy', date(1988, 4, 24)]
row2 = ['Erika', date(1988, 9, 20)]
data = [row1, row2]
