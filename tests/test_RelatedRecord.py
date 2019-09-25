import unittest
from porthole import config, RelatedRecord, ConnectionManager


class TestRelatedRecord(unittest.TestCase):

    def setUp(self):
        db = config['Default']['database']
        cm = ConnectionManager(db)
        cm.connect()
        self.cm = cm

    def tearDown(self):
        self.cm.close()

    def test_basic_insert_and_update(self):
        """When provided valid parameters, a record should be inserted."""
        record = basic_insert_and_update(self.cm)
        record.update = {'foo': 'Billy', 'bar': 1}
        self.assertTrue(record.inserted)
        self.assertIsInstance(record.primary_key, int)

    def test_multiple_inserts(self):
        """Sequentially inserted records should have sequential keys."""
        first_record, second_record = multiple_inserts(self.cm)
        self.assertEqual(first_record.primary_key, second_record.primary_key - 1)


def basic_insert_and_update(cm):
    record = RelatedRecord(cm, 'flarp')
    record.insert({'foo': "Test text",
                        'bar': 123})
    return record


def multiple_inserts(cm):
    first_record = RelatedRecord(cm, 'flarp')
    first_record.insert({'foo': "First record",
                        'bar': 456})
    second_record = RelatedRecord(cm, 'flarp')
    second_record.insert({'foo': "Second record",
                        'bar': 456})
    return first_record, second_record


def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRelatedRecord)
    unittest.TextTestRunner(verbosity=3).run(suite)


if __name__ == '__main__':
    unittest.main()
