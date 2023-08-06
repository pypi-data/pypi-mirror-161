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


EnvironmentStage = Enum(
    # [Development]
    # This is the working environment for individual developers or small
    # teams.  Working in isolation with the rest of the tiers, the
    # developer(s) can try radical changes to the code without adversely
    # affecting the rest of the development team.
    'dev',

    # [Integration]
    # A common environment where all developers commit code changes.  The
    # goal of this environment is to combine and validate the work of the
    # entire project team so it can be tested before being promoted to the
    # Staging Environment.  It is possible for Development and Integration
    # to be the same environment (as in the case where the developer does
    # not use a local copy of the source code).
    'int',

    # [Staging]
    # The staging tier is a environment that is as identical to the
    # production environment as possible.  The purpose of the Staging
    # environment is to simulate as much of the Production environment as
    # possible.  The Staging environment can also double as a
    # Demonstration/Training environment.
    'stg',

    # [Production]
    # The production tier might include a single machine or a huge cluster
    # comprising many machines.
    'prod',
)
