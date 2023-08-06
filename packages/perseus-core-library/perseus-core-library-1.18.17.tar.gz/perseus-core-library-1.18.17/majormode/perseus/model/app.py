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


class ClientApplication:
    """
    Represent a client application that may communicate with a remote
    service such as a Web server or a RESTful API server.
    """
    def __eq__(self, other):
        # Check conditions from the most to least probable of difference.
        return self.__product_version == other.__product_version \
            and self.__os_version == other.__os_version \
            and self.__product_name == other.__product_name \
            and self.__os_name == other.__os_name \
            and self.__device_model == other.__device_model

    def __init__(
            self,
            product_name,
            product_version,
            os_name,
            os_version,
            device_model):
        """
        Build a new instance `ClientApplication`.


        :param product_name: Official name of the client application.

        :param product_version: An instance `Version` representing the current
            version of the client application.

        :param os_name: Name of the operating system this client application
            is running on.

        :param os_version: A string representation of the version of the
            operating system this client application is running on.

        :param device_model: end-user-visible name of the device on which the
            client application is running on.
        """
        self.__product_name = product_name
        self.__product_version = product_version
        self.__os_name = os_name
        self.__os_version = os_version
        self.__device_model = device_model

    @property
    def device_model(self):
        return self.__device_model

    @property
    def os_name(self):
        return self.__os_name

    @property
    def os_version(self):
        return self.__os_version

    @property
    def product_name(self):
        return self.__product_name

    @property
    def product_version(self):
        return self.__product_version
