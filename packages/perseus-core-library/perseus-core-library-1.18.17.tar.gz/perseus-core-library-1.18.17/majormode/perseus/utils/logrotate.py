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

import errno
import gzip
import os
import zipfile

try:
    import bz2
except ImportError as error:
    bz2 = None

from logging.handlers import RotatingFileHandler
#try:
#    from cloghandler import ConcurrentRotatingFileHandler as RotatingFileHandler
#except ImportError:
#    warn(__file__)
#    warn("ConcurrentLogHandler package not installed; using built-in log handler")
#    from logging.handlers import RotatingFileHandler


class RotatingFileHandlerEx(RotatingFileHandler):
    """
    Provides an additional log handler for Python's standard logging
    package (PEP 282).  This handler will write log events to log file
    which is rotated when the log file reaches a certain size.  The log
    file will be compressed.  Multiple processes can safely write to the
    same log file concurrently.
    """
    def __init__(self, path, maxBytes, backupCount,
            compression='gzip'):
        """
        Build a new instance of the ``RotatingFileHandlerEx`` class.


        @param path: absolute path name where the rotating log file will be
            written into.

        @param maxBytes: maximum number of bytes to be written before rolling
            over the current log file, compressing it, and creating a new log
            file.

        @param backupCount: if non-zero, the system will save old log files by
            appending the extensions ``.1``, ``.2`` etc., to the filename.  For
            example, with a ``backupCount`` of ``5`` and a base file name of
            ``app.log``, the logger generates ``app.log``, ``app.log.1``,
            ``app.log.2``, up to ``app.log.5``.  The file being written to is
            always ``app.log``.  When this file is filled, it is closed and
            renamed to ``app.log.1``, and if files ``app.log.1``, ``app.log.2``,
            etc. exist, then they are renamed to ``app.log.2``, ``app.log.3``,
            etc. respectively.

        @param compression: indicate which compression has to be used:

            * ``none``: NoneCompressor

            * ``zip``: ZipCompressor

            * ``gzip``: GzipCompressor

            * ``bzip2``: Bzip2Compressor
        """
        print('[INFO] Writing logs into %s (%d MB, %d files)' % (path, maxBytes / 1024 / 1024, backupCount))

        filename = os.path.abspath(path)
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise exception

        super(self.__class__, self).__init__(
            filename, mode='a', maxBytes=maxBytes, backupCount=backupCount)
        self.baseFilename = filename
        self.compressor = get_compressor(compression)

    def doRollover(self):
        self.stream.close()
        if self.backupCount > 0:
            file_pattern = self.compressor.file_pattern
            for i in range(self.backupCount - 1, 0, -1):
                sfn = file_pattern % (self.baseFilename, i)
                dfn = file_pattern % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            self.compressor.compress(self.baseFilename)
        self.stream = open(self.baseFilename, "w")

    def reopen(self):
        self.close()
        self.stream = open(self.baseFilename, 'a')


class NoneCompressor(object):
    file_pattern = '%s.%d'

    def __init__(self):
        pass
        # warn("[WARNING] Using no compression for logging.")

    def compress(self, filename):
        dfn = filename + '.1'
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(filename, dfn)


class ZipCompressor(object):
    file_pattern = '%s.%d.zip'

    def compress(self, filename):
        dfn = filename + '.1.zip'
        if os.path.exists(dfn):
            os.remove(dfn)
        zf = zipfile.ZipFile(dfn, 'w', zipfile.ZIP_DEFLATED)
        zf.write(filename, os.path.basename(filename))
        zf.close()
        os.remove(filename)


class GzipCompressor(object):
    file_pattern = '%s.%d.gz'

    def compress(self, filename):
        dfn = filename + '.1.gz'
        if os.path.exists(dfn):
            os.remove(dfn)
        zf = gzip.GzipFile(dfn, 'wb')
        zf.write(open(filename, 'rb').read())
        zf.close()
        os.remove(filename)


if bz2:
    class Bzip2Compressor(object):
        file_pattern = '%s.%d.bz2'

        def compress(self, filename):
            dfn = filename + '.1.bz2'
            if os.path.exists(dfn):
                os.remove(dfn)
            zf = bz2.BZ2File(dfn, 'w')
            zf.write(open(filename, 'rb').read())
            zf.close()
            os.remove(filename)
else:
    Bzip2Compressor = NoneCompressor


def get_compressor(compression):
    # { compression mode: compressor class, ...}
    compressors = {
        'none': NoneCompressor,
        'zip': ZipCompressor,
        'gzip': GzipCompressor,
        'bzip2': Bzip2Compressor
    }

    klass = compressors.get(compression, NoneCompressor)
    return klass()
