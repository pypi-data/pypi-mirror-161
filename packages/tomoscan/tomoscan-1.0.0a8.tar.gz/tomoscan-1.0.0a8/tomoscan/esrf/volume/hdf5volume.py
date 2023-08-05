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
"""module defining utils for an hdf5 volume"""


__authors__ = ["H. Payno", "P. Paleo"]
__license__ = "MIT"
__date__ = "27/01/2022"


import os
from typing import Optional
from tomoscan.scanbase import TomoScanBase
from tomoscan.volumebase import VolumeBase
from tomoscan.esrf.identifier.hdf5Identifier import HDF5VolumeIdentifier
from silx.io.url import DataUrl
from tomoscan.utils import docstring
from tomoscan.io import HDF5File
from silx.io.dictdump import dicttonx, nxtodict
import numpy
import logging
import h5py

_logger = logging.getLogger(__name__)


class HDF5Volume(VolumeBase):
    """
    Volume where both data and metadata are store in a HDF5 file but at a different location.
    """

    DATA_DATASET_NAME = "results/data"
    METADATA_GROUP_NAME = "configuration"

    def __init__(
        self,
        file_path: Optional[str] = None,
        data_path: Optional[str] = None,
        data: Optional[numpy.ndarray] = None,
        source_scan: Optional[TomoScanBase] = None,
        metadata: Optional[dict] = None,
        data_url: Optional[DataUrl] = None,
        metadata_url: Optional[DataUrl] = None,
        overwrite: bool = False,
    ) -> None:
        url = self._get_url_from_file_path_data_path(
            file_path=file_path, data_path=data_path
        )

        self._file_path = file_path
        self._data_path = data_path
        super().__init__(
            url=url,
            data=data,
            source_scan=source_scan,
            metadata=metadata,
            data_url=data_url,
            metadata_url=metadata_url,
            overwrite=overwrite,
        )

    @property
    def data_extension(self):
        if self.data_url is not None and self.data_url.file_path() is not None:
            return os.path.splitext(self.data_url.file_path())[1]

    @property
    def metadata_extension(self):
        if self.metadata_url is not None and self.metadata_url.file_path() is not None:
            return os.path.splitext(self.metadata_url.file_path())[1]

    @staticmethod
    def _get_url_from_file_path_data_path(
        file_path: Optional[str], data_path: Optional[str]
    ) -> Optional[DataUrl]:
        if file_path is not None and data_path is not None:
            return DataUrl(file_path=file_path, data_path=data_path, scheme="silx")
        else:
            return None

    @VolumeBase.data.setter
    def data(self, data):
        if not isinstance(data, (numpy.ndarray, type(None), h5py.VirtualLayout)):
            raise TypeError(
                f"data is expected to be None or a numpy array not {type(data)}"
            )
        if isinstance(data, numpy.ndarray) and data.ndim != 3:
            raise ValueError(f"data is expected to be 3D and not {data.ndim}D.")
        self._data = data

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path: Optional[str]):
        if not (file_path is None or isinstance(file_path, str)):
            raise TypeError
        self._file_path = file_path
        self.url = self._get_url_from_file_path_data_path(
            self.file_path, self.data_path
        )

    @property
    def data_path(self):
        return self._data_path

    @data_path.setter
    def data_path(self, data_path: Optional[str]):
        if not (data_path is None or isinstance(data_path, str)):
            raise TypeError
        self._data_path = data_path
        self.url = self._get_url_from_file_path_data_path(
            self.file_path, self.data_path
        )

    @docstring(VolumeBase)
    def deduce_data_and_metadata_urls(self, url: Optional[DataUrl]) -> tuple:
        if url is None:
            return None, None
        else:
            if url.data_slice() is not None:
                raise ValueError(f"data_slice is not handled by the {HDF5Volume}")
            file_path = url.file_path()
            data_path = url.data_path()
            if data_path is None:
                raise ValueError(
                    "data_path not provided from the DataUrl. Please provide one."
                )
            scheme = url.scheme() or "silx"
            return (
                # data url
                DataUrl(
                    file_path=file_path,
                    data_path="/".join([data_path, self.DATA_DATASET_NAME]),
                    scheme=scheme,
                ),
                # medata url
                DataUrl(
                    file_path=file_path,
                    data_path="/".join([data_path, self.METADATA_GROUP_NAME]),
                    scheme=scheme,
                ),
            )

    @docstring(VolumeBase)
    def save_data(self, url: Optional[DataUrl] = None, mode="a", **kwargs) -> None:
        """
        :raises KeyError: if data path already exists and overwrite set to False
        :raises ValueError: if data is None
        """
        # to be discussed. Not sure we should raise an error in this case. Could be usefull but this could also be double edged knife
        if self.data is None:
            raise ValueError("No data to be saved")
        url = url or self.data_url
        if url is None:
            raise ValueError(
                "Cannot get data_url. An url should be provided. Don't know where to save this."
            )
        else:
            _logger.info(f"save data to {url.path()}")

        if url.file_path() is not None and os.path.dirname(url.file_path()) != "":
            os.makedirs(os.path.dirname(url.file_path()), exist_ok=True)
        with HDF5File(filename=url.file_path(), mode=mode) as h5s:
            if url.data_path() in h5s:
                if self.overwrite:
                    _logger.debug(
                        f"overwrite requested. Will remove {url.data_path()} entry"
                    )
                    del h5s[url.data_path()]
                else:
                    raise OSError(
                        f"Unable to save data to {url.data_path()}. This path already exists in {url.file_path()}. If you want you can ask to overwrite it."
                    )
            if isinstance(self.data, h5py.VirtualLayout):
                h5s.create_virtual_dataset(name=url.data_path(), layout=self.data)
            else:
                h5s.create_dataset(url.data_path(), data=self.data, **kwargs)

    @docstring(VolumeBase)
    def save_metadata(self, url: Optional[DataUrl] = None) -> None:
        """
        :raises KeyError: if data path already exists and overwrite set to False
        :raises ValueError: if data is None
        """
        if self.metadata is None:
            raise ValueError("No metadata to be saved")
        url = url or self.metadata_url
        if url is None:
            raise ValueError(
                "Cannot get metadata_url. An url should be provided. Don't know where to save this."
            )
        else:
            _logger.info(f"save metadata to {url.path()}")

        if url.file_path() is not None and os.path.dirname(url.file_path()) != "":
            os.makedirs(os.path.dirname(url.file_path()), exist_ok=True)

        dicttonx(
            self.metadata,
            h5file=url.file_path(),
            h5path=url.data_path(),
            update_mode="replace",
            mode="a",
        )

    @docstring(VolumeBase)
    def load_data(
        self, url: Optional[DataUrl] = None, store: bool = True
    ) -> numpy.ndarray:
        url = url or self.data_url
        if url is None:
            raise ValueError(
                "Cannot get data_url. An url should be provided. Don't know where to save this."
            )

        with HDF5File(filename=url.file_path(), mode="r") as h5s:
            if url.data_path() in h5s:
                data = h5s[url.data_path()][()]
            else:
                raise KeyError(f"Data path {url.data_path()} not found.")

        if store:
            self.data = data

        return data

    def get_slice(self, xy=None, xz=None, yz=None, url: Optional[DataUrl] = None):
        if xy is yz is xz is None:
            raise ValueError(
                "At most one of xy, xz or yz should be given to decide which slice user wants"
            )

        if self.data is not None:
            return self.select(volume=self.data, xy=xy, xz=xz, yz=yz)
        else:
            url = url or self.data_url
            if url is None:
                raise ValueError(
                    "Cannot get data_url. An url should be provided. Don't know where to save this."
                )
            with HDF5File(filename=url.file_path(), mode="r") as h5s:
                if url.data_path() in h5s:
                    return self.select(volume=h5s[url.data_path()], xy=xy, xz=xz, yz=yz)
                else:
                    raise KeyError(f"Data path {url.data_path()} not found.")

    @docstring(VolumeBase)
    def load_metadata(self, url: Optional[DataUrl] = None, store: bool = True) -> dict:
        url = url or self.metadata_url
        if url is None:
            raise ValueError(
                "Cannot get metadata_url. An url should be provided. Don't know where to save this."
            )
        try:
            metadata = nxtodict(
                h5file=url.file_path(), path=url.data_path(), asarray=False
            )
        except KeyError:
            _logger.warning(f"no metadata found in {url.data_path()}")
            metadata = {}
        if store:
            self.metadata = metadata
        return metadata

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
        if url is not None and os.path.exists(url.file_path()):
            yield url

    @staticmethod
    @docstring(VolumeBase)
    def from_identifier(identifier):
        """Return the Dataset from a identifier"""
        if not isinstance(identifier, HDF5VolumeIdentifier):
            raise TypeError(
                f"identifier should be an instance of {HDF5VolumeIdentifier}"
            )
        return HDF5Volume(
            file_path=identifier.file_path,
            data_path=identifier.data_path,
        )

    @docstring(VolumeBase)
    def get_identifier(self) -> HDF5VolumeIdentifier:
        if self.url is None:
            raise ValueError("no file_path provided. Cannot provide an identifier")
        return HDF5VolumeIdentifier(
            object=self, hdf5_file=self.url.file_path(), entry=self.url.data_path()
        )

    @staticmethod
    def example_defined_from_str_identifier() -> str:
        return (
            HDF5Volume(file_path="/path/to/file_path", data_path="entry0000")
            .get_identifier()
            .to_str()
        )


def get_default_data_path_for_volume(scan: TomoScanBase) -> str:
    if not isinstance(scan, TomoScanBase):
        raise TypeError(
            f"scan is expected to be an instance of {TomoScanBase} not {type(scan)}"
        )
    entry = getattr(scan, "entry", "entry")
    return "/".join([entry, "reconstruction"])
