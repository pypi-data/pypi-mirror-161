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
import json
import math
import re
import unidecode
import uuid

import dateutil
import dateutil.parser

from majormode.perseus.constant import regex
from majormode.perseus.model import obj
from majormode.perseus.model.enum import Enum
from majormode.perseus.model.locale import Locale
from majormode.perseus.utils.date_util import ISO8601DateTime


TimestampRoundingMethod = Enum(
    'ceiling',
    'floor'
)


REGEX_IPV4 = None  # Lazy evaluation.
REGEX_MAC_ADDRESS = None  # Lazy evaluation.


def is_integer(value):
    """
    Indicate whether the specified string represents am integer value.


    :param: a supposed string representation of an integer value.


    :return: `True` if the specified string represents an integer value;
        `False` otherwise.
    """
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_numeric(value):
    """
    Indicate whether the specified string represents a numeric value.


    :param: a supposed string representation of a numeric value.


    :return: `True` if the specified string represents a numeric value;
        `False` otherwise.
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_undefined(value):
    """
    Indicate whether the specified value is undefined or not.

    A string is undefined if it is null or if it does not contain any data.


    :param value: a value.


    :return: `True` if the value is undefined, `False` otherwise.
    """
    return value is None or (isinstance(value, str) and len(value.strip()) == 0)


def is_uuid(value):
    """
    Indicate if the specified string represents a Universally Unique
    Identifier (UUID).


    :param value: a supposed string representation of a Universally Unique
        Identifier (UUID) .


    :return: `True` if the specified string represents a UUID; `False`
        otherwise.
    """
    try:
        return uuid.UUID(value) is not None
    except ValueError:
        return False


def json_to_object(value):
    """
    Return an instance `Object` from a JSON object.


    :param value: a JSON object, i.e., a dictionary.


    :return: an instance `Object`.
    """
    return obj.Object.from_json(value)


def json_to_string(value, null_string_repr='{}', trimmable=False):
    """
    Return a string representation of the specified JSON object.


    :param value: a JSON object.

    :param null_string_repr: the string representation of the null
        object.

    :param trimmable: `True` to strip out attributes with a null value.


    :return: a string representation of the specified JSON object.
    """
    return null_string_repr if is_undefined(value) \
        else json.dumps(obj.stringify(value, trimmable=trimmable))


def macaddr_to_string(value, strict=False):
    """
    Return the string representation of a MAC address.


    :param value: A MAC address represented with a tuple of hexadecimals.

    :param strict: Indicate whether the argument `value` can be null.


    :return: The string representation of the MAC address, or `None` if
        the argument is `null`


    :raise ValueError: If the argument `value` is null while the argument
        `strict` equals `False`, or if the argument `value` is not a list
        or a tuple, or if each item of the argument `value` is not 2
        characters.
    """
    if not value:
        if strict:
            raise ValueError("The argument `value` cannot be null")
        return None

    if not isinstance(value, (list, tuple)):
        raise ValueError("The argument `value` must be a list or a tuple")

    if any([
        not isinstance(e, str) or len(e) != 2
        for e in value
    ]):
        raise ValueError("All the elements of `value` must be a string of 2 characters")

    mac_address = ':'.join(value)
    return mac_address


def string_to_boolean(value, strict=False, default_value=False):
    """
    Return a boolean with a value represented by the specified string.


    :param value: a string representation of a boolean.

    :param strict: indicate whether the specified string MUST be of a
        valid boolean representation.

    :param default_value: default boolean value to return is the given
        value is not defined


    :return: the boolean value represented by the string.


    :raise ValueError: if the string doesn't represent a valid boolean,
        while the argument `strict` equals `True`.
    """
    if is_undefined(value) and default_value is not None:
        return default_value

    if isinstance(value, bool):
        return value

    if isinstance(value, str) and value is not None:
        value = value.lower()

    is_true = value in ('yes', 'true', 't', '1')

    if not is_true and strict and value not in ('no', 'false', 'f', '0'):
        raise ValueError("The specified string doesn't represent a boolean value")

    return is_true


def string_to_date(value):
    """
    Return a Python date that corresponds to the specified string
    representation.


    :param value: string representation of a date.


    :return: an instance `datetime.datetime` represented by the string.


    :raise OverflowError: Raised if the parsed date exceeds the largest
        valid C integer on your system.

    :raise ValueError: Raised for invalid or unknown string format, if the
        provided `tzinfo` is not in a valid format, or if an invalid date
        would be created.
    """
    return value if isinstance(value, datetime.date) else dateutil.parser.parse(value).date()


def string_to_decimal(value, strict=True):
    """
    Return a decimal corresponding to the string representation of a
    number.


    :param value: a string representation of an decimal number.

    :param strict:  indicate whether the specified string MUST be of a
        valid decimal number representation.


    :return: the decimal value represented by the string.


    :raise ValueError: if the string doesn't represent a valid decimal,
        while the argument `strict` equals `True`.
    """
    if is_undefined(value):
        if strict:
            raise ValueError("The value cannot be null")
        return None

    try:
        return float(value)

    except ValueError:
        raise ValueError(f'The specified string "{value}" does not represent an integer')


def string_to_enum(value, enumeration, strict=False, default_value=None):
    """
    Return the item of an enumeration that corresponds to the specified
    string representation.


    :param value: string representation of an item of a Python
        enumeration.

    :param enumeration: a Python enumeration.

    :param strict: indicate whether the value must correspond to an
        item of the specified Python enumeration or if `None` value is
        accepted.

    :param default_value: default value to return if the value is null.


    :return: the item of the Python enumeration the specified string
        representation corresponds to.


    :raise ValueError: if the enumeration is not an instance of `Enum`, or
        if the string representation doesn't correspond to any item of the
        given Python enumeration, or if the default value is not an item
        of the given Python enumeration.
    """
    if not isinstance(enumeration, Enum):
        raise ValueError("The specified enumeration is not an instance of Enum")

    # @patch: it happens that developer already provide an item of the
    #     enumeration instead of a string...
    if not isinstance(value, str):
        if value in enumeration:
            return value

    if is_undefined(value):
        if strict:
            raise ValueError("The value cannot be null")

        if default_value is not None and default_value not in enumeration:
            raise ValueError(
                f'The default value {default_value} must be an item of the enumeration')

        return default_value

    item = [item for item in enumeration if str(item) == value]
    if len(item) == 0:
        raise ValueError(
            f'The specified string "{value}" does not represent any item of the enumeration')

    return item[0]


def string_to_integer(value, strict=False):
    """
    Return an integer corresponding to the string representation of a
    number.


    :param value: a string representation of an integer number.

    :param strict:  indicate whether the specified string MUST be of a
        valid integer number representation.


    :return: the integer value represented by the string.


    :raise ValueError: if the string doesn't represent a valid integer,
        while the argument `strict` equals `True`.
    """
    if is_undefined(value):
        if strict:
            raise ValueError('The value cannot be null')
        return None

    try:
        return int(value)

    except ValueError:
        raise ValueError(f'The specified string "{value}" does not represent an integer')


def string_to_ipv4(value, strict=False):
    """
    Return a tuple corresponding to the string representation of an IPv4
    address.

    An IPv4 address is canonically represented in dot-decimal notation,
    which consists of four decimal numbers, each ranging from 0 to 255,
    separated by dots, e.g., `172.16.254.1`.


    :param value: a dotted-decimal notation of an IPv4 address, consisting
        of four decimal numbers, each ranging from `0` to `255`,
        separated by dots.

    :param strict: indicate whether the `None` value is accepted.


    :return: a tuple of four decimal numbers `(byte1, byte2, byte3, byte4)`,
        each ranging from `0` to `255`.
    """
    if is_undefined(value):
        if strict:
            raise ValueError('The value cannot be null')
        return None

    global REGEX_IPV4
    if REGEX_IPV4 is None:
        REGEX_IPV4 = re.compile(regex.REGEX_PATTERN_IPV4)

    if not REGEX_IPV4.match(value):
        raise ValueError(f'The specified string "{value}" does not represent a IPv4')

    ipv4 = [int(byte) for byte in value.split('.') if int(byte) < 256]

    if len(ipv4) != 4:
        raise ValueError('The IPv4 "%s" has invalid byte(s)' % value)

    return ipv4


def string_to_json(value):
    """
    Return a JSON object represented by the specified string.

    :param value: a string representation of a json expression.

    :return: the json object represented by the string.
    """
    return None if is_undefined(value) else json.loads(value)


def string_to_locale(value, strict=True):
    """
    Return an instance `Locale` corresponding to the string
    representation of a locale.

    :param value: a string representation of a locale, i.e., a ISO 639-3
        alpha-3 code (or alpha-2 code), optionally followed by a dash
        character `-` and a ISO 3166-1 alpha-2 code.

    :param strict: indicate whether the string representation of a locale
        has to be strictly compliant with RFC 4646, or whether a Java-
        style locale (character `_` instead of `-`) is accepted.

    :return: an instance `Locale`.
    """
    try:
        return None if is_undefined(value) else Locale.from_string(value, strict=strict)
    except Locale.MalformedLocaleException as exception:
        if strict:
            raise exception


def string_to_macaddr(value, strict=False):
    """
    Return a tuple corresponding to the string representation of a Media
    Access Control address (MAC address) of a device, which is a unique
    identifier assigned to a network interface controller (NIC) for
    communications at the data link layer of a network segment.

    The standard (IEEE 802) format for printing EUI-48 addresses in human-
    friendly form is six groups of two hexadecimal digits, separated by
    hyphens (-) in transmission order (e.g. `01-23-45-67-89-AB`).  This
    form is also commonly used for EUI-64 (e.g. `01-23-45-67-89-AB-CD-EF`).
    Other conventions include six groups of two hexadecimal digits
    separated by colons (:) (e.g. 01:23:45:67:89:AB), and three groups of
    four hexadecimal digits separated by dots (.) (e.g. `0123.4567.89AB`);
    again in transmission order.


    :param value: a string representation of a MAC address.

    :param strict: indicate whether the `None` value is accepted.


    :return: a tuple of 6 hexadecimal strings `(hex1, hex2, hex3, hex4, hex5, hex6)`,
        each ranging from `0x00` to `0xFF`.
    """
    if is_undefined(value):
        if strict:
            raise ValueError('The value cannot be null')
        return None

    global REGEX_MAC_ADDRESS
    if REGEX_MAC_ADDRESS is None:
        REGEX_MAC_ADDRESS = re.compile(regex.REGEX_PATTERN_MAC_ADDRESS)

    match = REGEX_MAC_ADDRESS.match(value.lower())
    if match is None:
        raise ValueError(f'The specified string "{value}" does not represent a MAC address')

    return match.groups()


def string_to_natural_number(value, strict=False):
    """
    Return an integer corresponding to the string representation of a
    natural number (a.k.a. a positive integer).


    :param value: a string representation of an integer number.

    :param strict:  indicate whether the specified string MUST be of a
        valid natural number representation.


    :return: the integer value represented by the string.


    :raise ValueError: if the string doesn't represent a valid natural,
        number while the argument `strict` equals `True`.
    """
    if is_undefined(value):
        if strict:
            raise ValueError('The value cannot be null')
        return None

    try:
        natural_number = int(value)
    except ValueError:
        raise ValueError(f'The specified string "{value}" does not represent a natural number')

    if natural_number < 0:
        raise ValueError('The value cannot be negative')

    return natural_number


def string_to_object(value):
    """
    Return an instance `Object` from the string representation of a JSON
    expression.

    :param value: a string representation of a JSON expression.

    :return: an instance `Object`.
    """
    return obj.objectify(value)


def string_to_time(value):
    """
    Return an instance `datetime.time` that corresponds to the specified
    string representation.


    :param value: a string representation of a time `HH:MM[:SS]`, where:

        * `HH`: hour (24-hour clock) as a zero-padded decimal number.

        * `MM`: minute as a zero-padded decimal number.

        * `SS`: second as a zero-padded decimal number.


    :return: an instance `datetime.time` represented by the string.


    :raise ValueError: if the string representation doesn't correspond to
        a valid time.
    """

    if not value:
        return None
    try:
        return datetime.datetime.strptime(value, '%H:%M:%S').time()
    except ValueError:
        return datetime.datetime.strptime(value, '%H:%M').time()


def string_to_timestamp(
        value,
        second_digits=3,
        default_utc_offset=None,
        rounding_method=TimestampRoundingMethod.ceiling):
    """
    Return the ISO 8601 date time that corresponds to the specified string
    representation.

    When the required precision is lower than microsecond, the function
    rounds the sub-second time to the specified number of digits.

    By default, when possible, it returns the smallest value greater than
    or equal to the sub-second time for specified precision, also know as
    "ceiling conversion"; for instance, the function converts `918845`
    microseconds to `919` milliseconds.  Otherwise, the function return
    the largest value equal to the sub-second time for specified
    precision, also known as "floor conversion"; for instance, the
    function converts `999916` microseconds to `999` milliseconds.


    :param value: string representation of an ISO date time.

    :param second_digits: indicate the number of second digits after the
        decimal point, to determine the time precision.  For instance, 3
        digits corresponds to milliseconds, 6 digits corresponds to
        microseconds.

    :param default_utc_offset: if the specified string representation
        doesn't mention any time zone, use this offset as the time zone
        of the corresponding ISO 8601 date time, or use the time zone
        of the machine this code is running on as the default time zone.

    :param rounding_method: one of the rounding method, as declared in
        `TimestampRoundingMethod`, when the required precision is lower
        than microsecond.


    :return: an instance `ISO8601DateTime` represented by the string.


    :raise ValueError: if the specified number of second digits after the
        decimal point is not in 0..6, or if the string representation
        doesn't correspond to a valid ISO 8601 date time.
    """
    if second_digits < 0 or second_digits > 6:
        raise ValueError("The number of second digits after the decimal point must be in 0..6")

    if not value:
        return None

    if isinstance(value, datetime.date):
        pydatetime = ISO8601DateTime.from_datetime(value)

    else:
        if default_utc_offset is not None:
            value = '%s%s%02d'.format(value[:19], '-' if default_utc_offset < 0 else '+', default_utc_offset)

        d = dateutil.parser.parse(value)

        if second_digits >= 6:
            microsecond = d.microsecond
        else:
            f = 10 ** (6 - second_digits)
            if rounding_method == TimestampRoundingMethod.ceiling:
                m = int(math.ceil(float(d.microsecond) / f))
                if m >= f:
                    m -= 1
            else:
                m = int(math.floor(float(d.microsecond) / f))

            microsecond = m * f

        pydatetime = ISO8601DateTime(
            d.year, d.month, d.day,
            d.hour, d.minute, d.second, microsecond,
            d.tzinfo or dateutil.tz.tzlocal())

    pydatetime.set_second_digits(second_digits)

    return pydatetime


def string_to_uuid(value, strict=True):
    """
    Return a Universally Unique Identifier (UUID) object represented by
    the specified string.


    :param value: a string representation of a UUID.

    :param strict: indicate whether the specified string MUST be of a
        valid UUID representation.


    :return: a UUID object.
    """
    try:
        return None if is_undefined(value) else uuid.UUID(value)
    except ValueError as error:
        if strict:
            raise error
