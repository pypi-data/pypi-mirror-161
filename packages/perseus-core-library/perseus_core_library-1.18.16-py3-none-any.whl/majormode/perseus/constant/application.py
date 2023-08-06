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


ApplicationMemberRole = Enum(
    # Secondary contact for teams and has many of the  same responsibilities
    # as the agent role. Administrators have access to all applications
    # registered on behalf of the team that these administrators belong to.
    'administrator',

    # Responsible for entering into legal agreements with the Service
    # Provider of the online platform where server applications are deployed
    # to or connect to.  The person who completes program enrollment is
    # assigned the agent role.
    'agent',

    # Manage development and delivery of an application.
    'developer',
)

ApplicationPlatform = Enum(
    # Command line interface (CLI) application that runs on a terminal console.
    'console',

    # Graphical User Interface (GUI) application that runs stand-alone in a
    # desktop or laptop computer.
    'desktop',

    # Graphical User Interface (GUI) application that runs in a smartphone.
    'mobile',

    # Application that waits for requests from other applications and
    # responds to them, thus providing a "service" upon their request.
    # For example, a web server, a RESTful API, are server applications.
    'server',
)

ApplicationStage = Enum(
    # A testing environment that enables the isolated execution of an
    # application for independent evaluation, monitoring or testing.
    'sandbox',

    # A production environment where the application is made available to
    # real users (equivalent to ``EnvironmentStage.prod``).
    'live',
)

