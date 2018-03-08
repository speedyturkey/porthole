import pymysql
from sqlalchemy import create_engine
from .app import config


class ConnectionManager():
    def __init__(self, db=None):
        self.db = db
        self.config = config
        self.engine = None
        self.conn = None
        if db:
            self.unpack_params()

    def unpack_params(self):
        self.rdbms = self.config[self.db].get('rdbms')
        self.db_host = self.config[self.db].get('host')
        self.db_port = int(self.config[self.db].get('port', 0))
        self.db_user = self.config[self.db].get('user')
        self.db_password = self.config[self.db].get('password')
        self.database = self.config[self.db].get('database')
        self.schema = self.config[self.db].get('schema')

    def connect(self):
        if not self.db:
            raise ValueError("Cannot connect - db attribute not set.")
        try:
            self.engine = self.create_engine()
            self.conn = self.engine.connect()
        except ValueError:
            raise
        except:
            raise RuntimeError("Unable to connect to database {}".format(self.db))

    def create_engine(self):
        if self.rdbms == 'sqlite':
            return create_engine('sqlite:///{db_host}'.format(**self.__dict__))
        elif self.rdbms == 'mysql':
            return create_engine('mysql+pymysql://{db_user}:{db_password}@{db_host}'.format(**self.__dict__))
        elif self.rdbms == 'postgresql':
            return create_engine('postgresql://{db_user}:{db_password}@{db_host}/{database}'.format(**self.__dict__))
        else:
            raise ValueError("Unsupported RDBMS: {}".format(self.rdbms))

    def close(self):
        self.conn.close()
        self.engine.dispose()

    def closed(self):
        if self.conn:
            return self.conn.closed
        else:
            return None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()


class ConnectionPool(object):

    def __init__(self, dbs=[]):
        self.pool = {}
        for db in dbs:
            self.add_connection(db)

    def connections(self):
        return self.pool.keys()

    def add_connection(self, db):
        if db not in self.connections():
            cm = ConnectionManager(db)
            cm.connect()
            self.pool[db] = cm
        return self.get(db)

    def get(self, db):
        return self.pool.get(db)

    def close(self, db):
        self.pool[db].close()

    def close_all(self):
        for conn in self.connections():
            self.close(conn)


if __name__ == '__main__':
    pass
