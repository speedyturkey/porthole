
"""
RelatedRecord.py
Created by William McMonagle on 01/03/17.
Contains classes to allow for inserting, tracking, and associating of new db log records
with parent/child relationships.
"""
from sqlalchemy import Table, MetaData, ForeignKey


class RelatedRecord(object):
    """
    Represents a database record; provides insert/update functionality of
    of individual records.
    """
    def __init__(self, connection_manager, table):
        self.cm = connection_manager
        self.table = Table(table,
                            MetaData(schema=connection_manager.schema),
                            autoload=True,
                            autoload_with=connection_manager.engine)
        self.primary_key_name = self.inspect_primary_key()
        self.primary_key = None
        self.inserted = False
        self.updated = False

    def inspect_primary_key(self):
        keys = [column.name for column in self.table.columns.values() if column.primary_key]
        if len(keys) == 1:
            return keys[0]
        else:
            raise ValueError("Expected one primary key, found {}".format(len(keys)))

    def insert(self, data_to_insert):
        if not self.inserted:
            try:
                statement = self.table.insert().values(**data_to_insert)
                result = self.cm.conn.execute(statement)
                self.primary_key = result.inserted_primary_key[0]
                self.inserted = True
            except:
                raise
        else:
            raise("Cannot perform insert - record already inserted.")

    def update(self, date_to_update):
        try:
            key_column = getattr(self.table.c, self.primary_key_name)
            statement = self.table.update()\
                                    .where(key_column==self.primary_key)\
                                    .values(**date_to_update)
            self.cm.conn.execute(statement)
            self.updated = True
        except:
            raise

class ChildRecord(RelatedRecord):
    """
    A ChildRecord is the child of a RelatedRecord. Functionality is similar
    except that ChildRecord is related to the parent through a foreign key.
    If foreign key name is not provided, an attempt is made to inspect the
    reflected table.
    """
    def __init__(self, connection_manager, table, parent, foreign_key_name=None):
        super().__init__(connection_manager, table)
        self.parent = parent
        if foreign_key_name:
            self.foreign_key_name = foreign_key_name
        else:
            self.foreign_key_name = self.inspect_foreign_key()
        self.foreign_key = parent.primary_key

    def inspect_foreign_key(self):
        """
        Examines table to determine name of foreign key to parent table; validates
        name match between identified key and primary key of parent table.
        """
        parent_key = "{}.{}".format(self.parent.table.name, self.parent.primary_key_name)
        fk_cols = [column for column in self.table.columns.values() if column.foreign_keys]
        found_keys = []
        for col in fk_cols:
            found = False
            for fk in col.foreign_keys:
                if str(fk.column) == parent_key:
                    found = True
            if found:
                found_keys.append(col.name)
        if len(found_keys) == 1:
            return found_keys[0]
        else:
            raise ValueError("Expected one foreign key, found {}".format(len(found_keys)))

    def insert(self, data_to_insert):
        "Add fk key/value to dict and insert record."
        data_to_insert[self.foreign_key_name] = self.foreign_key
        super().insert(data_to_insert)

if __name__ == '__main__':
    pass
