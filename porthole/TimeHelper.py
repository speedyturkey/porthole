"""
Created on 03/23/2017.

Contains various helper functions related to time. By default,
dates and timestamps are returned as formatted strings. Just pass
string=False to change this behavior.

Sample Usage:

>>> from helpers import TimeHelper
>>> TimeHelper.current_timestamp()
'2017-03-23 22:50:31'
>>> TimeHelper.today()
'2017-03-23'
>>> TimeHelper.yesterday()
'2017-03-22'
>>> TimeHelper.today(string=False)
datetime.date(2017, 3, 23)

"""

from datetime import datetime, timedelta


def current_timestamp(string=True):
    timestamp = datetime.utcnow()
    if string:
        return timestamp_to_string(timestamp)
    else:
        return timestamp

def now(string=True):
    return current_timestamp(string)

def today(string=True):
    date = datetime.utcnow().date()
    if string:
        return date_to_string(date)
    else:
        return date

def yesterday(string=True):
    date = today(False) - timedelta(days=1)
    if string:
        return date_to_string(date)
    else:
        return date

def timestamp_to_string(timestamp):
    return timestamp.strftime('%Y-%m-%d %-H:%M:%S')

def date_to_string(date):
    return date.strftime('%Y-%m-%d')


if __name__ == '__main__':
    pass
