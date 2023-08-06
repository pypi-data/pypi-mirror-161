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

import socket
import uuid


def get_ip_address():
    """
    Return the Internet Protocol (IP) address of the network interface of
    the computer the Python program is running on.

    An IP address is a numerical label assigned to a network interface
    that uses the Internet Protocol for communication.


    :return: a string representation of the IP address of the network
        interface, using a dot-decimal notation, which consists of four
        decimal numbers, each ranging from ``0`` to ``255``, separated by
        dots, e.g., ``172.16.254.1``.
    """
    return socket.gethostbyname(socket.gethostname())


def get_mac_address():
    """
    Return the Media Access Control (MAC) address of the network interface
    of the computer the Python program is running on.

    A MAC address is a unique identifier assigned to network interfaces
    for communications on the physical network segment.  MAC addresses are
    used for numerous network technologies and most IEEE 802 network
    technologies, including Ethernet.


    :return: an hexadecimal string representation without the leading
        ``0x`` of the network interface MAC address.
    """
    return '%x' % uuid.getnode()
