# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2022 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "10/01/2022"


from urllib.parse import ParseResult, urlparse
from tomoscan.esrf.identifier.url_utils import (
    UrlSettings,
    join_path,
    join_query,
    split_path,
    split_query,
)
from tomoscan.identifier import ScanIdentifier, VolumeIdentifier
import os
from tomoscan.utils import docstring


class _HDF5IdentifierMixIn:
    def __init__(self, object, hdf5_file, entry):
        super().__init__(object)
        self._file_path = os.path.realpath(os.path.abspath(hdf5_file))
        self._data_path = entry

    @docstring(ScanIdentifier)
    def short_description(self) -> str:
        return ParseResult(
            scheme=self.scheme,
            path=join_path(
                (self.tomo_type, os.path.basename(self._file_path)),
            ),
            query=join_query(
                ((UrlSettings.DATA_PATH_KEY, self.data_path),),
            ),
            netloc=None,
            params=None,
            fragment=None,
        ).geturl()

    @property
    def file_path(self):
        return self._file_path

    @property
    def data_path(self):
        return self._data_path

    @property
    @docstring(ScanIdentifier)
    def scheme(self) -> str:
        return "hdf5"

    def __str__(self):
        return ParseResult(
            scheme=self.scheme,
            path=join_path(
                (self.tomo_type, self._file_path),
            ),
            query=join_query(
                ((UrlSettings.DATA_PATH_KEY, self.data_path),),
            ),
            netloc=None,
            params=None,
            fragment=None,
        ).geturl()

    def __eq__(self, other):
        if isinstance(other, HDF5TomoScanIdentifier):
            return (
                self.tomo_type == other.tomo_type
                and self._file_path == other._file_path
                and self._data_path == other._data_path
            )
        else:
            return super().__eq__(other)

    def __hash__(self):
        return hash((self._file_path, self._data_path))


class HDF5TomoScanIdentifier(_HDF5IdentifierMixIn, ScanIdentifier):
    @staticmethod
    def from_str(identifier):
        info = urlparse(identifier)
        paths = split_path(info.path)
        if len(paths) == 1:
            hdf5_file = paths[0]
            tomo_type = None
        elif len(paths) == 2:
            tomo_type, hdf5_file = paths
        else:
            raise ValueError("Failed to parse path string:", info.path)
        if tomo_type is not None and tomo_type != HDF5TomoScanIdentifier.TOMO_TYPE:
            raise TypeError(
                f"provided identifier fits {tomo_type} and not {HDF5TomoScanIdentifier.TOMO_TYPE}"
            )

        queries = split_query(info.query)
        entry = queries.get(UrlSettings.DATA_PATH_KEY, None)
        if entry is None:
            raise ValueError(f"expects to get {UrlSettings.DATA_PATH_KEY} query")
        from tomoscan.esrf.scan.hdf5scan import HDF5TomoScan

        return HDF5TomoScanIdentifier(
            object=HDF5TomoScan, hdf5_file=hdf5_file, entry=entry
        )


class HDF5VolumeIdentifier(_HDF5IdentifierMixIn, VolumeIdentifier):
    @staticmethod
    def from_str(identifier):
        info = urlparse(identifier)
        paths = split_path(info.path)
        if len(paths) == 1:
            hdf5_file = paths[0]
            tomo_type = None
        elif len(paths) == 2:
            tomo_type, hdf5_file = paths
        else:
            raise ValueError("Failed to parse path string:", info.path)
        if tomo_type is not None and tomo_type != VolumeIdentifier.TOMO_TYPE:
            raise TypeError(
                f"provided identifier fits {tomo_type} and not {VolumeIdentifier.TOMO_TYPE}"
            )

        queries = split_query(info.query)
        entry = queries.get(UrlSettings.DATA_PATH_KEY, None)
        if entry is None:
            raise ValueError("expects to get a data_path")
        from tomoscan.esrf.volume.hdf5volume import HDF5Volume

        return HDF5VolumeIdentifier(object=HDF5Volume, hdf5_file=hdf5_file, entry=entry)
