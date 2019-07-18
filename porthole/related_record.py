from sqlalchemy import Table, MetaData


class RelatedRecord(object):
    """
    Represents a database record; provides insert/update functionality of
    of individual records.
    """
    def __init__(self, connection_manager, table):
        self.cm = connection_manager
        self.table = Table(
            table,
            MetaData(schema=connection_manager.schema),
            autoload=True,
            autoload_with=connection_manager.engine
        )
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
            raise RuntimeError("Cannot perform insert - record already inserted.")

    def update(self, date_to_update):
        try:
            key_column = getattr(self.table.c, self.primary_key_name)
            statement = self.table.update().where(
                key_column == self.primary_key
            ).values(**date_to_update)
            self.cm.conn.execute(statement)
            self.updated = True
        except:
            raise


if __name__ == '__main__':
    pass
