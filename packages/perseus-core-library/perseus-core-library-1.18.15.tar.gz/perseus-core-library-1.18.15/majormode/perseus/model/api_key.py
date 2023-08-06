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


class ApiKey:
    """
    Represent an Application Programming Interface (API) key, sometimes
    referred to as application ID, which uniquely identifies a client
    application such as a Web, a desktop, or a mobile application that
    needs to access to a remote service on another computer system, known
    as a server, by way of a network.
    """
    def __init__(self, consumer_key, consumer_secret):
        """
        Build a new instance of an API key.


        :param consumer_key: a unique string used by the Consumer to identify
            itself to the Service Provider.

        :param consumer_secret: a secret used by the Consumer to establish
            ownership of the Consumer Key.
        """
        self.__consumer_key = consumer_key
        self.__consumer_secret = consumer_secret

    @property
    def consumer_key(self):
        return self.__consumer_key

    @property
    def consumer_secret(self):
        return self.__consumer_secret
