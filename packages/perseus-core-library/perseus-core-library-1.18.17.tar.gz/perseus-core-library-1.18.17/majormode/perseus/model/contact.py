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

import re

from majormode.perseus.constant.contact import ContactName
from majormode.perseus.constant.privacy import Visibility
from majormode.perseus.constant.regex import REGEX_PATTERN_EMAIL_ADDRESS
from majormode.perseus.constant.regex import REGEX_PATTERN_PHONE_NUMBER
from majormode.perseus.utils import cast


class Contact:
    """
    Represent a contact information, such as an e-mail address, a phone
    numbers, the Uniform Resource Locator (URL) of a Web site.
    """
    class InvalidContactException(Exception):
        """
        Indicate that a given name doesn't represent a valid contact name.
        """

    REGEX_EMAIL_ADDRESS = re.compile(REGEX_PATTERN_EMAIL_ADDRESS)
    REGEX_PHONE_NUMBER = re.compile(REGEX_PATTERN_PHONE_NUMBER)

    __CONTACT_NAME_REGEX_MAPPING = {
        ContactName.EMAIL: REGEX_EMAIL_ADDRESS,
        ContactName.PHONE: REGEX_PHONE_NUMBER,
    }

    def __assert_contact_value(self, property_name, property_value):
        if not self.__CONTACT_NAME_REGEX_MAPPING[property_name].match(property_value):
            raise self.InvalidContactException(
                f'Invalid value "{property_value}" of a contact information {property_name}')

    def __init__(
            self,
            property_name,
            property_value,
            is_primary=False,
            is_verified=False,
            strict=True,
            visibility=Visibility.public):
        """
        Build a new instance `Contact`.


        :param property_name: An item of the enumeration `ContactName`
            representing the type of this contact information.

        :param property_value: Value of this contact information representing
            by a string, such as `+84.8272170781`, the formatted value for a
            telephone number property.

        :param is_primary: Indicate whether this contact property is the first
            to be used to contact the entity that this contact information
            corresponds to.  There is only one primary contact property for a
            given property name (e.g., `EMAIL`, `PHONE`, `WEBSITE`).

        :param is_verified: Indicate whether this contact information has been
            verified, whether it has been grabbed from a trusted Social
            Networking Service (SNS), or whether through a challenge/response
            process.

        :param visibility: An item of the enumeration `Visibility` that
            indicates the visibility of this contact information to other
            users.  By default, `Visibility.public` if not defined.


        :raise AssertError: If the specified type of this contact information
            is not a string representation of an item of the enumeration
            `ContactName`.

        :raise ValueError: If the value of this contact information is null.
        """
        if isinstance(property_name, str):
            property_name = cast.string_to_enum(property_name, ContactName)
        else:
            if property_name not in ContactName:
                raise self.InvalidContactException(
                    f'The name "{property_name} doesn\'t represent a valid contact property name')

        if property_value is None:
            raise self.InvalidContactException("The property value of a contact MUST NOT be null")

        self.__property_name = property_name
        self.__property_value = property_value.strip().lower()

        if strict:
            self.__assert_contact_value(self.__property_name, self.__property_value)

        self.__is_primary = is_primary
        self.__is_verified = is_verified
        self.__visibility = visibility or Visibility.public

    def __eq__(self, other):
        """
        Check whether this contact information to the one passed to this
        function.

        Two instances are equivalent when they are of the same type and they
        have the same value.


        :param other: an instance `Contact`.


        :return: `True` if this contact information corresponds to the
            contact information passed to this function; `False` otherwise.
        """
        return self.__property_name == other.__property_name \
               and self.__property_value == other.__property_value

    def __str__(self):
        """
        Return a nicely printable string representation of this contact
        information:

            [ name:string, value:string, [is_primary:boolean, [is_verified:boolean]] ]


        :return: a string of the array representation of this contact
            information.
        """
        # Do not include the attribute `is_verified` if the attribute
        # `is_primary` has not been defined.
        attributes = (
            str(self.__property_name),
            self.__property_value,
            self.__is_primary,
            self.__is_primary and self.__is_verified)

        return str([
            attribute
            for attribute in attributes
            if attribute is not None
        ])

    @staticmethod
    def from_json(payload):
        """
        Convert the JSON expression of a contact information into an instance
        `Contact`.


        :param payload: a JSON expression representing a contact information:

            [ type:ContactName, value:string, [is_primary:boolean, [is_verified:boolean]] ]


        :return: an instance `Contact`.


        :raise AssertError: if the specified type of this contact information
            is not a string representation of an item of the enumeration
            `ContactName`.

        :raise ValueError: if the value of this contact information is null.
        """
        contact_item_number = len(payload)
        assert 2 <= contact_item_number <= 4, 'Invalid contact information format'

        is_primary = is_verified = None

        # Unpack the contact information to each component.
        if contact_item_number == 2:
            property_name, property_value = payload
        elif contact_item_number == 3:
            property_name, property_value, is_primary = payload
        else:
            property_name, property_value, is_primary, is_verified = payload

        return Contact(
            cast.string_to_enum(property_name, ContactName), property_value,
            is_primary=is_primary and cast.string_to_boolean(is_primary, strict=True),
            is_verified=is_verified and cast.string_to_boolean(is_verified, strict=True))

    @staticmethod
    def from_object(obj):
        """
        Convert an object representing a contact information to an instance
        `Contact`.


        :param obj: an object containing the following attributes:

            * `name`: an item of the enumeration `ContactName` representing the
              type of this contact information.

            * `value`: value of this contact information representing by a string,
              such as `+84.01272170781`, the formatted value for a telephone
              number property.

            * `is_primary`: indicate whether this contact property is the first to
              be used to contact the entity that this contact information
              corresponds to.  There is only one primary contact property for a
              given property name (e.g., `EMAIL`, `PHONE`, `WEBSITE`).

            * `is_verified`: indicate whether this contact information has been
              verified, whether it has been grabbed from a trusted Social
              Networking Service (SNS), or whether through a challenge/response
              process.


        :raise ValueError: if the value of this contact information is null.
        """
        return obj if isinstance(obj, Contact) \
            else Contact(
                cast.string_to_enum(obj.property_name, ContactName),
                obj.property_value,
                is_primary=obj.is_primary and cast.string_to_boolean(obj.is_primary, strict=True),
                is_verified=obj.is_verified and cast.string_to_boolean(obj.is_verified, strict=True))

    @classmethod
    def from_string(
            cls,
            property_value,
            is_primary=None,
            is_verified=None,
            visibility=None):
        """
        Return the contact information corresponding to a contact value.


        :param property_value: A string representing a contact value.

        :param is_primary: Indicate whether this contact property is the first
            to be used to contact the entity that this contact information
            corresponds to.  There is only one primary contact property for a
            given property name (e.g., `EMAIL`, `PHONE`, `WEBSITE`).

        :param is_verified: Indicate whether this contact information has been
            verified, whether it has been grabbed from a trusted Social
            Networking Service (SNS), or whether through a challenge/response
            process.

        :param visibility: An item of the enumeration `Visibility` that
            indicates the visibility of this contact information to other
            users.  By default, `Visibility.public` if not defined.


        :return: An object `Contact` with the appropriate contact name and the
            given contact value.


        :raise InvalidContactException: If the contact value doesn't
            correspond to a valid contact information.
        """
        for property_name, regex in cls.__CONTACT_NAME_REGEX_MAPPING.items():
            if regex.match(property_value):
                return Contact(
                    property_name,
                    property_value,
                    is_primary=is_primary,
                    is_verified=is_verified,
                    strict=False,
                    visibility=visibility)
        else:
            raise cls.InvalidContactException(f'Unsupported contact information "{property_value}"')

    @property
    def is_primary(self):
        return self.__is_primary

    @is_primary.setter
    def is_primary(self, is_primary):
        if not isinstance(is_primary, bool):
            raise TypeError("argument 'is_primary' MUST be a boolean value")

        self.__is_primary = is_primary

    @property
    def is_verified(self):
        return self.__is_verified

    @property
    def property_name(self):
        return self.__property_name

    @property
    def property_value(self):
        return self.__property_value

    @property
    def visibility(self):
        return self.__visibility
