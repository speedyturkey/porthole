"""
Created on 03/23/2017.

Contains various helper functions related to time. By default,
dates and timestamps are returned as formatted strings. Just pass
string=False to change this behavior.

Sample Usage:

>>> import TimeHelper
>>> TimeHelper.current_timestamp()
'2017-03-23 22:50:31'
>>> TimeHelper.today()
'2017-03-23'
>>> TimeHelper.today(string=False)
datetime.date(2017, 3, 23)

"""

import datetime
import pytz


def current_timestamp(string: bool = True, timezone: str = 'UTC'):
    timestamp = datetime.datetime.now(tz=pytz.utc)
    if timezone != 'UTC':
        timestamp = convert_tz(timestamp, convert_to=timezone)
    if string:
        return timestamp_to_string(timestamp)
    else:
        return timestamp


def now(string: bool = True, timezone: str = 'UTC'):
    return current_timestamp(string, timezone)


def today(string: bool = True, timezone: str = 'UTC'):
    date = current_timestamp(string=False, timezone=timezone).date()
    if string:
        return date_to_string(date)
    else:
        return date


def timestamp_to_string(timestamp: datetime.datetime):
    return timestamp.strftime('%Y-%m-%d %-H:%M:%S')


def date_to_string(date: datetime.date):
    return date.strftime('%Y-%m-%d')


def convert_tz(timestamp: datetime.datetime, convert_to: str = 'US/Eastern'):
    return timestamp.astimezone(pytz.timezone(convert_to))


if __name__ == '__main__':
    pass
