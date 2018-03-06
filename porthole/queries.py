import os, re, json
from collections import OrderedDict
from decimal import Decimal
from datetime import date
from .app import config
from .connections import ConnectionManager
from .logger import PortholeLogger

logger = PortholeLogger(name=__name__)


class QueryResult(object):
    """Represent result data from an executed query. Includes capability to write results as json."""

    def __init__(self, result_count=None, field_names=None, result_data=None, row_proxies=None):
        self.result_count = result_count
        self.field_names = field_names
        self.result_data = [RowDict(fields=field_names, values=row) for row in result_data]
        self.row_proxies = row_proxies
        self.field_index = {field: idx for idx, field in enumerate(field_names)}

    @staticmethod
    def json_converter(obj):
        """Required to convert datatypes not otherwise json serializable."""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, date):
            return obj.isoformat()
        else:
            raise TypeError("Cannot convert provided type {}".format(type(obj)))

    def as_dict(self):
        raise DeprecationWarning("QueryResult.as_dict method is no longer available and will be removed.")

    def write_to_json(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.result_data, f, default=self.json_converter)

    def map_function_to_field(self, field, func):
        assert field in self.field_names
        for row in self.result_data:
            row[field] = func(row[field])

    def apply(self, func):
        for row in self.result_data:
            func(row)


class RowDict(OrderedDict):
    """
    RowDict is used to represent a record in a query result. Because RowDict inherits from
    OrderedDict, values are accessible using keys (field/header names). RowDict has special
    iteration behavior such that iterating over a RowDict instance will return values rather
    than keys.
    RowDict inherits from OrderedDict to preserve compatibility with Python < 3.6.
    """
    def __init__(self, data=None, fields=None, values=None):
        fields_and_values_provided = fields is not None and values is not None
        if fields_and_values_provided is True and data is None:
            data = OrderedDict(zip(fields, values))
        else:
            data = data or OrderedDict()
        super().__init__(data)

    def __iterkeys(self):
        """For reference, see cpython/Lib/collections/__init__.py"""
        # Traverse the linked list in order.
        root = self._OrderedDict__root
        curr = root.next
        while curr is not root:
            yield curr.key
            curr = curr.next

    def __itervalues(self):
        """For reference, see cpython/Lib/collections/__init__.py"""
        # Traverse the linked list in order.
        root = self._OrderedDict__root
        curr = root.next
        while curr is not root:
            yield self.__getitem__(curr.key)
            curr = curr.next

    def keys(self):
        return list(iter(self.__iterkeys()))

    def values(self):
        return list(iter(self.__itervalues()))

    def items(self):
        return zip(self.keys(), self.values())

    def __iter__(self):
        return self.__itervalues()

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self.items()))


class QueryGenerator(object):
    """Execute SQL query and return results"""
    def __init__(self, cm, filename=None, params=None, sql=None):
        self.cm = cm
        self.filename = filename
        self.params = params
        self.sql = sql

    def construct_query(self):
        "Read and parameterize (if necessary) a .sql file for execution."
        if self.filename:
            reader = QueryReader(filename=self.filename, params=self.params)
            self.sql = reader.sql
        else:
            raise Exception("Cannot construct query without providing the SQL filename.")

    def execute(self):

        if self.sql is None:
            self.construct_query()

        try:
            result_proxy = self.cm.conn.execute(self.sql)
            field_names = result_proxy.keys()
            row_proxies = result_proxy.fetchall()
            result_data = [row.values() for row in row_proxies]
            logger.info("Executed {} against {}".format(self.filename or str(self.sql)[:25], self.cm.db))
        except Exception as e:
            logger.exception(e)
            raise RuntimeError("Unable to execute query.")

        query_results = QueryResult(result_count=len(result_data),
                                    field_names=field_names,
                                    result_data=result_data,
                                    row_proxies=row_proxies)
        return query_results


class QueryReader(object):
    """
    QueryReader is used to read, and optionally to parameterize, .sql files.

    Saved queries requiring parameters at runtime should use placeholders in the format
    matching the raw_pattern attribute, which is by default:
        #{parameter_name} e.g. #{first_name}, #{last_name}, etc.

    Replacement values must be provided for all parameter placeholders.

    Simple Usage - No Parameters

    >> my_query = QueryReader(filename='my_query')
    >> my_query.sql
    select * from table;

    Usage with Parameters

    >> my_query = QueryReader(filename='my_query', params={'field': 'value'})
    >> my_query.sql
    select * from table where field = 'value';

    """
    def __init__(self, filename=None, params=None):
        self.filename = filename
        self.params = params
        self.raw_sql = None
        self.sql = None
        self.query_path = config['Default']['query_path']
        self.raw_pattern = '(#{[a-zA-Z_]*})'
        self.to_replace = None
        if filename:
            self.read()
            self.find_values_to_replace()
            if self.to_replace:
                self.replace_params()
            self.validate()

    def __repr__(self):
        if self.sql:
            return self.sql
        elif self.raw_sql:
            return self.raw_sql
        else:
            return "< QueryReader object >"

    def read(self):
        """Reads and stores query contents"""
        file_path = os.path.join(self.query_path, self.filename + '.sql')
        with open(file_path, 'r') as f:
            self.raw_sql = f.read()
            self.sql = self.raw_sql

    def find_values_to_replace(self):
        """Use pattern to identify all parameters in raw sql which need to be replaced."""
        regexp = re.compile(self.raw_pattern)
        self.to_replace = regexp.findall(self.raw_sql)

    def replace_params(self):
        """For every param, find and replace placeholder with appropriate value."""
        raw_sql = self.raw_sql
        for placeholder in self.to_replace:
            newreg = re.compile(placeholder)
            repl = self.get_replacement_value(placeholder)
            if repl:
                raw_sql = newreg.sub(str(repl), raw_sql)
        self.sql = raw_sql

    def get_replacement_value(self, to_be_replaced):
        """Given placeholder to be replaced, get name of parameter from w/in the pattern and lookup parameter value."""
        name_reg = re.compile('[a-zA-z_]+')
        param_name = name_reg.search(to_be_replaced).group()
        return self.params.get(param_name)

    def validate(self):
        """Check whether any placeholders have not been provided a replacement value."""
        regexp = re.compile(self.raw_pattern)
        missing = regexp.findall(self.sql)
        if missing:
            raise NameError("Value not provided for placeholder {}".format(missing))


class QueryExecutor(object):
    """
    QueryExecutor acts as a context manager for the execution of a given query against the selected database.
    Open database connection, execute query, and close the connection.
    Usage:
    with QueryExecutor(db=MyDB, sql='select count(*) from my_table') as qe:
        result = qe.execute_query()
    """
    def __init__(self, db, filename=None, params=None, sql=None):
        self.db = db
        self.cm = None
        self.filename = filename
        self.params = params
        self.sql = sql

    def create_database_connection(self):
        self.cm = ConnectionManager(db=self.db)
        self.cm.connect()

    def close_database_connection(self):
        self.cm.close()

    def execute_query(self):
        query = QueryGenerator(
            cm=self.cm,
            filename=self.filename,
            params=self.params,
            sql=self.sql
        )
        return query.execute()

    def __enter__(self):
        self.create_database_connection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_database_connection()


if __name__ == '__main__':
    pass
