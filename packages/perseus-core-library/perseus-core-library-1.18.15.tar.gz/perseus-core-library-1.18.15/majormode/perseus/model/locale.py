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

from __future__ import annotations

import re

from majormode.perseus.constant.locale import ISO_3166_1_ALPHA_2_CODES
from majormode.perseus.constant.locale import ISO_639_1_CODES
from majormode.perseus.constant.locale import ISO_639_1_CODES_TO_ISO_639_3_CODES
from majormode.perseus.constant.locale import ISO_639_3_CODES


REGEX_PATTERN_LANGUAGE_CODE = r'[a-z]{2,3}'
REGEX_PATTERN_COUNTRY_CODE = r'[A-Z]{2}'
REGEX_PATTERN_LOCALE = r'(([a-z]{2,3})-([A-Z]{2})$)|([a-z]{2,3}$)'
REGEX_PATTERN_JAVA_LOCALE = r'(([a-z]{2})-([A-Z]{2})$)|([a-z]{2}$)'
REGEX_PATTERN_PERMISSIVE_LOCALE = r'(([a-z]{2,3})[-_]([A-Za-z]{2})$)|([a-z]{2,3}$)'

REGEX_LOCALE = re.compile(REGEX_PATTERN_LOCALE)
REGEX_JAVA_LOCALE = re.compile(REGEX_PATTERN_JAVA_LOCALE)
REGEX_PERMISSIVE_LOCALE = re.compile(REGEX_PATTERN_PERMISSIVE_LOCALE)


