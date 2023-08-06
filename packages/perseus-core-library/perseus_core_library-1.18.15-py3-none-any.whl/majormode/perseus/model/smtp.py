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


class SmtpConnectionProperties:
    """
    Represent the properties of connection to a Simple Mail Transport
    Protocol (SMTP) server.
    """
    def __eq__(self, other):
        return self.hostname.lower() == other.hostname.lower() \
            and self.port_number == other.port_number \
            and self.username == other.username \
            and self.password == other.password

    def __init__(
            self,
            hostname,
            username,
            password,
            port_number=587):
        """
        Build the connection properties to access a SMTP server

        :param hostname: Internet address or fully qualified domain name --
            human-readable nickname that corresponds to the address -- of the
            SMTP server is running on.

        :param port_number:  Internet port number on which the remote SMTP
            server is listening at.

            SMTP communication between mail servers uses TCP port 25.  Mail
            clients on the other hand, often submit the outgoing emails to a
            mail server on port 587.  Despite being deprecated, mail providers
            sometimes still permit the use of nonstandard port 465 for this
            purpose.

        :param username: username to authenticate with against the SMTP server.

        :param password: password associate to the username to authenticate
            with against the SMTP server.
        """
        self.hostname = hostname
        self.port_number = port_number
        self.username = username
        self.password = password

