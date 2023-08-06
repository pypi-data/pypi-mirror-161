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

import functools
import re
import sys
import unidecode

from majormode.perseus.constant.regex import REGEX_PATTERN_EMAIL_ADDRESS
from majormode.perseus.constant.regex import REGEX_PATTERN_PHONE_NUMBER
from majormode.perseus.constant.regex import REGEX_PATTERN_USERNAME

REGEX_EMAIL_ADDRESS = re.compile(REGEX_PATTERN_EMAIL_ADDRESS)
REGEX_PHONE_NUMBER = re.compile(REGEX_PATTERN_PHONE_NUMBER)
REGEX_USERNAME = re.compile(REGEX_PATTERN_USERNAME)


def flatten_list(l):
    """
    Flatten the elements contained in the sub-lists of a list.


    :param l: A list containing sub-lists of elements.


    :return: A list with all the elements flattened from the sub-lists of
        the list `l`.
    """
    return [e for sublist in l for e in sublist]


def inicap_string(s, cleanse=False):
    """
    Convert the first letter of each word to capital letter without
    touching the rest of the word.


    @param s: a string.

    @param cleanse: `True` to remove any separator character from the
        string, such as comma; `False` to keeps any character but space.


    @return: a string for which the first letter of each word has been
        capitalized without modifying the case of the rest of the word.
    """
    return s and ' '.join([
        word[0].upper() + word[1:]
        for word in (s.split() if cleanse else s.split(' '))])


def is_email_address(s):
    """
    Indicate whether a string corresponds to an email address


    @param s: A string that is expected to be an email address.


    @return: `True` if the string corresponds to an email address,
        `False` otherwise.
    """
    return (s and REGEX_EMAIL_ADDRESS.match(s.strip().lower())) is not None


def is_phone_number(s):
    """
    Indicate whether a string corresponds to an international phone number

    The phone number MUST be written in E.164 numbering plan, formatted
    according to RFC 5733 (Extensible Provisioning Protocol (EPP) Contact
    Mapping).

    EPP-style phone numbers use the format `+CCC.NNNNNNNNNNxEEEE`, where
    `C` is the 1–3 digit country code, `N` is up to 14 digits, and `E` is
    the (optional) extension.  The leading plus sign and the dot following
    the country code are required.  The literal "x" character is required
    only if an extension is provided.

    :param s: An EPP-style phone number.


    :return: `True` if the string represents an international phone number,
        `False` otherwise.
    """
    return (s and REGEX_PHONE_NUMBER.match(s.strip())) is not None


def is_username(s):
    """
    Indicate whether a string corresponds to a username


    :param s: A username


    :return: `True` if the string represents a username, `False` otherwise.
    """
    return (s and REGEX_USERNAME.match(s.strip())) is not None


def string_hash_code(s):
    """
    Calculate the hash code of a string.


    :param s: a string.


    :return: the hash code of the string.
    """
    string_length = len(s)
    return functools.reduce(
        lambda x, y: x + y,
        [ord(s[i]) * 31 ** (string_length - i - 1) for i in range(string_length)]) % sys.maxsize


def strip_string_words(s):
    """
    Return the string with all its words stripped.


    :param s: A string.


    :return: The string with all its words stripped.
    """
    return s and ' '.join([word for word in s.split(' ')])


def string_to_keywords(s, keyword_minimal_length=1):
    """
    Split the specified string(s) in a list of ASCII keywords

    Remove any punctuation character from the specified list of keywords,
    remove any double or more space character and represent Unicode
    characters in ASCII.


    :param s: A word or a list of words to strip out any punctuation
        characters and to convert to ASCII characters.

    :param keyword_minimal_length: Minimal number of characters of the
        keywords to be returned.


    :return: A list of distinct keywords cleansed from any special Unicode
        accentuated character, punctuation character, and double space
        character.


    :raise ValueError: If the argument is null, or if it is not a string
        or a list of string.
    """
    if s is None:
        return None

    if isinstance(s, str):
        s = [s]
    elif isinstance(s, (list, set, tuple)):
        if any(not isinstance(_, str) for _ in s):
            raise ValueError('Each item of the list `s` MUST be a string')
    else:
        raise ValueError('The argument `s` MUST be a string or a list of strings')

    # Convert the list of strings to ASCII lower characters.
    ascii_strings = [
        unidecode.unidecode(_.strip()).lower()
        for _ in s
    ]

    # Replace from the list of strings any punctuation character with space.
    punctuationless_strings = [
        re.sub(r'[.,\\/#!$%^&*;:{}=\-_`~()<>"\']', ' ', _)
        for _ in ascii_strings
    ]

    # Decompose the string into distinct keywords.
    keywords = set(flatten_list([
        _.split()
        for _ in punctuationless_strings
    ]))

    # Filter out sub-keywords of less than 2 characters.
    keywords = [
        keyword
        for keyword in keywords
        if len(keyword) > keyword_minimal_length
    ]

    return keywords
