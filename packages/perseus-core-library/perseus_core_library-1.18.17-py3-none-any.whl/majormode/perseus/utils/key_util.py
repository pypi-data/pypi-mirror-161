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
import hashlib
import itertools
import time


def calculate_base_sequence(base_offsets):
    """
    Return a sequence of characters corresponding to the specified base.

    Example:

    ```python
    >>> calculate_base_sequence([ ('0', '9'), ('A', 'F') ])
    '0123456789ABCDEF'
    ```
    

    :param base_offsets: a list of character offsets in the form of tuples
        ``(x, y)`` where ``x`` corresponds to the first character of a
        sequence and ``y`` to the last character of this sequence.


    :return a sequence of characters, i.e., a string, corresponding to the
        specified base.
    """
    return ''.join([chr(c) for c in list(itertools.chain.from_iterable(
        [range(ord(x), ord(y) + 1) for x, y in base_offsets]))])


BASE62_OFFSETS = [('0', '9'), ('a', 'z'), ('A', 'Z')]
BASE62 = calculate_base_sequence(BASE62_OFFSETS)


def generate_secured_key(
        value,
        key_nonce_separator='.',
        nonce_length=4,
        base=BASE62):
    """
    Generate a secured key composed of the integer value encoded in Base62
    and a nonce.


    :param value: an integer value.

    :param key_nonce_separator: the character that is used to separate the
        key and the nonce to form the secured key.

    :param nonce_length: the number of characters to compose the nonce.

    :param base: a sequence of characters that is used to encode the
           integer value.


    :return: a tuple ``(key, nonce, secured_key)``:
        * ``key``: string representation of the integer value in Base62.

        * ``nonce``: "number used once", a pseudo-random number to
          ensure that the key cannot be reused in replay attacks.

        * ``secured_key``: a string composed of the key concatenated with
          the nonce.
    """
    if not isinstance(value, int):
        raise ValueError()

    posix_time = int(time.mktime(datetime.datetime.now().timetuple()))
    nonce = hashlib.md5(str(posix_time)).hexdigest()[:nonce_length]
    key = int_to_key(value, base=base)
    return key, nonce, f'{key}{key_nonce_separator}{nonce}'


def int_to_key(value, base=BASE62):
    """
    Convert the specified integer to a key using the given base.


    :param value: a positive integer.

    :param base: a sequence of characters that is used to encode the
        integer value.


    :return: a key expressed in the specified base.
    """
    def key_sequence_generator(value, base):
        """
        Generator for producing sequence of characters of a key providing an
        integer value and a base of characters for encoding, such as Base62
        for instance.


        :param value: a positive integer.

        :param base: a sequence of characters that is used to encode the
            integer value.


        :return: the next character of the object's key encoded with the
                 specified base.
        """
        base_length = len(base)
        while True:
            yield base[value % base_length]
            if value < base_length:
                break
            value //= base_length

    return ''.join([c for c in key_sequence_generator(value, base)])


def key_to_int(key, base=BASE62):
    """
    Convert the following key to an integer.


    :param key: a key.

    :param base: a sequence of characters that was used to encode the
        integer value.


    :return: the integer value corresponding to the given key.


    @raise ValueError: if one character of the specified key doesn't match
        any character of the specified base.
    """
    base_length = len(base)

    value = 0
    for c in reversed(key):
        value = (value * base_length) + base.index(c)

    return value


def parse_secured_key(
        secured_key,
        key_nonce_separator='.',
        nonce_length=4,
        base=BASE62):
    """
    Parse a given secured key and return its associated integer, the key
    itself, and the embedded nonce.


    :param secured_key a string representation of a secured key composed
        of a key in Base62, a separator character, and a nonce.

    :param key_nonce_separator: the character that is used to separate the
        key and the nonce to form the secured key.

    :param nonce_length: the number of characters to compose the nonce.

    :param base: a sequence of characters that is used to encode the
           integer value.


    :return: a tuple ``(value, key, nonce)``:

        * ``value``: the integer value of the key.

        * ``key``: the plain-text key.

        * ``nonce``: "number used once", a pseudo-random number to ensure that
          the key cannot be reused in replay attacks.


    @raise ValueError: if the format of the secured key is invalid, or if
        the embedded nonce is of the wrong length.
       """
    parts = secured_key.split(key_nonce_separator)
    if len(parts) != 2:
        raise ValueError("Invalid secured key format")

    key, nonce = parts
    if len(nonce) != nonce_length:
        raise ValueError("Invalid length of the key nonce")

    return key_to_int(key, base=base), key, nonce
