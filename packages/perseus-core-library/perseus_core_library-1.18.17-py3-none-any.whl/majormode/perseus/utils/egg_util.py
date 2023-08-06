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

import os
import re
import sys


REGEX_EGG_PACKAGE_PATH = re.compile(r'^.+[.]egg$')


def find_module_egg_path(module_path):
    """
    Find the path of the deployed egg package that may contain the
    specified module path.


    :param module_path: the path of a Python module.


    :return: the absolute path of the deployed egg package that contains
        the specified module path, or `None` if no deployed egg package
        contains this module path.
    """
    if module_path.find('.egg') == -1:
        return None

    module_absolute_path = os.path.abspath(module_path)

    egg_paths = [
        os.path.relpath(module_absolute_path, egg_path)
        for egg_path in [
            egg_path for egg_path in sys.path
            if REGEX_EGG_PACKAGE_PATH.match(egg_path) and module_absolute_path.startswith(egg_path)]]

    return None if len(egg_paths) == 0 else egg_paths[0]
