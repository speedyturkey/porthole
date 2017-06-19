#!/usr/bin/env python
# encoding: utf-8
"""
ResultContainers.py
Created by William McMonagle on 11/29/16.
"""

from datetime import date

class ResultRecord():
    """Represents a row in the result set of a database query. The name of each attribute is the
    column header in the query, and the value is the field value. Provides the ability to
    reference a row by attribute name rather than by an index value within a list (row).
    """
    def __init__(self, row, headers):
        for i, elem in enumerate(row):
            setattr(self, headers[i], elem)

class ResultsDictionary(list):
    def __init__(self, data, headers):
        for record in data:
            for i, elem in enumerate(record):
                # Date objects are not json serializable,
                # so we convert them to strings using isoformat.
                if isinstance(elem, date):
                    record[i] = elem.isoformat()
            self.append(dict(zip(headers, record)))

class ResultsList(list):
    """Inherits from the list built-in, and is a collection of ResultRecord objects."""
    def __init__(self, data, headers):
        for record in data:
            self.append(ResultRecord(record, headers))

    def to_dict(self):
        for record in self:
            for k, v in record.__dict__.items():
                record[k] = v
        for k, v in record.items():
            print(k, v)

def example():
    headers = ['field1', 'field2', 'field3']

    l1 = ['a', 'b', 'c']
    l2 = ['d', 'e', 'f']
    l3 = ['g', 'h', 'i']

    data = [l1, l2, l3]

    rs = ResultSet(data, headers)

    # for item in rs:
    #     for field in headers:
    #         print(getattr(item, field))

    rd = ResultsDictionary(data, headers)
    for d in rd:
        print(type(d))
        for k, v in d.items():
            print(k,v)


if __name__ == '__main__':
    example()
