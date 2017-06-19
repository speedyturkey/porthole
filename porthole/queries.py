import os, re, sys, json
from decimal import Decimal
from datetime import date
from .app import config
from .connection_manager import ConnectionManager


class QueryResult(object):
    "Represent result data from an executed query. Includes capability to write results as json."

    def __init__(self, result_count=None, field_names=None, result_data=None):
        self.result_count = result_count
        self.field_names = field_names
        self.result_data = result_data

    def json_converter(self, obj):
        "Required to convert datatypes not otherwise json serializable."
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, date):
            return obj.isoformat()
        else:
            raise TypeError("Cannot convert provided type {}".format(type(obj)))

    def as_dict(self):
        "Returns contents as list of dictionaries with headers as keys."
        if self.field_names and self.result_data:
            return [dict(zip(self.field_names, row)) for row in self.result_data]
        else:
            raise ValueError("Both field_names and result_data attributes are required to convert query results to dictionary.")

    def write_to_json(self, filename):
        contents = self.as_dict()
        with open(filename, 'w') as f:
            json.dump(contents, f, default=self.json_converter)


class QueryGenerator(object):
    "Execute SQL query and return results"
    def __init__(self, cm, filename=None, params=None, sql=None):
        self.cm = cm
        self.filename = filename
        self.params = params
        self.sql = sql

    def construct_query(self):
        # Resolve full SQL statement.
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
            result_data = result_proxy.fetchall()
        except:
            print(sys.exc_info())
            raise RuntimeError("Unable to execute query.")

        query_results = QueryResult(result_count=len(result_data),
                                    field_names=result_proxy.keys(),
                                    result_data=result_data)
        return query_results


class QueryReader(object):
    """
    QueryReader is used to read, and optionally to parameterize, .sql files.

    Saved queries requiring paremeters at runtime should use placeholders in the format
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
        self.raw_pattern = '(#{[a-z]*})'
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
        "Reads and stores query contents"
        file_path = os.path.join(self.query_path, self.filename + '.sql')
        with open(file_path, 'r') as f:
            self.raw_sql = f.read()
            self.sql = self.raw_sql

    def find_values_to_replace(self):
        "Use pattern to identify all parameters in raw sql which need to be replaced."
        regexp = re.compile(self.raw_pattern)
        self.to_replace = regexp.findall(self.raw_sql)

    def replace_params(self):
        "For every param, find and replace placeholder with appropriate value."
        raw_sql = self.raw_sql
        for placeholder in self.to_replace:
            newreg = re.compile(placeholder)
            repl = self.get_replacement_value(placeholder)
            if repl:
                raw_sql = newreg.sub(str(repl), raw_sql)
        self.sql = raw_sql

    def get_replacement_value(self, to_be_replaced):
        "Given placeholder to be replaced, get name of parameter from within the pattern and lookup parameter value."
        name_reg = re.compile('[a-z]+')
        param_name = name_reg.search(to_be_replaced).group()
        return self.params.get(param_name)

    def validate(self):
        "Check whether any placeholders have not been provided a replacement value."
        regexp = re.compile(self.raw_pattern)
        missing = regexp.findall(self.sql)
        if missing:
            raise NameError("Value not provided for placeholder {}".format(missing))


if __name__ == '__main__':
    pass
