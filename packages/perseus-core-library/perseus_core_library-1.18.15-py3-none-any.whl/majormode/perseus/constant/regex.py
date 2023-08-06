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


# Regular expression to match an email address compliant with RFC 5322
# (http://tools.ietf.org/html/rfc5322#section-3.4.1).  This regular
# expression has two parts: the part before the `@`, and the part
# after the `@`.  There are two alternatives for the part before the
# `@`: it can either consist of a series of letters, digits and
# certain symbols, including one or more dots.  However, dots may not
# appear consecutively or at the start or end of the email address.
# The other alternative requires the part before the `@` to be
# enclosed in double quotes, allowing any string of ASCII characters
# between the quotes.  Whitespace characters, double quotes and
# backslashes must be escaped with backslashes.
#
# The part after the `@` also has two alternatives.  It can either
# be a fully qualified domain name (e.g., `somehost.example.com`).
# The literal Internet address can either be an IP address, or a
# domain-specific routing address.  This regular expression omits the
# syntax using double quotes and square brackets, as RFC 2822 marks
# this notation as obsolete.
# REGEX_PATTERN_EMAIL_ADDRESS = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
REGEX_PATTERN_EMAIL_ADDRESS = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""

# Regular expression that matches an integer.
REGEX_PATTERN_INTEGER = r'\d+'

# Regular expression that matches an Internet Protocol version 4 (32-bit
# number).
REGEX_PATTERN_IPV4 = r'(\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})'

# Regular expression that matches a Media Access Control (MAC) address.
#
# :note: This regular expression is generated with the following code:
#
#     ```python
#     r'^%s$' % '[.:-]{0,1}'.join([r'([0-9A-Za-z]{2})' for i in range(6)])
#     ```
REGEX_PATTERN_MAC_ADDRESS = r'([0-9A-Za-z]{2})[.:-]{0,1}([0-9A-Za-z]{2})[.:-]{0,1}([0-9A-Za-z]{2})[.:-]{0,1}([0-9A-Za-z]{2})[.:-]{0,1}([0-9A-Za-z]{2})[.:-]{0,1}([0-9A-Za-z]{2})'

# Regular expression to require a password to contain:
#
# - At least eight characters
# - At least one uppercase letter
# - At least one lowercase letter
# - At least one digit
# - At least one special character
REGEX_PATTERN_PASSWORD = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

# Regular expression that matches a phone number in E.164 numbering plan,
# formatted according to RFC 5733 (Extensible Provisioning Protocol (EPP)
# Contact Mapping).  EPP-style phone numbers use the format
# `+CCC.NNNNNNNNNNxEEEE`, where `C` is the 1–3 digit country code,
# `N` is up to 14 digits, and `E` is the (optional) extension.  The
# leading plus sign and the dot following the country code are required.
# The literal "x" character is required only if an extension is provided.
#
# References :
# - E.164 numbering plan; https://www.itu.int/rec/T-REC-E.164-201011-I/en>
# - Extensible Provisioning Protocol (EPP) Contact Mapping);
#   https://tools.ietf.org/html/rfc5733#section-2.5
#
# @depracated: REGEX_PATTERN_PHONE_NUMBER = r'(([+][(]?[0-9]{1,3}[)]?)|([(]?[0-9]{4}[)]?))\s*[)]?[-\s\.]?[(]?[0-9]{1,3}[)]?([-\s\.]?[0-9]{3})([-\s\.]?[0-9]{3,4})'
REGEX_PATTERN_PHONE_NUMBER = r'^\+[0-9]{1,3}\.[0-9]{4,14}(?:x.+)?$'

# Pattern of a regular expression to match a username:
#
# 1. MUST only contain lowercase/uppercase letters, digits, underscores,
#    and periods
#
# 2. MUST start with a lowercase/uppercase letter
#
# 3. MUST NOT end with an underscore or a period
#
# 4. MUST NOT contain underscore and period next to each other (e.g.,
#    "user_.name")
#
# 5. MUST NOT contain underscore or period used multiple times in a row
#    (e.g., "user__name, "user..name")
#
# 6. MUST contain between 6 and 20 characters
REGEX_PATTERN_USERNAME = r'^(?=.{6,20}$)(?![0-9_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$'

# Regular expression that matches a Universally Unique Identifier (UUID).
REGEX_PATTERN_UUID = r'(?i)[\da-z]{8}-{0,1}[\da-z]{4}-{0,1}[\da-z]{4}-{0,1}[\da-z]{4}-{0,1}[\da-z]{12}'