class Locale:
    """
    Represent a locale that corresponds to a tag respecting RFC 4646.

    Some computational tasks require information about the current user
    context to be able to process data—particularly when formatting output
    for presentation to the user or when interpreting input.  A locale
    object provides a repository for that information.  An operation that
    requires a locale object to perform its task is called locale-
    sensitive.

    A locale is not a language; it’s a set of conventions for handling
    written language text and various units (for example, date and time
    formats, currency used, and the decimal separator).

    Conceptually, a locale identifies a specific user community—a group of
    users who have similar cultural and linguistic expectations for human-
    computer interaction (and the kinds of data they process). A locale’s
    identifier is a label for a given set of settings.  For example, "en”
    (representing "English”) is an identifier for a linguistic (and to
    some extent cultural) locale that includes (among others) Australia,
    Great Britain, and the United States.  There are also specific
    regional locales for Australian English, British English, U.S.
    English, and so on.

    When data are displayed to a user it should be formatted according to
    the conventions of the user’s native country, region, or culture.
    Conversely, when users enter data, they may do so according to their
    own customs or preferences.  Locale objects are used to provide
    information required to localize the presentation or interpretation of
    data.  This information can include decimal separators, date formats,
    and units of measurement, as well as language and region information.

    Locales are arranged in a hierarchy. At the root is the system locale,
    which provides default values for all settings. Below the root
    hierarchy are language locales.  These encapsulate settings for
    language groups, such as English, German and Chinese (using
    identifiers "en”, "de”, and "zh”).  Normal locales specify a language
    in a particular region (for example "en-GB”, "de-AT”, and "zh-SG”).

    A locale is expressed by a ISO 639-3 alpha-3 code element, optionally
    followed by a dash character `-` and a ISO 3166-1 alpha-2 code.  For
    example: "eng" (which denotes a standard English), "eng-US" (which
    denotes an American English).
    """
    class MalformedLocaleException(Exception):
        """
        Indicate that a string doesn't comply with the valid expression of a
        locale.
        """

    class InvalidCountryCodeException(Exception):
        """
        Indicate that a string doesn't match a valid country code.
        """

    class InvalidLanguageCodeException(Exception):
        """
        Indicate that a string doesn't match a valid language code.
        """

    @classmethod
    def assert_country_code(cls, code: str, strict: bool = True) -> None:
        """
        Asset that a country code is valid


        :param code: A country code.

        :param strict: Indicate whether the comparison of the country code
            string is case sensitive or not.


        :raise InvalidCountryCodeException: If the country code passed to this
            function doesn't match a valid language code.
        """
        if not cls.is_country_code(code, strict=strict):
            raise cls.InvalidCountryCodeException(f'Invalid country code "{code}"')

    @classmethod
    def assert_language_code(cls, code: str, strict: bool = True) -> None:
        """
        Assert the a language code is valid


        :param code: A language code.

        :param strict: Indicate whether the comparison of the language code
            string is case sensitive or not.


        :raise InvalidLanguageCodeException: If the language code passed to
            this function doesn't match a valid language code.
        """
        if not cls.is_language_code(code, strict=strict):
            raise cls.InvalidLanguageCodeException(f'Invalid language code "{code}"')

    def __eq__(self, other: object) -> bool:
        """
        Indicate whether this locale is the same than the other locale

        Two locale objects are the same when they corresponds to the same
        language and the same country (unless no country is defined for both
        locales).


        :param other: The other locale to compare.


        :return: Indicate whether this locale is the identical to the other
            locale.
        """
        if not isinstance(other, Locale):
            return False

        return self.language_code == other.language_code and \
            self.__country_code == other.country_code

    def __hash__(self) -> int:
        if not hasattr(self, '__hash'):
            encoded_locale = self.language_code if self.__country_code is None \
                else f'{self.language_code}{self.__country_code}'

            self.__hash = sum([
                (ord(c) - ord('a') if ord(c) >= ord('a') else ord(c) - ord('A')) * 52**i
                for i, c in enumerate(encoded_locale)
            ])

        return self.__hash

    def __init__(
            self,
            language_code: str,
            country_code: str = None,
            strict: bool = True):
        """
        Build a locale providing a ISO 639-3 alpha-3 code (or alpha-2 code),
        and an optional ISO 3166-1 alpha-2 code


        :param language_code: A ISO 639-3 alpha-3 code (or alpha-2 code; which
            will be automatically converted to its equivalent ISO 639-3
            alpha-3 code).

        :param country_code: A ISO 3166-1 alpha-2 code.


        :raise InvalidCountryCodeException: If the argument `country_code`
            doesn't match a valid country_code code.

        :raose InvalidLanguageCodeException: If the argument `language_code`
            doesn't match a valid language code.
        """
        self.assert_language_code(language_code, strict=strict)
        if country_code:
            self.assert_country_code(country_code, strict=strict)

        self.__language_code = self.__to_iso_639_3(language_code)
        self.__country_code = country_code

    def __repr__(self) -> str:
        return self.to_string()

    def __str__(self) -> str:
        return self.to_string()

    @staticmethod
    def __to_iso_639_3(code: str) -> str:
        return code if len(code) == 3 else ISO_639_1_CODES_TO_ISO_639_3_CODES[code]

    @property
    def country_code(self) -> str:
        return self.__country_code

    @staticmethod
    def from_string(locale: str, strict: bool = True) -> Locale | None:
        """
        Return an object `Locale` corresponding to the string representation
        of a locale.


        :param locale: A string representation of a locale, i.e., a ISO 639-3
           alpha-3 code (or alpha-2 code), optionally followed by a dash
           character `-` and a ISO 3166-1 alpha-2 code.

        :param strict: Indicate whether the string representation of a locale
            has to be strictly compliant with RFC 4646, or whether a Java-style
            locale (character `_` instead of `-`) is accepted.


        :return: A locale or `None` if the argument `locale` is undefined.
        """
        if not locale:
            return None

        language_code, country_code = Locale.decompose_locale(locale, strict)
        return Locale(language_code, country_code, strict=strict)

    @classmethod
    def is_country_code(cls, code: str, strict: bool = True) -> bool:
        return cls.is_iso_3166_1_alpha_2(code, strict=strict)

    @staticmethod
    def is_iso_3166_1_alpha_2(code: str, strict: bool = True) -> bool:
        return (code if strict else code.upper()) in ISO_3166_1_ALPHA_2_CODES

    @staticmethod
    def is_iso_639_2_code(code: str, strict: bool = True) -> bool:
        return (code if strict else code.lower()) in ISO_639_1_CODES

    @staticmethod
    def is_iso_639_3_code(code: str, strict: bool = True):
        return (code if strict else code.lower()) in ISO_639_3_CODES

    @classmethod
    def is_language_code(cls, code: str, strict: bool = True):
        if 2 <= len(code) <= 3:
            return cls.is_iso_639_2_code(code, strict=strict) if len(code) == 2 \
                else cls.is_iso_639_3_code(code, strict=strict)
        return False

    def is_similar(self, other: Locale) -> bool:
        """
        Indicate whether the current locale object is similar to another
        passed to the comparison method.  Two locale objects are said similar
        if they have at least the same language, but not necessarily the same
        country.


        :param other: a `Locale` object to compare with the current locale
            object.


        :return: `True` if the given locale is similar to the current
            locale; `False` otherwise.
        """
        return self.language_code == other.language_code

    @property
    def language_code(self) -> str:
        return self.__language_code
    
    def to_http_string(self) -> str:
        """
        Return the string representation of the locale compatible with the
        HTTP header `Accept-Language` as specified in `RFC 7231
        <https://tools.ietf.org/html/rfc7231#section-5.3.5>_`

        The Accept-Language request HTTP header advertises which languages the
        client is able to understand, and which locale variant is preferred.


        :return: a string representation of this locale compatible with HTTP
            request, i.e., a ISO 639-3 alpha-2, optionally followed by a dash
            character `-` and a ISO 3166-1 alpha-2 code.
        """
        return self.language_code[:2] if self.__country_code is None \
            else f'{self.language_code[:2]}-{self.__country_code}'

    def to_string(self) -> str:
        """
        Return a string representation of this object `Locale`.


        :return: a string representation of a locale, i.e., a ISO 639-3
             alpha-3 code (or alpha-2 code), optionally followed by a dash
            character `-` and a ISO 3166-1 alpha-2 code.
        """
        return Locale.compose_locale(self.language_code, self.__country_code)

    @staticmethod
    def decompose_locale(locale: str, strict: bool = True) -> (str, str):
        """
        Return the decomposition of the specified locale into a language
        and a country codes


        :param locale: A ISO 639-3 alpha-3 code (or alpha-2 code), optionally
            followed by a dash character `-` and a ISO 3166-1 alpha-2 code.
            If `None` passed, the function returns the default locale, i.e.,
            standard English `('eng', None)`.

        :param strict: Indicate whether the string representation of a locale
            has to be strictly compliant with RFC 4646, or whether a Java-
            style locale (character `_` instead of `-`) is accepted.


        :return: A tuple `(language_code, country_code)`, where the first code
            represents a ISO 639-3 alpha-3 code (or alpha-2 code), and the
            second code a ISO 3166-1 alpha-2 code.
        """
        if locale is None:
            raise ValueError("Undefined value 'locale'")

        match = REGEX_LOCALE.match(locale)
        if match is None:
            if strict:
                raise Locale.MalformedLocaleException(
                    f'The string "{locale}" doesn\'t represent a valid locale')

            match = REGEX_PERMISSIVE_LOCALE.match(locale)
            if match is None:
                raise Locale.MalformedLocaleException(
                    f'The string "{locale}" doesn\'t represent any forms of a valid locale')

        _, locale_language_code, locale_country_code, language_code = match.groups()

        return (locale_language_code, locale_country_code.upper()) if language_code is None \
            else (language_code, None)

    @staticmethod
    def compose_locale(language_code: str, country_code: str = None) -> str:
        """
        Return the string representation of the locale specified with a ISO
        639-3 alpha-3 code (or alpha-2 code), optionally followed by a dash
        character `-` and a ISO 3166-1 alpha-2 code


        :param language_code: A ISO 639-3 alpha-3 code (or alpha-2 code).

        :param country_code: A ISO 3166-1 alpha-2 code.


        :return: A string representing a locale.
        """
        return language_code if country_code is None \
            else f'{language_code}-{country_code}'


DEFAULT_LOCALE = Locale('eng')
