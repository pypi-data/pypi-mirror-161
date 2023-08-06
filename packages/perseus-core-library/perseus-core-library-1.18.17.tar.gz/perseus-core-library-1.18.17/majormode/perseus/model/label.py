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

from majormode.perseus.model.locale import DEFAULT_LOCALE
from majormode.perseus.model.locale import Locale


class Label:
    """
    A label corresponds to a humanly-readable textual content written in a
    given locale, English by default.
    """
    def __init__(self, content, locale=DEFAULT_LOCALE):
        """
        Build a new ``Label`` instance.


        :param content: humanly-readable textual content of the label.

        :param locale: a ``Locale`` instance defining the language of the
            textual content of this label, English by default.


        :raise ValueError: if the argument ``locale`` is ``None``.
        """
        if locale is None:
            raise ValueError('The locale of a label CANNOT be null')

        if not isinstance(locale, Locale):
            raise TypeError('The locale MUST be an instance of `Locale`')

        self.__content = content.strip()
        self.__locale = locale

    @staticmethod
    def from_json(payload):
        return payload and Label(
            payload['content'],
            locale=Locale.from_string(payload['locale']))

    @property
    def content(self):
        return self.__content

    @property
    def locale(self):
        return self.__locale
