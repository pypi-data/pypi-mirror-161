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
"""module defining utils for an edf volume"""


__authors__ = ["H. Payno", "P. Paleo"]
__license__ = "MIT"
__date__ = "27/01/2022"


from typing import Optional
from tomoscan.scanbase import TomoScanBase
from tomoscan.esrf.volume.singleframebase import VolumeSingleFrameBase
from tomoscan.esrf.identifier.edfidentifier import EDFVolumeIdentifier
import numpy
from silx.io.url import DataUrl
from tomoscan.utils import docstring
import fabio
import os


class EDFVolume(VolumeSingleFrameBase):
    """
    Save volume data to single frame edf and metadata to .txt files

    :warning: each file saved under {volume_basename}_{index_zfill4}.edf is considered to be a slice of the volume.
    """

    DEFAULT_DATA_SCHEME = "fabio"

    DEFAULT_DATA_EXTENSION = "edf"

    def __init__(
        self,
        folder: Optional[str] = None,
        volume_basename: Optional[str] = None,
        data: Optional[numpy.ndarray] = None,
        source_scan: Optional[TomoScanBase] = None,
        metadata: Optional[dict] = None,
        data_url: Optional[DataUrl] = None,
        metadata_url: Optional[DataUrl] = None,
        overwrite: bool = False,
        header: Optional[dict] = None,
        start_index=0,
        data_extension=DEFAULT_DATA_EXTENSION,
        metadata_extension=VolumeSingleFrameBase.DEFAULT_METADATA_EXTENSION,
    ) -> None:
        if folder is not None:
            url = DataUrl(
                file_path=str(folder),
                data_path=None,
            )
        else:
            url = None
        super().__init__(
            volume_basename=volume_basename,
            url=url,
            data=data,
            source_scan=source_scan,
            metadata=metadata,
            data_url=data_url,
            metadata_url=metadata_url,
            overwrite=overwrite,
            start_index=start_index,
            data_extension=data_extension,
            metadata_extension=metadata_extension,
        )

        self._header = header

    @property
    def header(self) -> Optional[dict]:
        """possible header for the edf files"""
        return self._header

    @docstring(VolumeSingleFrameBase)
    def save_frame(self, frame, file_name, scheme):
        if scheme == "fabio":
            header = self.header or {}
            edf_writer = fabio.edfimage.EdfImage(
                data=frame,
                header=header,
            )
            parent_dir = os.path.dirname(file_name)
            if parent_dir != "":
                os.makedirs(parent_dir, exist_ok=True)
            edf_writer.write(file_name)
        else:
            raise ValueError(f"scheme {scheme} is not handled")

    @docstring(VolumeSingleFrameBase)
    def load_frame(self, file_name, scheme):
        if scheme == "fabio":
            return fabio.open(file_name).data
        else:
            raise ValueError(f"scheme {scheme} is not handled")

    @staticmethod
    @docstring(VolumeSingleFrameBase)
    def from_identifier(identifier):
        """Return the Dataset from a identifier"""
        if not isinstance(identifier, EDFVolumeIdentifier):
            raise TypeError(
                f"identifier should be an instance of {EDFVolumeIdentifier}"
            )
        return EDFVolume(
            folder=identifier.folder,
            volume_basename=identifier.file_prefix,
        )

    @docstring(VolumeSingleFrameBase)
    def get_identifier(self) -> EDFVolumeIdentifier:
        if self.url is None:
            raise ValueError("no file_path provided. Cannot provide an identifier")
        return EDFVolumeIdentifier(
            object=self, folder=self.url.file_path(), file_prefix=self._volume_basename
        )

    @staticmethod
    def example_defined_from_str_identifier() -> str:
        return " ; ".join(
            [
                f"{EDFVolume(folder='/path/to/my/my_folder').get_identifier().to_str()}",
                f"{EDFVolume(folder='/path/to/my/my_folder', volume_basename='mybasename').get_identifier().to_str()} (if mybasename != folder name)",
            ]
        )
