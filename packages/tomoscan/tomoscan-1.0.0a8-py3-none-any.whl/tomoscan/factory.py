# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016-2022 European Synchrotron Radiation Facility
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
#############################################################################
"""Contains the Factory class and dedicated functions"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "27/02/2019"


from urllib.parse import urlparse
from tomoscan.esrf.identifier.jp2kidentifier import JP2KVolumeIdentifier
from tomoscan.esrf.identifier.tiffidentifier import (
    MultiTiffVolumeIdentifier,
    TIFFVolumeIdentifier,
)
from tomoscan.esrf.identifier.url_utils import split_path
from tomoscan.esrf.volume.edfvolume import EDFVolume
from tomoscan.esrf.volume.hdf5volume import HDF5Volume
from tomoscan.esrf.volume.jp2kvolume import JP2KVolume
from tomoscan.esrf.volume.tiffvolume import MultiTIFFVolume, TIFFVolume
from tomoscan.tomoobject import TomoObject
from .scanbase import TomoScanBase
from .esrf.scan.edfscan import EDFTomoScan
from .esrf.scan.hdf5scan import HDF5TomoScan
from .esrf.identifier.edfidentifier import EDFTomoScanIdentifier, EDFVolumeIdentifier
from .esrf.identifier.hdf5Identifier import HDF5TomoScanIdentifier, HDF5VolumeIdentifier
from tomoscan.identifier import BaseIdentifier, ScanIdentifier, VolumeIdentifier
from . import identifier as _identifier_mod
from typing import Union
import os


class Factory:
    """
    Factory any TomoObject
    """

    @staticmethod
    def create_tomo_object_from_identifier(
        identifier: Union[str, ScanIdentifier],
    ) -> TomoObject:
        """
        Create an instance of TomoScanBase from his identifier if possible

        :param str identifier: identifier of the TomoScanBase
        :raises: TypeError if identifier is not a str
        :raises: ValueError if identifier cannot be converted back to an instance of TomoScanBase
        """
        if not isinstance(identifier, (str, BaseIdentifier)):
            raise TypeError(
                f"identifier is expected to be a str or an instance of {BaseIdentifier} not {type(identifier)}"
            )

        # step 1: convert identifier to an instance of BaseIdentifier if necessary
        if isinstance(identifier, str):
            info = urlparse(identifier)
            paths = split_path(info.path)
            scheme = info.scheme
            if len(paths) == 1:
                # insure backward compatibility. Originally (until 0.8) there was only one type which was scan
                tomo_type = ScanIdentifier.TOMO_TYPE
            elif len(paths) == 2:
                tomo_type, _ = paths
            else:
                raise ValueError("Failed to parse path string:", info.path)

            if tomo_type == _identifier_mod.VolumeIdentifier.TOMO_TYPE:
                if scheme == "edf":
                    identifier = EDFVolumeIdentifier.from_str(identifier=identifier)
                elif scheme == "hdf5":
                    identifier = HDF5VolumeIdentifier.from_str(identifier=identifier)
                elif scheme == "tiff":
                    identifier = TIFFVolumeIdentifier.from_str(identifier=identifier)
                elif scheme == "tiff3d":
                    identifier = MultiTiffVolumeIdentifier.from_str(
                        identifier=identifier
                    )
                elif scheme == "jp2k":
                    identifier = JP2KVolumeIdentifier.from_str(identifier=identifier)
                else:
                    raise ValueError(f"Scheme {scheme} is not recognized")

            elif tomo_type == _identifier_mod.ScanIdentifier.TOMO_TYPE:
                # otherwise consider this is a scan. Insure backward compatibility
                if scheme == "edf":
                    identifier = EDFTomoScanIdentifier.from_str(identifier=identifier)
                elif scheme == "hdf5":
                    identifier = HDF5TomoScanIdentifier.from_str(identifier=identifier)
                else:
                    raise ValueError(f"Scheme {scheme} not recognized")
            else:
                raise ValueError(f"{tomo_type} is not an handled tomo type")

        # step 2: convert identifier to a TomoBaseObject
        assert isinstance(identifier, BaseIdentifier)
        scheme = identifier.scheme
        tomo_type = identifier.tomo_type

        if scheme == "edf":
            if tomo_type == VolumeIdentifier.TOMO_TYPE:
                return EDFVolume.from_identifier(identifier=identifier)
            elif tomo_type == ScanIdentifier.TOMO_TYPE:
                return EDFTomoScan.from_identifier(identifier=identifier)
            else:
                raise NotImplementedError()
        elif scheme == "hdf5":
            if tomo_type == VolumeIdentifier.TOMO_TYPE:
                return HDF5Volume.from_identifier(identifier=identifier)
            elif tomo_type == ScanIdentifier.TOMO_TYPE:
                return HDF5TomoScan.from_identifier(identifier=identifier)
            else:
                raise NotImplementedError()
        elif scheme == "jp2k":
            if tomo_type == VolumeIdentifier.TOMO_TYPE:
                return JP2KVolume.from_identifier(identifier=identifier)
            else:
                raise NotImplementedError
        elif scheme == "tiff":
            if tomo_type == VolumeIdentifier.TOMO_TYPE:
                return TIFFVolume.from_identifier(identifier=identifier)
            else:
                raise NotImplementedError
        elif scheme == "tiff3d":
            if tomo_type == VolumeIdentifier.TOMO_TYPE:
                return MultiTIFFVolume.from_identifier(identifier=identifier)
            else:
                raise NotImplementedError
        else:
            raise ValueError(f"Scheme {scheme} not recognized")

    @staticmethod
    def create_scan_object(scan_path: str) -> TomoScanBase:
        """

        :param str scan_path: path to the scan directory or file
        :return: ScanBase instance fitting the scan folder or scan path
        :rtype: TomoScanBase
        """
        # remove any final separator (otherwise basename might fail)
        scan_path = scan_path.rstrip(os.path.sep)
        if EDFTomoScan.is_tomoscan_dir(scan_path):
            return EDFTomoScan(scan=scan_path)
        elif HDF5TomoScan.is_tomoscan_dir(scan_path):
            return HDF5TomoScan(scan=scan_path)
        else:
            raise ValueError("%s is not a valid scan path" % scan_path)

    @staticmethod
    def create_scan_objects(scan_path: str) -> tuple:
        """

        :param str scan_path: path to the scan directory or file
        :return: all possible instances of TomoScanBase contained in the given
                 path
        :rtype: tuple
        """
        scan_path = scan_path.rstrip(os.path.sep)
        if EDFTomoScan.is_tomoscan_dir(scan_path):
            return (EDFTomoScan(scan=scan_path),)
        elif HDF5TomoScan.is_tomoscan_dir(scan_path):
            scans = []
            master_file = HDF5TomoScan.get_master_file(scan_path=scan_path)
            entries = HDF5TomoScan.get_valid_entries(master_file)
            for entry in entries:
                scans.append(HDF5TomoScan(scan=scan_path, entry=entry, index=None))
            return tuple(scans)

        raise ValueError("%s is not a valid scan path" % scan_path)

    @staticmethod
    def create_scan_object_frm_dict(_dict: dict) -> TomoScanBase:
        """
        Create a TomoScanBase instance from a dictionary. It should contains
        the TomoScanBase._DICT_TYPE_KEY key at least.

        :param _dict: dictionary to be converted
        :return: instance of TomoScanBase
        :rtype: TomoScanBase
        """
        if TomoScanBase.DICT_TYPE_KEY not in _dict:
            raise ValueError(
                "given dict is not recognized. Cannot find" "",
                TomoScanBase.DICT_TYPE_KEY,
            )
        elif _dict[TomoScanBase.DICT_TYPE_KEY] == EDFTomoScan._TYPE:
            return EDFTomoScan(scan=None).load_from_dict(_dict)
        else:
            raise ValueError(
                f"Scan type: {_dict[TomoScanBase.DICT_TYPE_KEY]} is not managed"
            )

    @staticmethod
    def is_tomoscan_dir(scan_path: str) -> bool:
        """

        :param str scan_path: path to the scan directory or file
        :return: True if the given path is a root folder of an acquisition.
        :rtype: bool
        """
        return HDF5TomoScan.is_tomoscan_dir(scan_path) or EDFTomoScan.is_tomoscan_dir(
            scan_path
        )
