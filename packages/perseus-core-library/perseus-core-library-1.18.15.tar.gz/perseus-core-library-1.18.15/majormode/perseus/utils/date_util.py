# Copyright (C) 2019 Majormode.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import datetime
import dateutil
import dateutil.tz
import pytz


class ISO8601TimeZoneInfo(datetime.tzinfo):
    def __init__(self, utc_offset=0):
        self.utc_offset = utc_offset
        self.time_delta = datetime.timedelta(hours=utc_offset)
        self.time_delta_hours = datetime.timedelta(hours=utc_offset)

    def utcoffset(self, dt):
        return self.time_delta

    def tzname(self, dt):
        return '%s%02d:00' % ('+' if self.utc_offset >= 0 else '-', self.utc_offset)

    def dst(self, dt):
        return self.time_delta_hours


class ISO8601DateTime(datetime.datetime):
    REVISION_FIELD_OFFSETS = [(0, 4), (5, 7), (8, 10), (11, 13), (14, 16), (17, 19)]

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self._second_digits = 3
        return self

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self._second_digits = 3

    def __eq__(self, other):
        return self.date() == other if type(other) == datetime.date \
            else super().__eq__(other)

    def __lt__(self, other):
        return self.date() < other if type(other) == datetime.date \
            else super().__lt__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return not (self.__lt__(other) or self.__eq__(other))

    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)

    def __repr__(self):
        value = self.isoformat(sep='T')
        timezone_sign = self._get_timezone_sign(value)

        if value.find('.') == -1:
            offset = value.rfind(timezone_sign)
            if offset >= 0:
                value = f'{value[:offset]}.000{value[offset:]}'

        if self._second_digits < 6:
            value = value[:value.find('.') + self._second_digits + 1] + value[value.rfind(timezone_sign):]

        return value

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def _get_timezone_sign(value):
        offset = value.rfind('+')
        return '+' if offset > 0 else '-'

    @property
    def revision(self):
        time_str = str(self)
        return ''.join([time_str[start:end] for (start, end) in ISO8601DateTime.REVISION_FIELD_OFFSETS ])

    @staticmethod
    def from_datetime(pydatetime, utc_offset=None):
        if type(pydatetime) == datetime.date:  # datetime.date doesn't have attributes "hour", "minute", etc.
            pydatetime = datetime.datetime.combine(pydatetime, datetime.datetime.min.time())

        return ISO8601DateTime(
            pydatetime.year, pydatetime.month, pydatetime.day,
            pydatetime.hour, pydatetime.minute, pydatetime.second, pydatetime.microsecond,
            pydatetime.tzinfo or (ISO8601TimeZoneInfo(utc_offset)
                                  if utc_offset is not None else dateutil.tz.tzlocal()))

    @staticmethod
    def from_milliseconds(milliseconds):
        return ISO8601DateTime.from_datetime(
            datetime.datetime.utcfromtimestamp(milliseconds // 1000).replace(
                microsecond=milliseconds % 1000 * 1000),
            utc_offset=0)

    @staticmethod
    def from_seconds(seconds):
        return ISO8601DateTime.from_datetime(
            datetime.datetime.utcfromtimestamp(seconds),
            utc_offset=0)

    @classmethod
    def now(cls, tz=None):
        return cls.from_datetime(datetime.datetime.utcnow().replace(tzinfo=pytz.utc))

    def set_second_digits(self, second_digits):
        """
        Set the number of second digits after the decimal point, to
        determine the time precision.


        :param second_digits: indicate the number of second digits after the
            decimal point, to determine the time precision.  For instance, 3
            digits corresponds to milliseconds, 6 digits corresponds to
            microseconds.


        :return: this instance.
        """
        self._second_digits = second_digits


def get_first_day_from_week(year, week_number, utc_offset=None):
    pydatetime = datetime.datetime.strptime('%04d-%02d-1' % (year, week_number), '%Y-%W-%w')

    if datetime.date(year, 1, 4).isoweekday() > 4:
        pydatetime -= datetime.timedelta(days=7)

    return ISO8601DateTime.from_datetime(pydatetime, utc_offset=utc_offset)

