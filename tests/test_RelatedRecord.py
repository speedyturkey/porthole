import sys
import unittest
from porthole import RelatedRecord, ChildRecord, ConnectionManager


class TestRelatedRecord(unittest.TestCase):

    def setUp(self):
        cm = ConnectionManager()
        cm.rdbms = 'sqlite'
        cm.schema = 'main'
        cm.db = 'test'
        cm.db_host = 'test.db'
        cm.engine = cm.create_engine()
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

    def test_insert_parent_and_child(self):
        """When provided valid parameters, related records should be inserted."""
        parent_record, child_record = insert_parent_and_child(self.cm)
        self.assertTrue(parent_record.inserted)
        self.assertTrue(child_record.inserted)
        self.assertEqual(parent_record.primary_key, child_record.foreign_key)

    def test_insert_parent_and_children(self):
        """When provided valid parameters, a record should be inserted with multiple children,
        which have a common foreign key defining their relationship."""
        parent, first_child, second_child = insert_parent_and_children(self.cm)
        self.assertEqual(parent.primary_key, first_child.foreign_key)
        self.assertEqual(first_child.foreign_key, second_child.foreign_key)
        self.assertEqual(first_child.primary_key, second_child.primary_key - 1)


def basic_insert_and_update(cm):
    record = RelatedRecord(cm, 'flarp')
    record.insert({'foo': "Test text",
                        'bar': 123})
    return record

def insert_parent_and_child(cm):
    parent_record = RelatedRecord(cm, 'flarp')
    parent_record.insert({'foo': 'foo flarp'})
    child_record = ChildRecord(cm, 'florp', parent_record)
    child_record.insert({'baz': 'foo bar baz'})
    return parent_record, child_record

def multiple_inserts(cm):
    first_record = RelatedRecord(cm, 'flarp')
    first_record.insert({'foo': "First record",
                        'bar': 456})
    second_record = RelatedRecord(cm, 'flarp')
    second_record.insert({'foo': "Second record",
                        'bar': 456})
    return first_record, second_record

def insert_parent_and_children(cm):
    parent = RelatedRecord(cm, 'flarp')
    parent.insert({'foo': 'Large Dog'})
    first_child = ChildRecord(cm, 'florp', parent)
    first_child.insert({'baz': 'Small Dog'})
    second_child = ChildRecord(cm, 'florp', parent)
    second_child.insert({'baz': 'Tiny Dog'})
    return parent, first_child, second_child

def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRelatedRecord)
    unittest.TextTestRunner(verbosity=3).run(suite)

if __name__ == '__main__':
    unittest.main()
