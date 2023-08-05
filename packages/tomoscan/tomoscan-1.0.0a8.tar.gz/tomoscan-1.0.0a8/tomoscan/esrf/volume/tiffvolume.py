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
"""module defining utils for a tiff volume"""


__authors__ = ["H. Payno", "P. Paleo"]
__license__ = "MIT"
__date__ = "01/02/2022"


from typing import Optional
import numpy
from tomoscan.esrf.identifier.tiffidentifier import (
    MultiTiffVolumeIdentifier,
    TIFFVolumeIdentifier,
)
from tomoscan.scanbase import TomoScanBase
from tomoscan.esrf.volume.singleframebase import VolumeSingleFrameBase
from tomoscan.utils import docstring
from silx.io.url import DataUrl
from silx.io.dictdump import dicttoini, load as load_ini
import os
from tomoscan.volumebase import VolumeBase

try:
    import tifffile  # noqa #F401 needed for later possible lazy loading
except ImportError:
    has_tifffile = False
else:
    has_tifffile = True
    from tifffile import TiffWriter

import logging

_logger = logging.getLogger(__name__)


def check_has_tiffle_file(handle_mode: str):
    assert handle_mode in ("warning", "raises")

    if not has_tifffile:
        message = "Unable to import `tifffile`. Unable to load or save tiff file. You can use pip to install it"
        if handle_mode == "message":
            _logger.warning(message)
        elif handle_mode == "raises":
            raise ValueError(message)


class TIFFVolume(VolumeSingleFrameBase):
    """
    Save volume data to single frame tiff and metadata to .txt files

    :warning: each file saved under {volume_basename}_{index_zfill4}.tiff is considered to be a slice of the volume.
    """

    DEFAULT_DATA_EXTENSION = "tiff"

    DEFAULT_DATA_SCHEME = "tifffile"

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
            url=url,
            volume_basename=volume_basename,
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

        check_has_tiffle_file("warning")

    @property
    def header(self) -> Optional[dict]:
        """possible header for the edf files"""
        return self._header

    @docstring(VolumeSingleFrameBase)
    def save_frame(self, frame, file_name, scheme):
        check_has_tiffle_file("raises")
        if scheme == "tifffile":
            tiff_writer = TiffWriter(file_name)
            tiff_writer.write(frame)
        else:
            raise ValueError(f"scheme {scheme} is not handled")

    @docstring(VolumeSingleFrameBase)
    def load_frame(self, file_name, scheme) -> numpy.ndarray:
        check_has_tiffle_file("raises")
        if scheme == "tifffile":
            return tifffile.imread(file_name)
        else:
            raise ValueError(f"scheme {scheme} is not handled")

    # identifier section

    @staticmethod
    @docstring(VolumeSingleFrameBase)
    def from_identifier(identifier):
        """Return the Dataset from a identifier"""
        if not isinstance(identifier, TIFFVolumeIdentifier):
            raise TypeError(
                f"identifier should be an instance of {TIFFVolumeIdentifier} not {type(identifier)}"
            )
        return TIFFVolume(
            folder=identifier.folder,
            volume_basename=identifier.file_prefix,
        )

    @docstring(VolumeSingleFrameBase)
    def get_identifier(self) -> TIFFVolumeIdentifier:
        if self.url is None:
            raise ValueError("no file_path provided. Cannot provide an identifier")
        return TIFFVolumeIdentifier(
            object=self, folder=self.url.file_path(), file_prefix=self._volume_basename
        )

    @staticmethod
    def example_defined_from_str_identifier() -> str:
        return " ; ".join(
            [
                f"{TIFFVolume(folder='/path/to/my/my_folder').get_identifier().to_str()}",
                f"{TIFFVolume(folder='/path/to/my/my_folder', volume_basename='mybasename').get_identifier().to_str()} (if mybasename != folder name)",
            ]
        )


