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

import codecs
import contextlib
import errno
import hashlib
import os
import platform
import shutil
import sys


def build_tree_pathname(filename, directory_depth=8, pathname_separator_character=os.sep):
    """
    Return a pathname built of the specified number of sub-directories,
    and where each directory is named after the nth letter of the filename
    corresponding to the directory depth.

    Examples::

      >>> build_tree_pathname('foo.txt', 2, '/')
      'f/o/'
      >>> build_tree_pathname('0123456789abcdef')
      '0/1/2/3/4/5/6/7/'


    :param filename: name of a file, with or without extension.

    :param directory_depth: number of sub-directories to be generated.

    :param pathname_separator_character: character to be used to separate
        pathname components, such as '/' for POSIX and '\\' for Windows.
        If not defined, the default is the character used by the operating
        system ``os.sep``.


    :return: a file pathname.
    """
    filename_without_extension, _file_extension_ = os.path.splitext(filename)
    max_depth = min(directory_depth, len(filename_without_extension))

    pathname = os.path.join(*[
        c
        for c in filename_without_extension[:max_depth]
    ])

    return pathname


def build_tree_file_pathname(filename, directory_depth=8, pathname_separator_character=os.sep):
    """
    Return a file pathname which pathname is built of the specified
    number of sub-directories, and where each directory is named after the
    nth letter of the filename corresponding to the directory depth.

    Examples::

    ```python
    >>> build_tree_file_pathname('foo.txt', 2, '/')
    'f/o/foo.txt'
    >>> build_tree_file_pathname('0123456789abcdef')
    '0/1/2/3/4/5/6/7/0123456789abcdef'
    ```


    :param filename: name of a file, with or without extension.

    :param directory_depth: number of sub-directories to be generated.

    :param pathname_separator_character: character to be used to separate
        pathname components, such as '/' for POSIX and '\\' for Windows.
        If not defined, the default is the character used by the operating
        system ``os.sep``.


    :return: a file pathname.
    """
    return build_tree_pathname(filename, directory_depth, pathname_separator_character) + filename


def find_root_path(absolute_path, relative_path):
    """
    Return the root path of a path relative to an absolute path.


    :param absolute_path: an absolute path that is ended by the specified
        relative path.

    :param relative_path: a relative path that ends the specified absolute
        path.


    :return: the root path of the relative path.
    """
    _absolute_path = os.path.normpath(absolute_path)
    _relative_path = os.path.normpath(relative_path)

    index = _absolute_path.rfind(_relative_path)
    if index == -1 or len(_relative_path) + index < len(_absolute_path):
        raise ValueError('The relative path does not end the specified absolute path')

    return _absolute_path[:index]


def get_file_checksum(file_path_name, hash_algorithm_name='md5'):
    """
    Generate the MD5 checksum of the specified file.


    :param file_path_name: the absolute path and name of the file to
        generate its MD5 checksum.

    :param hash_algorithm_name: specify the hash algorithm to use.  Refer
        to ``hashlib.algorithms`` to get the names of the hash algorithms
        guaranteed to be supported by this module.


    :return: hash digest returned as a string of double length, containing
        only hexadecimal digits.  This may be used to exchange the value
        safely in email or other non-binary environments.


    :note: the file can not be entirely read to memory, but it needs to
        be read by chunks of memory that will be freed after each
        iteration.  What's important to notice is that the file  must be
        opened in binary mode.  The function breaks the file into chunks
        using block size of any multiple of 128 (say 8192, 32768, etc.)
        and its feed them to MD5 consecutively using ``update()``.  This
        takes advantage advantage of the fact that MD5 has 128-byte digest
        blocks.  The function actually uses a block size that depends on the block
        size of the filesystem to avoid performances issues.

    :note: The ``F_FRSIZE`` value is the actual minimum allocation unit
        of the filesystem, while the ``F_BSIZE`` is the block size that
        would lead to most efficient use of the disk with io calls.
    """
    hash_algorithm = hashlib.new(hash_algorithm_name)

    if sys.platform == "win32":
        import ctypes

        sectors_per_cluster = ctypes.c_ulonglong(0)
        bytes_per_sector = ctypes.c_ulonglong(0)
        root_path_name = ctypes.c_wchar_p(u"C:\\")

        ctypes.windll.kernel32.GetDiskFreeSpaceW(
            root_path_name,
            ctypes.pointer(sectors_per_cluster),
            ctypes.pointer(bytes_per_sector),
            None,
            None)

        block_size = bytes_per_sector.value
    else:
        block_size = os.statvfs('/').f_bsize

    with open(file_path_name, 'rb') as handle:
        for chunk in iter(lambda: handle.read(block_size), b''):
            hash_algorithm.update(chunk)

    return hash_algorithm.hexdigest()


