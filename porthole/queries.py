import os, re, json
from collections import OrderedDict
from decimal import Decimal
from datetime import date
from .app import config
from .connections import ConnectionManager
from .logger import PortholeLogger

logger = PortholeLogger(name=__name__)

RE_SQL_STATEMENT = re.compile(''';(?=(?:[^"'`]*["'`][^"'`]*["'`])*[^"'`]*$)''')


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
            if len(fields) > len(set(fields)):
                raise ValueError("Field names must be unique, but your result set contains non-unique field names.")
            data = OrderedDict(zip(fields, values))
        else:
            data = data or OrderedDict()
        super().__init__(data)

    def __iter__(self):
        return iter(self.values())

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self.items()))


class QueryGenerator(object):
    """Execute SQL query and return results"""
    def __init__(self, cm, filepath=None, filename=None, params=None, sql=None, multiple_statements=False):
        if filename is not None and sql is not None:
            raise TypeError("Cannot give both 'filename' and 'sql' arguments")
        self.cm = cm
        self.filepath = filepath
        self.filename = filename
        self.params = params
        self.raw_sql = sql
        self.sql = None
        self.multiple_statements = multiple_statements

    def construct_query(self):
        """Read and parameterize (if necessary) a .sql file for execution."""
        reader = QueryReader(filepath=self.filepath, filename=self.filename, raw_sql=self.raw_sql, params=self.params)
        return reader.sql

    def execute(self):
        """
        This method will execute a series of statements, if that is what has been provided.
        The first returnable set of data will be returned - if the statements provided
        include multiple selects, results from only the first will be returned.
        Future implementations may allow for a sequence of results to be returned.
        """
        if self.sql is None:
            self.sql = self.construct_query()
        # Only SQL strings can be split, not (e.g.) SQLAlchemy statements.
        if self.multiple_statements and isinstance(self.sql, str):
            statements = self._split_sql()
        else:
            statements = [self.sql]
        single_statement = True if len(statements) == 1 and self.filename else False
        try:
            for statement in statements:
                result_proxy = self.cm.conn.execute(statement)
                log_string = self.filename if single_statement else str(statement)[:25]
                logger.info("Executed {} against {}".format(log_string, self.cm.db))
            if result_proxy.cursor:
                return self.fetch_results(result_proxy)
        except Exception as e:
            logger.exception(e)
            raise

    def _split_sql(self):
        """
        Returns a list containing individual sql statements as strings to be executed.
        """
        return [stmt.strip() for stmt in RE_SQL_STATEMENT.split(self.sql) if stmt.strip()]

    @staticmethod
    def fetch_results(result_proxy):
        field_names = result_proxy.keys()
        row_proxies = result_proxy.fetchall()
        result_data = [row.values() for row in row_proxies]
        query_results = QueryResult(result_count=len(result_data),
                                    field_names=field_names,
                                    result_data=result_data,
                                    row_proxies=row_proxies)
        return query_results


class QueryReader(object):
    """
    QueryReader is used to read, and optionally to parameterize, .sql files.

    By default, it is assumed that your query lives in your project's default
    query path. Override this behavior by providing a value for the `filepath`
    parameter.

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
    def __init__(self, filepath=None, filename=None, raw_sql=None, params=None):
        self.filename = filename
        self.params = params
        self.raw_sql = raw_sql
        self.sql = None
        self.to_replace = None
        self.query_path = filepath or config['Default']['query_path']
        self.raw_pattern = '(#{[a-zA-Z_]*})'
        self.process_sql()

    def __repr__(self):
        if self.sql:
            return self.sql
        elif self.raw_sql:
            return self.raw_sql
        else:
            return "< Empty QueryReader object >"

    def process_sql(self):
        if self.filename:
            self.read()
        if isinstance(self.raw_sql, str):
            self.find_values_to_replace()
        if self.to_replace:
            self.replace_params()
            self.validate()
        else:
            self.sql = self.raw_sql

    def read(self):
        """Reads and stores query contents"""
        file_path = os.path.join(self.query_path, self.filename + '.sql')
        with open(file_path, 'r') as f:
            self.raw_sql = f.read()

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
    QueryExecutor acts as a context manager for the execution of a one or more queries against the selected database.
    Keeps database connection open for duration of `with` block and closes afterwards.
    Usage:
    with QueryExecutor(db=MyDB) as qe:
        result = qe.execute_query(sql='select count(*) from my_table')
    """
    def __init__(self, db):
        self.db = db
        self.cm = None

    def create_database_connection(self):
        self.cm = ConnectionManager(db=self.db)
        self.cm.connect()

    def close_database_connection(self):
        self.cm.close()

    def execute_query(self, filepath=None, filename=None, params=None, sql=None, multiple_statements=False):
        query = QueryGenerator(
            cm=self.cm,
            filepath=filepath,
            filename=filename,
            params=params,
            sql=sql,
            multiple_statements=multiple_statements
        )
        return query.execute()

    def commit(self):
        self.cm.commit()

    def __enter__(self):
        self.create_database_connection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_database_connection()


if __name__ == '__main__':
    pass
