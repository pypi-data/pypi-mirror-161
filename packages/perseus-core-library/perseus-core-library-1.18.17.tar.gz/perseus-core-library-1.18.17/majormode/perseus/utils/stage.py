# Copyright (C) 2020 Majormode.  All rights reserved.
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

import os

from majormode.perseus.constant.stage import EnvironmentStage
from majormode.perseus.utils import cast


# List of the standard environment stages.
DEFAULT_ENVIRONMENT_STAGES = [
    EnvironmentStage.dev,
    EnvironmentStage.int,
    EnvironmentStage.stg,
    EnvironmentStage.prod,
]


def detect_environment_stage(
        root_path,
        environment_stages=None,
        default_stage=EnvironmentStage.dev):
    """
    Return the environment stage where this server software application
    has been deployed into.

    By convention, the deployment path of a server software application
    MUST respect the following file system hierarchy::

        /srv/<project>/<env>/<version>/


    :param root_path: Absolute path where the server software application
        is deployed in.

    :param environment_stages: A list of items of the enumeration
        `EnvironmentStage`.

    :param default_stage: An item of the enumeration `EnvironmentStage`
        corresponding to the default environment stage to return when the
        deployment path of the server software application doesn't
        respect the expected file system hierarchy.


    :return: An item of the enumeration `EnvironmentStage` referring to
        the environment stage where the server software application has
        been deployed into.
    """
    if environment_stages is None:
        environment_stages = DEFAULT_ENVIRONMENT_STAGES

    environment_stage_str = os.path.basename(os.path.dirname(os.path.realpath(os.path.join(root_path, '..'))))
    try:
        environment_stage = cast.string_to_enum(environment_stage_str, EnvironmentStage)
    except ValueError:
        environment_stage = cast.string_to_enum(
            input(f"Enter environment stage ({', '.join([str(s) for s in environment_stages])}): "),
            EnvironmentStage)

    return environment_stage
