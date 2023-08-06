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

from majormode.perseus.model.enum import Enum


HttpMethod = Enum(
    'DELETE',
    'GET',
    'OPTIONS',
    'POST',
    'PUT'
)


HttpScheme = Enum(
    'http',
    'https'
)


# Regular expression that matches a valid User-Agent HTTP header:
#
#     ProductName/ProductVersion (OperatingSystemName/OperatingSystemVersion; MobileDeviceName)
#
# This regular expression decomposes a valid user-agent into the
# following groups:
#
# * group(1): name of the client application
#
# * group(2): version of the client application
#
# * group(3): name of the operating system running the client
#   application.
#
# * group(4): version of the operating system running the client
#   application.
#
# * group(5): name of the device model running the client application.
REGEX_PATTERN_USER_AGENT = r'^([^\/]+)\/([\d.]+)\s*\(([\w]+)\s+([^;]+)\s*;\s*(.+)\)$'

