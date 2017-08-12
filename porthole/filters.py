"""
We want to be able to split up query results according to an arbitrary attribute in the result data.

Two approaches -
(1) Execute query multiple times, each time w a different value for a given parameter.
(2) Execute query once and split results.

(2) is probably more performant, given db and network costs.
"""

from random import randint, choice


class ResultFilter(object):
    def __init__(self, headers, data, filter_by):
        self.headers = headers
        self.data = data
        self.filter_by = filter_by
        self.filtered_data = {}
        try:
            self.filter_idx = headers.index(filter_by)
        except:
            raise ValueError("Provided headers must contain filter_by value.")

    def filter(self):
        self.keys = []
        for row in self.data:
            key = row[self.filter_idx]
            if key not in self.keys:
                self.keys.append(key)
                self.filtered_data[key] = []
            self.filtered_data[key].append(row)

    def __iter__(self):
        self.pos = 0
        self.end = len(self.keys) - 1
        return self

    def __next__(self):
        if self.pos <= self.end:
            self.pos += 1
            key = self.keys[self.pos - 1]
            return key, self.filtered_data[key]
        else:
            raise StopIteration
