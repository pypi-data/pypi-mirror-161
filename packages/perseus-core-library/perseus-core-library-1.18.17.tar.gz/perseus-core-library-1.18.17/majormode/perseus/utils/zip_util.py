# Copyright (C) 2015 Majormode.  All rights reserved.
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

import contextlib
import io
import logging
import os
import tempfile
import urllib.request
import zipfile


# Default number of bytes to be fetched at every read operation of the
# ZIP archive file data hosted on a computer network.
DEFAULT_CHUNK_SIZE = 8192


def download_file(
        url,
        chunk_size=DEFAULT_CHUNK_SIZE,
        file_path_name=None,
        memory_mapped=True):
    """
    Return a `ZipFile` instance of a ZIP archive file downloaded from
    the specified Uniform Resource Locator (URL).


    :param url: Uniform Resource Locator that specifies the location of
        the ZIP archive file on a computer network and a mechanism for
        retrieving it.

    :param chunk_size: Maximal number of bytes to be fetched every read
        operation of the ZIP archive file data hosted on the computer
        network.

    :param file_path_name: An absolute path and name of the file in
        which the archive will be stored in.  If not defined, the function
        downloads the archive file in a temporary file created in the most
        secure manner possible; the user is responsible for deleting this
        temporary file when done with it.

    :param memory_mapped: Indicate whether to map the ZIP archive file-
        like object into memory, for performance optimization, or whether
        to store this archive into disk, for memory optimization.
        If the archive is directly stored into disk, the caller is
        responsible for deleting the temporary file when done with it.


    :return: An object `ZipFile` of the remote ZIP archive file if the
        argument `memory_mapped` is set to `True`, or a tuple
        `(file_path_name, zip_file)`.


    :raise urllib.error.URLError: If a connection timed out occurs.
    """
    if memory_mapped:
        fd = io.StringIO()
    else:
        if not file_path_name:
            # Create a temporary file in the most secure manner possible.
            file_descriptor, file_path_name = tempfile.mkstemp()
            fd = os.fdopen(file_descriptor, 'wb')
        else:
            fd = open(file_path_name, 'wb')

    with contextlib.closing(urllib.request.urlopen(url)) as resource_handle:
        while True:
            chunk_data = resource_handle.read(chunk_size)
            if not chunk_data: break
            fd.write(chunk_data)
            logging.debug(f"Downloaded {len(chunk_data)} bytes")

    if memory_mapped:
        fd.seek(0)
    else:
        fd.close()

    zip_file = zipfile.ZipFile(fd if memory_mapped else file_path_name)

    return zip_file if memory_mapped else (zip_file, file_path_name)


def open_entry_file(zip_file, entry_file_name):
    """
    Extract the specified entry from the archive and return it as a file-
    like object.


    :param zip_file: An object `ZipFile`.

    :param entry_file_name: The name of the file in the archive, or a
        `ZipInfo` object.


    :return: A file-like object corresponding to the specified entry.


    :raise KeyError: If the specified entry name is not contained in the
        ZIP archive.
    """
    data = zip_file.read(entry_file_name)

    memory_mapped_file = io.StringIO()
    memory_mapped_file.write(data)
    memory_mapped_file.seek(0)

    return memory_mapped_file
