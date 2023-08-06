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
"""module defining utils for a jp2k volume"""


__authors__ = ["H. Payno", "P. Paleo"]
__license__ = "MIT"
__date__ = "27/01/2022"


from typing import Optional
import os
import numpy
from tomoscan.esrf.identifier.jp2kidentifier import JP2KVolumeIdentifier
from tomoscan.scanbase import TomoScanBase
from .singleframebase import VolumeSingleFrameBase
from silx.io.url import DataUrl
from packaging.version import parse as parse_version
from tomoscan.utils import docstring
import logging

try:
    import glymur  # noqa #F401 needed for later possible lazy loading
except ImportError:
    has_glymur = False
    has_minimal_opengl = False
else:
    has_glymur = True
    from glymur import set_option as glymur_set_option
    from glymur.version import openjpeg_version, version as glymur_version

    if openjpeg_version < "2.3.0":
        has_minimal_opengl = False
    else:
        has_minimal_opengl = True

_logger = logging.getLogger(__name__)

_MISSING_GLYMUR_MSG = "Fail to import glymur. won't be able to load / save volume to jp2k. You can install it by calling pip."


class JP2KVolume(VolumeSingleFrameBase):
    """
    Save volume data to single frame jp2k files and metadata to .txt file

    :param Optional[list] cratios: list of ints. compression ratio for each jpeg2000 layer
    :param Optional[list] psnr: list of int.
                                The PSNR (Peak Signal-to-Noise ratio) for each jpeg2000 layer.
                                This defines a quality metric for lossy compression.
                                The number "0" stands for lossless compression.
    :param Optional[int] n_threads: number of thread to use for writing. If None will try to get as much as possible

    :warning: each file saved under {volume_basename}_{index_zfill4}.jp2k is considered to be a slice of the volume.
    """

    DEFAULT_DATA_EXTENSION = "jp2k"

    DEFAULT_DATA_SCHEME = "glymur"

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
        cratios: Optional[list] = None,
        psnr: Optional[list] = None,
        n_threads: Optional[int] = None,
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
            data=data,
            volume_basename=volume_basename,
            source_scan=source_scan,
            metadata=metadata,
            data_url=data_url,
            metadata_url=metadata_url,
            overwrite=overwrite,
            start_index=start_index,
            data_extension=data_extension,
            metadata_extension=metadata_extension,
        )
        if not has_glymur:
            _logger.warning(_MISSING_GLYMUR_MSG)
        else:
            if not has_minimal_opengl:
                _logger.warning(
                    "You must have at least version 2.3.0 of OpenJPEG "
                    "in order to write jp2k images."
                )
        self._cratios = cratios
        self._psnr = psnr
        self.setup_multithread_encoding(n_threads=n_threads)

    @property
    def cratios(self) -> Optional[list]:
        return self._cratios

    @property
    def psnr(self) -> Optional[list]:
        return self._psnr

    @docstring(VolumeSingleFrameBase)
    def save_frame(self, frame, file_name, scheme):
        if not has_glymur:
            raise RuntimeError(_MISSING_GLYMUR_MSG)

        if scheme == "glymur":
            glymur.Jp2k(file_name, data=frame, psnr=self.psnr, cratios=self.cratios)
        else:
            raise ValueError(f"Scheme {scheme} is not handled")

    @docstring(VolumeSingleFrameBase)
    def load_frame(self, file_name, scheme):
        if not has_glymur:
            raise RuntimeError(_MISSING_GLYMUR_MSG)

        if scheme == "glymur":
            jp2_file = glymur.Jp2k(file_name)
            return jp2_file[:]
        else:
            raise ValueError(f"Scheme {scheme} is not handled")

    @staticmethod
    def setup_multithread_encoding(n_threads=None, what_if_not_available="ignore"):
        """
        Setup OpenJpeg multi-threaded encoding.

        Parameters
        -----------
        n_threads: int, optional
            Number of threads. If not provided, all available threads are used.
        na: str, optional
            What to do if requirements are not fulfilled. Possible values are:
               - "ignore": do nothing, proceed
               - "print": show an information message
               - "raise": raise an error
        """
        required_glymur_version = "0.9.3"
        required_openjpeg_version = "2.4.0"

        def not_available(msg):
            if what_if_not_available == "raise":
                raise ValueError(msg)
            elif what_if_not_available == "print":
                print(msg)

        requirements = [
            ("glymur", glymur_version, required_glymur_version),
            ("libopenjpeg", openjpeg_version, required_openjpeg_version),
        ]
        for what, current_version, required_version in requirements:
            if parse_version(current_version) < parse_version(required_version):
                not_available(
                    "%s version >= %s is required for multi-threaded encoding (current version: %s)"
                    % (what, required_version, current_version)
                )
                return
        if n_threads is None:
            n_threads = get_available_threads()
        glymur_set_option("lib.num_threads", n_threads)

    @staticmethod
    @docstring(VolumeSingleFrameBase)
    def from_identifier(identifier):
        """Return the Dataset from a identifier"""
        if not isinstance(identifier, JP2KVolumeIdentifier):
            raise TypeError(
                f"identifier should be an instance of {JP2KVolumeIdentifier}"
            )
        return JP2KVolume(
            folder=identifier.folder,
            volume_basename=identifier.file_prefix,
        )

    @docstring(VolumeSingleFrameBase)
    def get_identifier(self) -> JP2KVolumeIdentifier:
        if self.url is None:
            raise ValueError("no file_path provided. Cannot provide an identifier")
        return JP2KVolumeIdentifier(
            object=self, folder=self.url.file_path(), file_prefix=self._volume_basename
        )

    @staticmethod
    def example_defined_from_str_identifier() -> str:
        return " ; ".join(
            [
                f"{JP2KVolume(folder='/path/to/my/my_folder').get_identifier().to_str()}",
                f"{JP2KVolume(folder='/path/to/my/my_folder', volume_basename='mybasename').get_identifier().to_str()} (if mybasename != folder name)",
            ]
        )


def get_available_threads():
    return len(os.sched_getaffinity(0))
