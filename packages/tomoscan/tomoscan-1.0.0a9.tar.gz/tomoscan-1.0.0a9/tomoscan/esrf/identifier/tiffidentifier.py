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
__date__ = "01/02/2022"


from tomoscan.esrf.identifier.folderidentifier import (
    BaseFolderAndfilePrefixIdentifierMixIn,
)
from tomoscan.identifier import VolumeIdentifier
import os
from tomoscan.utils import docstring


class TIFFVolumeIdentifier(BaseFolderAndfilePrefixIdentifierMixIn, VolumeIdentifier):
    """Identifier specific to (single frame) tiff volume"""

    @property
    @docstring(VolumeIdentifier)
    def scheme(self) -> str:
        return "tiff"

    @staticmethod
    def from_str(identifier):
        from tomoscan.esrf.volume.tiffvolume import TIFFVolume

        return (
            BaseFolderAndfilePrefixIdentifierMixIn._from_str_to_single_frame_identifier(
                identifier=identifier,
                SingleFrameIdentifierClass=TIFFVolumeIdentifier,
                ObjClass=TIFFVolume,
            )
        )


class MultiTiffVolumeIdentifier(VolumeIdentifier):
    def __init__(self, object, tiff_file):
        super().__init__(object)
        self._file_path = os.path.realpath(os.path.abspath(tiff_file))

    @docstring(VolumeIdentifier)
    def short_description(self) -> str:
        return f"{self.scheme}:{self.tomo_type}:{os.path.basename(self._file_path)}"

    @property
    def file_path(self):
        return self._file_path

    @property
    @docstring(VolumeIdentifier)
    def scheme(self) -> str:
        return "tiff3d"

    def __str__(self):
        return f"{self.scheme}:{self.tomo_type}:{self._file_path}"

    def __eq__(self, other):
        if isinstance(other, MultiTiffVolumeIdentifier):
            return (
                self.tomo_type == other.tomo_type
                and self._file_path == other._file_path
            )
        else:
            return super().__eq__(other)

    def __hash__(self):
        return hash((self._file_path, self._data_path))

    @staticmethod
    def from_str(identifier):
        identifier_no_scheme = identifier.split(":")[-1]
        # TODO: check tomo_type ?
        tiff_file = identifier_no_scheme
        from tomoscan.esrf.volume.tiffvolume import TIFFVolume

        return MultiTiffVolumeIdentifier(object=TIFFVolume, tiff_file=tiff_file)