def make_directory_if_not_exists(path):
    """
    Create the specified path, making all intermediate-level directories
    needed to contain the leaf directory.  Ignore any error that would
    occur if the leaf directory already exists.


    :note: all the intermediate-level directories are created with the
        default mode is 0777 (octal).


    :param path: the path to create.


    @raise OSError: an error that would occur if the path cannot be
        created.
    """
    try:
        os.makedirs(path)
    except OSError as error:  # Ignore if the directory has been already created.
        if error.errno != errno.EEXIST:
            raise error


def move_file(source_file_pathname, destination_file_pathname):
    """
    Move the the specified file to another location.  If the destination
    already exists, it is replaced silently.

    This function is an alternative to ``shutil.move(src, dst)``, which
    might raise ``OSError`` if the destination already exists.


    :param source_file_pathname: the complete path and name of the file to
        move.

    :param destination_file_pathname: the complete path and name of the
        file once moved.
    """
    if os.path.exists(destination_file_pathname):
        os.remove(destination_file_pathname)

    shutil.move(source_file_pathname, destination_file_pathname)


def remove_file_if_exists(file_pathname):
    """
    Remove the file path, if it exists.


    :param file_pathname: path and file name the refers to the file.
    """
    try:
        os.remove(file_pathname)
    except:
        pass


@contextlib.contextmanager
def smart_open(file_path_name, mode='r', encoding='utf-8'):
    """
    Open an encoded file using the given mode and return a wrapped version
    providing transparent encoding/decoding.  The default file mode is 'r'
    meaning to open the file in read mode.


    :param file_path_name: the absolute path and name of the file to
        open.

    :param mode: indicate how the file is to be opened.  The most commonly-
        used values of mode are 'r' for reading, 'w' for writing
        (truncating the file if it already exists), and 'a' for appending
        (which on some Unix systems means that all writes append to the
        end of the file regardless of the current seek position).  If mode
        is omitted, it defaults to 'r'.

    :param encoding: specify the encoding which is to be used for the
        file.


    :return: an object of the file type.
    """
    if file_path_name and file_path_name != '-':
        file_handle = codecs.open(file_path_name, mode=mode, encoding='utf-8')
    else:
        file_handle = sys.stdout

    try:
        yield file_handle
    finally:
        if file_handle is not sys.stdout:
            file_handle.close()


def which(exe_name):
    """
    Locate a program file in the user's path.


    :param exe_name: name of the executable file.


    :return: ``None`` if the executable has not been found in the user's
        path, or the path for the executable file.
    """
    def is_exe(file_path_name):
        return os.path.isfile(file_path_name) and os.access(file_path_name, os.X_OK)

    is_platform_windows = (platform.system() == 'Windows')

    fpath, _fname = os.path.split(exe_name)
    if fpath:
        if is_exe(exe_name):
            return exe_name
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            exe_file_path_name = os.path.join(path, exe_name)
            if is_exe(exe_file_path_name):
                return exe_file_path_name

            if is_platform_windows:
                windows_exe_file_path_name = '%s.exe' % exe_file_path_name
                if is_exe(windows_exe_file_path_name):
                    return windows_exe_file_path_name

                windows_com_file_path_name = '%s.exe' % exe_file_path_name
                if is_exe(windows_com_file_path_name):
                    return windows_com_file_path_name

    return None
