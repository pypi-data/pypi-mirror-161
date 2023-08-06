# Copyright (C) 2021 Majormode.  All rights reserved.
#
# This software is the confidential and proprietary information of
# Majormode or one of its subsidiaries.  You shall not disclose this
# confidential information and shall use it only in accordance with the
# terms of the license agreement or other applicable agreement you
# entered into with Majormode.
#
# MAJORMODE MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY
# OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT.  MAJORMODE SHALL NOT BE LIABLE FOR ANY
# LOSSES OR DAMAGES SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING
# OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

from majormode.perseus.model.enum import Enum


# Code name of the supported mobile device platforms.
DevicePlatform = Enum(
    'ios',
    'android'
)

NotificationMode = Enum(
    # Indicate that a notification message is delivered to the specified
    # recipients when the request for the transmission of information is
    # initiated by the receiver or client application, and then is
    # responded by the publisher or server platform.
    'pull',

    # Indicate that a notification message is delivered to the specified
    # recipients when the request for the transmission of information is
    # initiated by the publisher or server platform and pushed out to the
    # receiver or client application.
    'push'
)
