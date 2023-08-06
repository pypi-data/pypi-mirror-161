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

import importlib
import sys


def load_module(module_package_name):
    """
    Load the specified Python module specified by a string representation.


    :note: The function prevents from circular import.


    :param module_package_name: Sstring representation of the Python
        packaged module (module namespace) using "dotted module names",
        e.g., ``foo.bar``.


    :return: An object of the specified module.
    """
    return sys.modules.get(module_package_name) or importlib.import_module(module_package_name)


def load_class(class_module_package_name):
    """
    Dynamically load a Python class specified by the string representation
    of this class in a Python packaged module (module namespace).


    :note: The function prevents from circular import.


    :param class_module_package_name: A string representation of the class
        to load using "dotted module names", e.g., ``foo.bar.MyClass``.


    :return: an instance of the specified class.
    """
    module_package_name, class_name = class_module_package_name.rsplit('.', 1)

    return getattr(load_module(module_package_name), class_name)
