# Copyright (C) 2021 Majormode.  All rights reserved.
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

class ConnectionProperties:
    def __init__(self, hostname: str, port: int, username: str = None, password: str = None):
        """
        Build a new object `ConnectionProperties`


        :param hostname: The hostname or the IP address of the machine where
            the server to connect to runs on.

        :param port: The TCP port number or the local Unix-domain socket file
             extension which the server is listening at for connections.

        :param username: The username to connect to the server instead of the
            default.

        :param password: The password to authenticate the specified or default
            user.
        """
        if not hostname:
            raise ValueError("Undefined hostname")

        if port is None or port < 0:
            raise ValueError(f"Invalid port number {port}")

        self.__hostname = hostname
        self.__password = password
        self.__port = port
        self.__username = username

    @property
    def hostname(self) -> str:
        return self.__hostname

    @property
    def password(self) -> str:
        return self.__password

    @property
    def port_number(self) -> int:
        return self.__port

    @property
    def username(self) -> str:
        return self.__username
