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

import copy
import datetime
import inspect
import json
import uuid

from majormode.perseus.model.enum import EnumValue
from majormode.perseus.model.locale import Locale
from majormode.perseus.utils.date_util import ISO8601DateTime


def objectify(string_or_json):
    """
    Deserialize a string containing a JSON document to a Python object.


    @param string_or_json: A string representation of a JSON document or a
        JSON expression.


    @return: An instance `Object`.
    """
    return string_or_json and Object.from_json(
        json.loads(string_or_json) if isinstance(string_or_json, str) else string_or_json)


def stringify(obj, include_properties=True, trimmable=False):
    """
    Convert an object to a stringified version where the attribute values
    have been stringified whenever these attributes are not of Python
    primitive data types.

    This function differs from the standard Python `str` as the latter
    returns a string version of object, while this function returns an
    object which attributes have Python primitive data types.


    :param obj: An object to return its stringified version.

    :param include_properties: Indicate whether the properties of the
        specified object need to be included in the JSON expression.

    :param trimmable: `True` to strip out attributes with a null value.


    :return: A copy of the object passed to this function, where the value
        of each attribute has been stringified when not of a Python
        primitive data type.
    """
    if obj is None:
        return None

    if isinstance(obj, (str, bool, int, float, complex)):
        return obj

    if isinstance(obj, (list, set, tuple)):
        return [stringify(item, trimmable=trimmable) for item in obj]

    if isinstance(obj, dict):
        return dict([
            (str(key), stringify(value, trimmable=trimmable))
            for key, value in obj.items()
            if not trimmable or value is not None])

    if isinstance(obj, (uuid.UUID, EnumValue, ISO8601DateTime, Locale)):
        return str(obj)

    if isinstance(obj, datetime.datetime):
        return str(ISO8601DateTime.from_datetime(obj)) if obj.tzinfo else str(obj)

    if hasattr(obj, '__dict__'):
        attributes = dict()

        # Retrieve the list of properties and their respective value, when
        # required.
        if include_properties:
            properties = dict([
                (name, stringify(getattr(obj, name), include_properties=include_properties, trimmable=trimmable))
                for name, value in inspect.getmembers(obj.__class__, lambda member: isinstance(member, property))])

            # Remove properties that have a null value, when required.
            #
            # @note: we don't remove these attributes while building the initial
            #     dictionary because some properties may be calculated.  We would
            #     have called the built-in function `getattr` two times, which
            #     would have resulted in running the property calculation two times.
            if trimmable:
                properties = [
                    (name, value)
                    for name, value in properties.items()
                    if not trimmable or value is not None]

            attributes.update(properties)

        # Retrieve the list of the public members. Remove attributes that have
        # a null value, when required.
        public_members = dict([
            (name, stringify(value, include_properties=include_properties, trimmable=trimmable))
            for name, value in vars(obj).items()
            if not name.startswith('_')                    # Don't include private attributes
               and (not trimmable or value is not None)])  # Don't include null attributes

        attributes.update(public_members)

        return attributes

    return str(obj)


class Object:
    """
    Simple object class that can be used to create anonymous instance on
    demand without creating any additional class.
    """
    def __init__(self, **kwargs):
        """
        Build a new instance `Object`.


        @param kwargs: A keyworded variable length argument dictionary of the
            attributes to automatically add to the object.  For instance::

            ```python
            >>> user = Object(full_name='Daniel CAUNE', email_address='daniel.caune@gmail.com')
            >>> user.full_name
            'Daniel CAUNE'
            >>> user.email_address
            'daniel.caune@gmail.com'
            ```
        """
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __str__(self):
        """
        Return a string representation of the stringified JSON expression of
        his object.


        :return: A string representation of the object.
        """
        return json.dumps(self.stringify(trimmable=True))

    def __repr__(self):
        """
        Return the "official" string representation of this object.


        :return: A JSON formatted string of this object that could be used to
            recreate this object with the same values--providing the
            attributes of this object have Python native data types, no custom
            class.
        """
        attribute_list = ', '.join([
            f'"{name}"=%s' % (f'"{value}"' if isinstance(value, str) else f'{value}')
            for name, value in self.stringify()
        ])

        return f'Object({attribute_list}))'

    def merge(self, other):
        """
        Add the attributes of the other object to this object.


        @param other: An instance `Object`.
        """
        self.__dict__.update(other.__dict__)

    @staticmethod
    def from_json(payload):
        """
        Build an object from a JSON dictionary.


        @param payload: A JSON dictionary which key/value pairs represent
           the members of the Python object to build, or `None`.


        @return: An instance `Object` with members built from the key/value
             pairs of the given JSON dictionary, or `None` if the payload
             is `None` or the given JSON dictionary is empty.
        """
        if payload is None or payload == {}:
            return None

        if isinstance(payload, dict):
            return Object(**dict([
                (k, v if not isinstance(v, (dict, list)) else Object.from_json(v))
                for (k, v) in payload.items()]))

        elif isinstance(payload, list):
            return payload and [Object.from_json(v) if isinstance(v, (dict, list)) else v for v in payload]

        else:
            raise ValueError('The payload MUST be a dictionary or a list')

    def stringify(self, trimmable=False):
        """
        Convert this object to a stringified version where the attribute
        values have been stringified whenever these attributes are not of
        Python primitive data types.

        This function differs from the standard Python `str` as the latter
        returns a string version of object, while this function returns an
        object which attributes have Python primitive data types.


        @param trimmable: Indicate whether null attributes of this object
            need to be stripped out.


        :return: A copy of this object passed where the value of each attribute
            has been stringified when not of a Python primitive data type.
        """
        return stringify(self, trimmable=trimmable)


class Serializable(Object):
    """
    Abstract class object that provides JSON serialization as the
    representation of the inheriting class (cf. `repr` function).
    """
    def __init__(self):
        """
        Build a new instance `Serializable` of the inheriting class.

        This class MUST be inherited by a child class.


        @raise Exception: If the class `Serializable` is instantiated
            directly..
        """
        super().__init__()
        if self.__class__.__name__ == Serializable.__name__:
            raise Exception('The class Serializable cannot be instantiated without using inheritance')

    def __str__(self):
        return str(stringify(self))

    def __repr__(self):
        return self.__str__()


def shallow_copy(obj, attribute_names, ignore_missing_attributes=True):
    """
    Return a shallow copy of the given object, including only the
    specified attributes of this object.


    @param obj: An object to copy.

    @param attribute_names: A list of names of the attributes to copy.

    @param ignore_missing_attributes: `False` indicates that the function
        can ignore attributes that have been specified but that are not
        defined in the given object; `True` indicates that the function
        MUST raise a `KeyError` exception if some specified attributes
        are not defined in the given object.


    @return: A shallow copy of the given object with the specified
        attributes only.


    @raise KeyError: If the argument `ignore_missing_attributes` equals
        `False` and if some specified attributes are not defined in the
        the given object.
    """
    shallow_object = copy.copy(obj)
    shallow_object.__dict__ = {}

    for attribute_name in attribute_names:
        try:
            setattr(shallow_object, attribute_name, getattr(obj, attribute_name))
        except KeyError as error:
            if not ignore_missing_attributes:
                raise error

    return shallow_object