class MultiTIFFVolume(VolumeBase):
    """
    Save tiff into a single tiff file

    :param str file_path: path to the multiframe tiff file
    """

    def __init__(
        self,
        file_path: Optional[str] = None,
        data: Optional[numpy.ndarray] = None,
        source_scan: Optional[TomoScanBase] = None,
        metadata: Optional[dict] = None,
        data_url: Optional[DataUrl] = None,
        metadata_url: Optional[DataUrl] = None,
        overwrite: bool = False,
        append: bool = False,
    ) -> None:
        if file_path is not None:
            url = DataUrl(file_path=file_path)
        else:
            url = None
        super().__init__(
            url, data, source_scan, metadata, data_url, metadata_url, overwrite
        )
        check_has_tiffle_file("warning")
        self.append = append

    @docstring(VolumeBase)
    def deduce_data_and_metadata_urls(self, url: Optional[DataUrl]) -> tuple:
        # convention for tiff multiframe:
        # expect the url to provide a path to a the tiff multiframe file. so data_url will be the same as url
        # and the metadata_url will target a prefix_info.txt file with prefix is the tiff file prefix

        if url is None:
            return None, None
        else:
            if url.data_slice() is not None:
                raise ValueError(f"data_slice is not handled by the {MultiTIFFVolume}")
            file_path = url.file_path()
            if url.data_path() is not None:
                raise ValueError("data_path is not handled")

            scheme = url.scheme() or "tifffile"
            metadata_file = "_".join([os.path.splitext(file_path)[0], "infos.txt"])
            return (
                # data url
                DataUrl(
                    file_path=url.file_path(),
                    scheme=scheme,
                ),
                # medata url
                DataUrl(
                    file_path=metadata_file,
                    scheme="ini",
                ),
            )

    @docstring(VolumeBase)
    def save_data(self, url: Optional[DataUrl] = None) -> None:
        """
        :raises KeyError: if data path already exists and overwrite set to False
        :raises ValueError: if data is None
        """
        # to be discussed. Not sure we should raise an error in this case. Could be usefull but this could also be double edged knife
        if self.data is None:
            raise ValueError("No data to be saved")
        check_has_tiffle_file("raises")

        url = url or self.data_url
        if url is None:
            raise ValueError(
                "Cannot get data_url. An url should be provided. Don't know where to save this."
            )

        if url.scheme() == "tifffile":
            if url.data_path() is not None:
                raise ValueError("No data path expected. Unagleto save data")
            else:
                _logger.info(f"save data to {url.path()}")

            with TiffWriter(url.file_path(), bigtiff=True, append=self.append) as tif:
                tif.write(self.data)
        else:
            raise ValueError(f"Scheme {url.scheme()} is not handled")

    @docstring(VolumeBase)
    def save_metadata(self, url: Optional[DataUrl] = None) -> None:
        """
        :raises KeyError: if data path already exists and overwrite set to False
        :raises ValueError: if data is None
        """
        if self.metadata is None:
            raise ValueError("No metadata to be saved")
        check_has_tiffle_file("raises")

        url = url or self.metadata_url
        if url is None:
            raise ValueError(
                "Cannot get metadata_url. An url should be provided. Don't know where to save this."
            )
        _logger.info(f"save metadata to {url.path()}")
        if url.scheme() == "ini":
            if url.data_path() is not None:
                raise ValueError("data_path is not handled by 'ini' scheme")
            else:
                dicttoini(
                    self.metadata,
                    url.file_path(),
                )
        else:
            raise ValueError(f"Scheme {url.scheme()} is not handled by multiframe tiff")

    @docstring(VolumeBase)
    def load_data(
        self, url: Optional[DataUrl] = None, store: bool = True
    ) -> numpy.ndarray:
        url = url or self.data_url
        if url is None:
            raise ValueError(
                "Cannot get data_url. An url should be provided. Don't know where to save this."
            )

        if url.scheme() == "tifffile":
            if url.data_path() is not None:
                raise ValueError("data_path is not handle by multiframe tiff")
            data = tifffile.imread(url.file_path())
        else:
            raise ValueError(f"Scheme {url.scheme()} is not handled by multiframe tiff")

        if store:
            self.data = data

        return data

    @docstring(VolumeBase)
    def load_metadata(self, url: Optional[DataUrl] = None, store: bool = True) -> dict:
        url = url or self.metadata_url
        if url is None:
            raise ValueError(
                "Cannot get metadata_url. An url should be provided. Don't know where to save this."
            )

        if url.scheme() == "ini":
            metadata_file = url.file_path()
            if url.data_path() is not None:
                raise ValueError("data_path is not handled by ini scheme")
            else:
                try:
                    metadata = load_ini(metadata_file, "ini")
                except FileNotFoundError:
                    _logger.warning(f"unable to load metadata from {metadata_file}")
                    metadata = {}
        else:
            raise ValueError(f"Scheme {url.scheme()} is not handled by multiframe tiff")

        if store:
            self.metadata = metadata
        return metadata

    @staticmethod
    @docstring(VolumeBase)
    def from_identifier(identifier):
        """Return the Dataset from a identifier"""
        if not isinstance(identifier, MultiTiffVolumeIdentifier):
            raise TypeError(
                f"identifier should be an instance of {MultiTiffVolumeIdentifier}"
            )
        return MultiTIFFVolume(
            file_path=identifier.file_path,
        )

    @docstring(VolumeBase)
    def get_identifier(self) -> MultiTiffVolumeIdentifier:
        if self.url is None:
            raise ValueError("no file_path provided. Cannot provide an identifier")
        return MultiTiffVolumeIdentifier(object=self, tiff_file=self.url.file_path())

    def browse_metadata_files(self, url=None):
        """
        return a generator go through all the existings files associated to the data volume
        """
        url = url or self.metadata_url
        if url is None:
            return
        elif url.file_path() is not None and os.path.exists(url.file_path()):
            yield url.file_path()

    def browse_data_files(self, url=None):
        """
        return a generator go through all the existings files associated to the data volume
        """
        url = url or self.data_url
        if url is None:
            return
        elif url.file_path() is not None and os.path.exists(url.file_path()):
            yield url.file_path()

    def browse_data_urls(self, url=None):
        url = url or self.data_url
        for data_file in self.browse_data_files(url=url):
            yield DataUrl(
                file_path=data_file,
                scheme=url.scheme(),
            )

    @staticmethod
    def example_defined_from_str_identifier() -> str:
        return (
            MultiTIFFVolume(file_path="/path/to/tiff_file.tif")
            .get_identifier()
            .to_str()
        )
