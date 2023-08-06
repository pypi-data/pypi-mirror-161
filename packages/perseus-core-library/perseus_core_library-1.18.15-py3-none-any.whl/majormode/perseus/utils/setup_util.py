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

import io
import os
import pipfile

from majormode.perseus.model.version import Version


# The default name of the `README.md` file.
DEFAULT_README_FILE_NAME = 'README.md'


def get_requirements() -> list[str]:
    """
    Return the list of 3rd party libraries declared in the PIP file.


    @return: A list of package names.
    """
    pip_file = pipfile.load()
    requirements = [
        package_name
        for package_name, package_version in pip_file.data['default'].items()
    ]
    return requirements


def read_file(file_path_name: str) -> str:
    """
    Read a given file.


    @param file_path_name: The absolute path and name of a file.


    @return: The content of the file.
    """
    with io.open(file_path_name, mode='rt', encoding='utf-8') as fd:
        return fd.read()


def read_readme_file(path: str, file_name: str = None) -> str:
    """
    Read the README.md file.

    @param path: The absolute path of the `README.md` file

    @param file_name: The alternate name of the `README.md` file.  It
        defaults to {@link DEFAULT_README_FILE_NAME}.

    @return:
    """
    return read_file(os.path.join(path, file_name or DEFAULT_README_FILE_NAME))


def read_version_file(path: str, file_name: str = None) -> Version:
    """
    Return the version written in a given file.


    @param path: The absolute path of the version file.

    @param file_name: The alternate name of the file where the version is written in.
        It defaults to {@link Version.DEFAULT_VERSION_FILE_NAME}.


    @return: An object {@link Version}.
    """
    return Version.from_file(path, file_name=file_name)
