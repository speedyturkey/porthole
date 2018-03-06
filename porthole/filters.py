from .queries import QueryResult


class ResultFilter(object):
    """
    Used for splitting a QueryResult on a specified attribute into sub-results.
    Subsets of the provided QueryResultw ill be created for each distinct value
    of the specified field.
    ResultFilter objects are iterables which iterate through the filtered_results
    attribute.

    Keyword arguments
    :result_to_filter: (QueryResult) The object to be split.
    :filter_by: (str) The field name on which to split.

    """
    def __init__(self, result_to_filter, filter_by):
        self.result_to_filter = result_to_filter
        self.headers = result_to_filter.field_names
        self.data = result_to_filter.result_data
        self.filter_by = filter_by
        self.keys = []
        self.filtered_data = {}
        self.filtered_results = {}
        self.filter_by = filter_by
        if filter_by not in self.headers:
            raise ValueError("Provided headers must contain filter_by value.")

    def filter(self):
        for row in self.data:
            key = row[self.filter_by]
            if key not in self.keys:
                self.keys.append(key)
                self.filtered_data[key] = []
            self.filtered_data[key].append(row)
        for key in self.keys:
            self.filtered_results[key] = QueryResult(
                field_names=self.headers,
                result_data=self.filtered_data[key]
                )

    def __iter__(self):
        self.pos = 0
        self.end = len(self.keys) - 1
        return self

    def __next__(self):
        if self.pos <= self.end:
            self.pos += 1
            key = self.keys[self.pos - 1]
            return key, self.filtered_results[key]
        else:
            raise StopIteration
