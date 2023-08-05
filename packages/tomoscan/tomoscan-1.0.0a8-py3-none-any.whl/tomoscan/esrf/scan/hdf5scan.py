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

"""contains HDF5TomoScan, class to be used with HDF5 acquisition and associated classes, functions."""


__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "09/08/2018"


from silx.utils.deprecation import deprecated
from tomoscan.esrf.scan.framereducer.hdf5framereducer import HDF5FrameReducer
from tomoscan.unitsystem import electriccurrentsystem, energysystem, timesystem
from tomoscan.scanbase import TomoScanBase, FOV
from tomoscan.scanbase import Source
import json
import io
import os
import h5py
import numpy
from silx.io.url import DataUrl
from silx.utils.enum import Enum as _Enum
from tomoscan.utils import BoundingBox1D, docstring
from tomoscan.io import HDF5File
from tomoscan.identifier import ScanIdentifier
from tomoscan.esrf.identifier.hdf5Identifier import HDF5TomoScanIdentifier
from silx.io.utils import get_data
from tomoscan.unitsystem.unit import Unit
from tomoscan.unitsystem.metricsystem import MetricSystem
from tomoscan.nexus.paths.nxtomo import get_paths as _get_nexus_paths
from .utils import get_compacted_dataslices
from silx.io.utils import h5py_read_dataset
import typing
import logging

_logger = logging.getLogger(__name__)


class ImageKey(_Enum):
    ALIGNMENT = -1
    PROJECTION = 0
    FLAT_FIELD = 1
    DARK_FIELD = 2
    INVALID = 3


@deprecated(
    reason="moved", replacement="tomoscan.nexus.paths.nxtomo", since_version="0.8.0"
)
def get_nexus_paths(version: float):
    return _get_nexus_paths(version=version)


class HDF5TomoScan(TomoScanBase):
    """
    This is the implementation of a TomoBase class for an acquisition stored
    in a HDF5 file.

    For now several property of the acquisition is accessible thought a getter
    (like get_scan_range) and a property (scan_range).

    This is done to be compliant with TomoBase instantiation. But his will be
    replace progressively by properties at the 'TomoBase' level

    :param scan: scan directory or scan masterfile.h5
    :param Union[str, None] entry: name of the NXtomo entry to select. If given
                                   index is ignored.
    :param Union[int, None] index: of the NXtomo entry to select. Ignored if
                                   an entry is specified. For consistency
                                   entries are ordered alphabetically
    :param Union[float, None] nx_version: Version of the Nexus convention to use.
                                          By default (None) it will take the latest one
    """

    _NEXUS_VERSION_PATH = "version"

    _TYPE = "hdf5"

    _DICT_ENTRY_KEY = "entry"

    SCHEME = "silx"

    REDUCED_DARKS_DATAURLS = (
        DataUrl(
            file_path="{scan_prefix}_darks.hdf5",
            data_path="{entry}/darks/{index}",
            scheme=SCHEME,
        ),
    )

    REDUCED_FLATS_DATAURLS = (
        DataUrl(
            file_path="{scan_prefix}_flats.hdf5",
            data_path="{entry}/flats/{index}",
            scheme=SCHEME,
        ),
    )

    FRAME_REDUCER_CLASS = HDF5FrameReducer

    def __init__(
        self,
        scan: str,
        entry: str = None,
        index: typing.Union[int, None] = 0,
        ignore_projections: typing.Union[None, typing.Iterable] = None,
        nx_version=None,
    ):
        if entry is not None:
            index = None
        # if the user give the master file instead of the scan dir...
        if scan is not None:
            if not os.path.exists(scan) and "." in os.path.split(scan)[-1]:
                self.master_file = scan
                scan = os.path.dirname(scan)
            elif os.path.isfile(scan) or ():
                self.master_file = scan
                scan = os.path.dirname(scan)
            else:
                self.master_file = self.get_master_file(scan)
        else:
            self.master_file = None

        super(HDF5TomoScan, self).__init__(
            scan=scan, type_=HDF5TomoScan._TYPE, ignore_projections=ignore_projections
        )

        if scan is None:
            self._entry = None
        else:
            self._entry = entry or self._get_entry_at(
                index=index, file_path=self.master_file
            )
            if self._entry is None:
                raise ValueError(
                    "unable to find a valid entry for %s" % self.master_file
                )
        # for now the default entry is 1_tomo but should change with time
        self._name = None
        self._sample_name = None
        self._grp_size = None
        # data caches
        self._projections_compacted = None
        self._flats = None
        self._darks = None
        self._tomo_n = None
        # number of projections / radios
        self._dark_n = None
        # number of dark image made during acquisition
        self._flat_n = None
        # number of flat field made during acquisition
        self._scan_range = None
        # scan range, in degree
        self._dim_1, self._dim_2 = None, None
        # image dimensions
        self._x_pixel_size = None
        self._y_pixel_size = None
        # pixel dimensions (tuple)
        self._frames = None
        self._image_keys = None
        self._image_keys_control = None
        self._rotation_angles = None
        self._distance = None
        self._fov = None
        self._energy = None
        self._estimated_cor_frm_motor = None
        self._start_time = None
        self._end_time = None
        self._x_translations = None
        self._y_translations = None
        self._z_translations = None
        self._nexus_paths = None
        self._nexus_version = None
        self._user_nx_version = nx_version
        self._source_type = None
        self._source_name = None
        self._instrument_name = None

    @staticmethod
    def get_master_file(scan_path):
        if os.path.isfile(scan_path):
            master_file = scan_path
        else:
            master_file = os.path.join(scan_path, os.path.basename(scan_path))
            if os.path.exists(master_file + ".nx"):
                master_file = master_file + ".nx"
            elif os.path.exists(master_file + ".hdf5"):
                master_file = master_file + ".hdf5"
            elif os.path.exists(master_file + ".h5"):
                master_file = master_file + ".h5"
            else:
                master_file = master_file + ".nx"
        return master_file

    @docstring(TomoScanBase.clear_caches)
    def clear_caches(self) -> None:
        super().clear_caches()
        self._projections = None
        self._projections_compacted = None
        self._flats = None
        self._darks = None
        self._tomo_n = None
        self._dark_n = None
        self._flat_n = None
        self._scan_range = None
        self._dim_1, self._dim_2 = None, None
        self._x_pixel_size = None
        self._y_pixel_size = None
        self._x_magnified_pixel_size = None
        self._y_magnified_pixel_size = None
        self._rotation_angles = None
        self._distance = None
        self._fov = None
        self._image_keys_control = None
        self._exposure_time = None
        self._x_flipped = None
        self._y_flipped = None
        self._x_translations = None
        self._y_translations = None
        self._z_translations = None
        self._source = None
        self._source_type = None
        self._source_name = None
        self._instrument_name = None

    @staticmethod
    def _get_entry_at(index: int, file_path: str) -> str:
        """

        :param index:
        :param file_path:
        :return:
        """
        entries = HDF5TomoScan.get_valid_entries(file_path)
        if len(entries) == 0:
            return None
        else:
            return entries[index]

    @staticmethod
    def get_valid_entries(file_path: str) -> tuple:
        """
        return the list of 'Nxtomo' entries at the root level

        :param str file_path:
        :return: list of valid Nxtomo node (ordered alphabetically)
        :rtype: tuple

        ..note: entries are sorted to insure consistency
        """
        res = []
        res_buf = []

        if not os.path.isfile(file_path):
            raise ValueError("given file path should be a file")

        with HDF5File(file_path, "r") as h5f:
            for root_node in h5f.keys():
                node = h5f[root_node]
                if HDF5TomoScan.node_is_nxtomo(node) is True:
                    res_buf.append(root_node)  # cannnot be node because of sym links

            [res.append(node) for node in res_buf]
        res.sort()
        return tuple(res)

    @staticmethod
    def node_is_nxtomo(node: h5py.Group) -> bool:
        """check if the given h5py node is an nxtomo node or not"""
        if "NX_class" in node.attrs or "NXclass" in node.attrs:
            _logger.info(node.name + " is recognized as an nx class.")
        else:
            _logger.info(node.name + " is node an nx class.")
            return False
        if "definition" in node.attrs and node.attrs["definition"].lower() == "nxtomo":
            _logger.info(node.name + " is recognized as an NXtomo class.")
            return True
        elif (
            "instrument" in node
            and "NX_class" in node["instrument"].attrs
            and node["instrument"].attrs["NX_class"] == "NXinstrument"
        ):
            return "detector" in node["instrument"]
        else:
            return False

    @docstring(TomoScanBase.is_tomoscan_dir)
    @staticmethod
    def is_tomoscan_dir(directory: str, **kwargs) -> bool:
        if os.path.isfile(directory):
            master_file = directory
        else:
            master_file = HDF5TomoScan.get_master_file(scan_path=directory)
        if master_file:
            entries = HDF5TomoScan.get_valid_entries(file_path=master_file)
            return len(entries) > 0

    @docstring(TomoScanBase.is_abort)
    def is_abort(self, **kwargs):
        # for now there is no abort definition in .hdf5
        return False

    @docstring(TomoScanBase.to_dict)
    def to_dict(self) -> dict:
        res = super().to_dict()
        res[self.DICT_PATH_KEY] = self.master_file
        res[self._DICT_ENTRY_KEY] = self.entry
        return res

    @staticmethod
    def from_dict(_dict: dict):
        scan = HDF5TomoScan(scan=None)
        scan.load_from_dict(_dict=_dict)
        return scan

    @docstring(TomoScanBase.load_from_dict)
    def load_from_dict(self, _dict: dict) -> TomoScanBase:
        """

        :param _dict:
        :return:
        """
        if isinstance(_dict, io.TextIOWrapper):
            data = json.load(_dict)
        else:
            data = _dict
        if not (self.DICT_TYPE_KEY in data and data[self.DICT_TYPE_KEY] == self._TYPE):
            raise ValueError("Description is not an HDF5Scan json description")
        if HDF5TomoScan._DICT_ENTRY_KEY not in data:
            raise ValueError("No hdf5 entry specified")

        assert self.DICT_PATH_KEY in data
        self._entry = data[self._DICT_ENTRY_KEY]
        self.master_file = self.get_master_file(data[self.DICT_PATH_KEY])

        if os.path.isdir(data[self.DICT_PATH_KEY]):
            self.path = data[self.DICT_PATH_KEY]
        else:
            self.path = os.path.dirname(data[self.DICT_PATH_KEY])
        return self

    @property
    def entry(self) -> str:
        return self._entry

    @property
    def nexus_version(self):
        if self._user_nx_version is not None:
            return self._user_nx_version
        return self._get_generic_key(
            "_nexus_version", self._NEXUS_VERSION_PATH, is_attribute=True
        )

    @nexus_version.setter
    def nexus_version(self, version):
        if not isinstance(version, float):
            raise TypeError("version expect to be a float")
        self._nexus_version = version

    @property
    def nexus_path(self):
        if self._nexus_paths is None:
            self._nexus_paths = _get_nexus_paths(self.nexus_version)
        return self._nexus_paths

    @property
    @docstring(TomoScanBase.source)
    def source(self):
        if self._source is None:
            self._source = Source(
                name=self.source_name,
                type=self.source_type,
            )
        return self._source

    @property
    def source_name(self):
        return self._get_generic_key("_source_name", self.nexus_path.SOURCE_NAME)

    @property
    def source_type(self):
        return self._get_generic_key("_source_type", self.nexus_path.SOURCE_TYPE)

    @property
    @docstring(TomoScanBase.instrument_name)
    def instrument_name(self) -> typing.Union[None, str]:
        """

        :return: instrument name
        """
        return self._get_generic_key(
            "_instrument_name", self.nexus_path.INSTRUMENT_NAME
        )

    @property
    def sequence_name(self):
        """Return the sequence name"""
        return self._get_generic_key("_name", self.nexus_path.NAME_PATH)

    @property
    @docstring(TomoScanBase.projections)
    def sample_name(self):
        return self._get_generic_key("_sample_name", self.nexus_path.SAMPLE_NAME_PATH)

    @property
    @docstring(TomoScanBase.projections)
    def group_size(self):
        return self._get_generic_key("_grp_size", self.nexus_path.GRP_SIZE_ATTR)

    @property
    @docstring(TomoScanBase.projections)
    def projections(self) -> typing.Union[dict, None]:
        if self._projections is None:
            if self.frames:
                ignored_projs = []
                if self.ignore_projections is not None:
                    ignored_projs = self.ignore_projections
                proj_frames = tuple(
                    filter(
                        lambda x: (
                            x.image_key is ImageKey.PROJECTION
                            and x.index not in ignored_projs
                            and x.is_control is False
                        ),
                        self.frames,
                    )
                )
                self._projections = {}
                for proj_frame in proj_frames:
                    self._projections[proj_frame.index] = proj_frame.url
        return self._projections

    @projections.setter
    def projections(self, projections: dict):
        self._projections = projections

    def get_projections_intensity_monitor(self) -> dict:
        """return intensity monitor values for projections"""
        if self.frames:
            ignored_projs = []
            if self.ignore_projections is not None:
                ignored_projs = self.ignore_projections
            proj_frames = tuple(
                filter(
                    lambda x: (
                        x.image_key is ImageKey.PROJECTION
                        and x.index not in ignored_projs
                        and x.is_control is False
                    ),
                    self.frames,
                )
            )
            intensity_monitor = {}
            for proj_frame in proj_frames:
                intensity_monitor[proj_frame.index] = proj_frame.intensity_monitor
            return intensity_monitor
        else:
            return {}

    @property
    @docstring(TomoScanBase.alignment_projections)
    def alignment_projections(self) -> typing.Union[dict, None]:
        if self._alignment_projections is None:
            if self.frames:
                proj_frames = tuple(
                    filter(
                        lambda x: x.image_key == ImageKey.PROJECTION
                        and x.is_control is True,
                        self.frames,
                    )
                )
                self._alignment_projections = {}
                for proj_frame in proj_frames:
                    self._alignment_projections[proj_frame.index] = proj_frame.url
        return self._alignment_projections

    @property
    @docstring(TomoScanBase.darks)
    def darks(self) -> typing.Union[dict, None]:
        if self._darks is None:
            if self.frames:
                dark_frames = tuple(
                    filter(lambda x: x.image_key is ImageKey.DARK_FIELD, self.frames)
                )
                self._darks = {}
                for dark_frame in dark_frames:
                    self._darks[dark_frame.index] = dark_frame.url
        return self._darks

    @property
    @docstring(TomoScanBase.flats)
    def flats(self) -> typing.Union[dict, None]:
        if self._flats is None:
            if self.frames:
                flat_frames = tuple(
                    filter(lambda x: x.image_key is ImageKey.FLAT_FIELD, self.frames)
                )
                self._flats = {}
                for flat_frame in flat_frames:
                    self._flats[flat_frame.index] = flat_frame.url
        return self._flats

    @docstring(TomoScanBase.update)
    def update(self) -> None:
        """update list of radio and reconstruction by parsing the scan folder"""
        if self.master_file is None or not os.path.exists(self.master_file):
            return
        self.projections = self._get_projections_url()
        # TODO: update darks and flats too

    @docstring(TomoScanBase.get_proj_angle_url)
    def _get_projections_url(self):
        if self.master_file is None or not os.path.exists(self.master_file):
            return
        frames = self.frames
        if frames is not None:
            urls = {}
            for frame in frames:
                if frame.image_key is ImageKey.PROJECTION:
                    urls[frame.index] = frame.url
            return urls
        else:
            return None

    @docstring(TomoScanBase.tomo_n)
    @property
    def tomo_n(self) -> typing.Union[None, int]:
        """we are making two asumptions for computing tomo_n:
        - if a rotation = scan_range +/- EPSILON this is a return projection
        - The delta between each projections is constant
        """
        return self._get_generic_key("_tomo_n", self.nexus_path.TOMO_N_SCAN)

    @docstring(TomoScanBase.tomo_n)
    @property
    def magnification(self):
        return self._get_generic_key(
            "_magnification",
            "/".join(
                [
                    self.nexus_path.INSTRUMENT_PATH,
                    self.nexus_path.nx_instrument_paths.DETECTOR_PATH,
                    self.nexus_path.nx_detector_paths.MAGNIFICATION,
                ]
            ),
        )

    @property
    def return_projs(self) -> typing.Union[None, list]:
        """ """
        frames = self.frames
        if frames:
            return_frames = list(filter(lambda x: x.is_control is True, frames))
            return return_frames
        else:
            return None

    @property
    def rotation_angle(self) -> typing.Union[None, tuple]:
        cast_to_float = lambda values: [float(val) for val in values]
        return self._get_generic_key(
            "_rotation_angles",
            self.nexus_path.ROTATION_ANGLE_PATH,
            apply_function=cast_to_float,
        )

    @property
    def x_translation(self) -> typing.Union[None, tuple]:
        cast_to_float = lambda values: [float(val) for val in values]
        return self._get_generic_key(
            "_x_translations",
            self.nexus_path.X_TRANS_PATH,
            apply_function=cast_to_float,
            unit=MetricSystem.METER,
        )

    @property
    def y_translation(self) -> typing.Union[None, tuple]:
        cast_to_float = lambda values: [float(val) for val in values]
        return self._get_generic_key(
            "_y_translations",
            self.nexus_path.Y_TRANS_PATH,
            apply_function=cast_to_float,
            unit=MetricSystem.METER,
        )

    @property
    def z_translation(self) -> typing.Union[None, tuple]:
        cast_to_float = lambda values: [float(val) for val in values]
        return self._get_generic_key(
            "_z_translations",
            self.nexus_path.Z_TRANS_PATH,
            apply_function=cast_to_float,
            unit=MetricSystem.METER,
        )

    @property
    def image_key(self) -> typing.Union[list, None]:
        return self._get_generic_key("_image_keys", self.nexus_path.IMG_KEY_PATH)

    @property
    def image_key_control(self) -> typing.Union[list, None]:
        return self._get_generic_key(
            "_image_keys_control", self.nexus_path.IMG_KEY_CONTROL_PATH
        )

    @property
    def exposure_time(self) -> typing.Union[list, None]:
        return self._get_generic_key(
            "_exposure_time",
            self.nexus_path.EXPOSURE_TIME_PATH,
            unit=timesystem.TimeSystem.SECOND,
        )

    @property
    def electric_current(self) -> dict:
        return self._get_generic_key(
            "_electric_current",
            self.nexus_path.ELECTRIC_CURRENT_PATH,
            unit=electriccurrentsystem.ElectricCurrentSystem.AMPERE,
        )

    def x_flipped(self) -> bool:
        return self._get_generic_key(
            "_x_flipped",
            "/".join(
                [
                    self.nexus_path.INSTRUMENT_PATH,
                    self.nexus_path.nx_instrument_paths.DETECTOR_PATH,
                    self.nexus_path.nx_detector_paths.X_FLIPPED,
                ]
            ),
        )

    @property
    def y_flipped(self) -> bool:
        return self._get_generic_key(
            "_y_flipped",
            "/".join(
                [
                    self.nexus_path.INSTRUMENT_PATH,
                    self.nexus_path.nx_instrument_paths.DETECTOR_PATH,
                    self.nexus_path.nx_detector_paths.Y_FLIPPED,
                ]
            ),
        )

    @docstring(TomoScanBase)
    def get_bounding_box(self, axis: typing.Union[str, int]) -> tuple:
        """
        Return the bounding box covered by the scan (only take into account the projections).
        axis is expected to be in (0, 1, 2) or (x==0, y==1, z==2)

        :note: current pixel size is given with magnification. To move back to sample space (x_translation, y_translation, z_translation)
               we need to `unmagnified` this is size
        """
        if axis == 0:
            axis = "x"
        elif axis == 1:
            axis = "y"
        elif axis == 2:
            axis = "z"
        if axis not in ("x", "y", "z"):
            raise ValueError(
                f"Axis is expected to be in ('x', 'y', 'z', 0, 1, 2). Got {axis}."
            )

        if axis == "x":
            translations = self.x_translation
            default_pixel_size = self.x_pixel_size
            n_pixel = self.dim_1
        elif axis == "y":
            translations = self.y_translation
            default_pixel_size = self.y_pixel_size
            n_pixel = self.dim_2
        elif axis == "z":
            translations = self.z_translation
            default_pixel_size = self.y_pixel_size
            n_pixel = self.dim_2
        else:
            raise ValueError(
                f"Axis is expected to be in ('x', 'y', 'z', 0, 1, 2). Got {axis}."
            )

        if translations is None or len(translations) == 0:
            raise ValueError(f"Unable to find translation for axis {axis}")
        translations = numpy.asarray(translations)
        # TODO: might need to filter only the projection one ?
        filetered_translation_for_proj = translations[
            self.image_key_control == ImageKey.PROJECTION.value
        ]
        min_axis_translation = filetered_translation_for_proj.min()
        max_axis_translation = filetered_translation_for_proj.max()
        if default_pixel_size is None:
            raise ValueError(f"Unable to find pixel size for axis {axis}")
        if n_pixel is None:
            raise ValueError(f"Unable to find number of pixel for axis {axis}")

        magnification = self.magnification
        if magnification is None:
            _logger.warning(
                f"Unable to find pixel magnification. Take 1 as magnification for {self}"
            )
            magnification = 1.0
        # we consider the w store represent the mean position of the detector
        min_pos_in_meter = min_axis_translation - (
            n_pixel / 2.0 * default_pixel_size / magnification
        )
        max_pos_in_meter = max_axis_translation + (
            n_pixel / 2.0 * default_pixel_size / magnification
        )
        return BoundingBox1D(min_pos_in_meter, max_pos_in_meter)

    def _get_generic_key(
        self,
        key_name,
        path_key_name,
        unit: typing.Optional[Unit] = None,
        apply_function=None,
        is_attribute=False,
    ) -> typing.Any:
        if not isinstance(unit, (type(None), Unit)):
            raise TypeError(
                f"default_unit must be an instance of {Unit} or None. Not {type(unit)}"
            )

        if getattr(self, key_name, None) is None:
            self._check_hdf5scan_validity()
            with HDF5File(self.master_file, "r") as h5_file:
                if is_attribute and path_key_name in h5_file[self._entry].attrs:
                    attr_val = h5py_read_dataset(
                        h5_file[self._entry].attrs[path_key_name]
                    )
                    if apply_function is not None:
                        attr_val = apply_function(attr_val)
                elif not is_attribute and path_key_name in h5_file[self._entry]:
                    if unit is not None:
                        attr_val = self._get_value(
                            h5_file[self._entry][path_key_name], default_unit=unit
                        )
                    else:
                        attr_val = h5py_read_dataset(
                            h5_file[self._entry][path_key_name]
                        )
                    if apply_function is not None:
                        attr_val = apply_function(attr_val)
                else:
                    attr_val = None
            setattr(self, key_name, attr_val)
        return getattr(self, key_name)

    @docstring(TomoScanBase.dark_n)
    @property
    def dark_n(self) -> typing.Union[None, int]:
        if self.darks is not None:
            return len(self.darks)
        else:
            return None

    @docstring(TomoScanBase.flat_n)
    @property
    def flat_n(self) -> typing.Union[None, int]:
        if self.flats is not None:
            return len(self.flats)
        else:
            return None

    @docstring(TomoScanBase.ff_interval)
    @property
    def ff_interval(self):
        raise NotImplementedError(
            "not implemented for hdf5. But we have " "acquisition sequence instead."
        )

    @docstring(TomoScanBase.scan_range)
    @property
    def scan_range(self) -> typing.Union[None, int]:
        """For now scan range should return 180 or 360. We don't expect other value."""
        if (
            self._scan_range is None
            and self.master_file
            and os.path.exists(self.master_file)
            and self._entry is not None
        ):
            rotation_angle = self.rotation_angle
            if rotation_angle is not None:
                angle_range = numpy.max(rotation_angle) - numpy.min(rotation_angle)
                dist_to180 = abs(180 - angle_range)
                dist_to360 = abs(360 - angle_range)
                if dist_to180 < dist_to360:
                    self._scan_range = 180
                else:
                    self._scan_range = 360
        return self._scan_range

    @property
    def dim_1(self) -> typing.Union[None, int]:
        if self._dim_1 is None:
            self._get_dim1_dim2()
        return self._dim_1

    @property
    def dim_2(self) -> typing.Union[None, int]:
        if self._dim_2 is None:
            self._get_dim1_dim2()
        return self._dim_2

    @property
    def pixel_size(self) -> typing.Union[None, float]:
        """return x pixel size in meter"""
        return self.x_pixel_size

    @property
    def x_pixel_size(self) -> typing.Union[None, float]:
        """return x pixel size in meter"""
        return self._get_generic_key(
            "_x_pixel_size",
            self.nexus_path.X_PIXEL_SIZE_PATH,
            unit=MetricSystem.METER,
        )

    @property
    def y_pixel_size(self) -> typing.Union[None, float]:
        """return y pixel size in meter"""
        return self._get_generic_key(
            "_y_pixel_size",
            self.nexus_path.Y_PIXEL_SIZE_PATH,
            unit=MetricSystem.METER,
        )

    def _get_fov(self):
        with HDF5File(self.master_file, "r", swmr=True, libver="latest") as h5_file:
            if self.nexus_path.FOV_PATH in h5_file[self._entry]:
                fov = h5py_read_dataset(h5_file[self._entry][self.nexus_path.FOV_PATH])
                return FOV.from_value(fov)
            else:
                return None

    def _get_dim1_dim2(self):
        if self.master_file and os.path.exists(self.master_file):
            if self.projections is not None:
                if len(self.projections) > 0:
                    url = list(self.projections.values())[0]
                    try:
                        with HDF5File(url.file_path(), mode="r") as h5s:
                            self._dim_2, self._dim_1 = h5s[url.data_path()].shape[-2:]
                    except Exception:
                        self._dim_2, self._dim_1 = get_data(
                            list(self.projections.values())[0]
                        ).shape

    @property
    def distance(self) -> typing.Union[None, float]:
        """return sample detector distance in meter"""
        return self._get_generic_key(
            "_distance",
            self.nexus_path.DISTANCE_PATH,
            unit=MetricSystem.METER,
        )

    @property
    @docstring(TomoScanBase.field_of_view)
    def field_of_view(self):
        if self._fov is None and self.master_file and os.path.exists(self.master_file):
            self._fov = self._get_fov()
        return self._fov

    @property
    @docstring(TomoScanBase.estimated_cor_frm_motor)
    def estimated_cor_frm_motor(self):
        cast_to_float = lambda x: float(x)
        return self._get_generic_key(
            "_estimated_cor_frm_motor",
            self.nexus_path.ESTIMATED_COR_FRM_MOTOR_PATH,
            apply_function=cast_to_float,
        )

    @property
    def energy(self) -> typing.Union[None, float]:
        """energy in keV"""
        energy_si = self._get_generic_key(
            "_energy",
            self.nexus_path.ENERGY_PATH,
            unit=energysystem.EnergySI.KILOELECTRONVOLT,
        )
        if energy_si is None:
            return None
        else:
            # has for energy we do an exception we don't use SI but kev
            energy_kev = energy_si / energysystem.EnergySI.KILOELECTRONVOLT.value
            return energy_kev

    @property
    def start_time(self):
        return self._get_generic_key("_start_time", self.nexus_path.START_TIME_PATH)

    @property
    def end_time(self):
        return self._get_generic_key("_end_time", self.nexus_path.END_TIME_PATH)

    @property
    def intensity_monitor(self):
        return self._get_generic_key(
            "_intensity_monitor", self.nexus_path.INTENSITY_MONITOR_PATH
        )

    @staticmethod
    def _is_return_frame(
        img_key, lframe, llast_proj_frame, ldelta_angle, return_already_reach
    ) -> tuple:
        """return is_return, delta_angle"""
        if ImageKey.from_value(img_key) is not ImageKey.PROJECTION:
            return False, None
        if ldelta_angle is None and llast_proj_frame is not None:
            delta_angle = lframe.rotation_angle - llast_proj_frame.rotation_angle
            return False, delta_angle
        elif return_already_reach:
            return True, ldelta_angle
        else:
            current_angle = lframe.rotation_angle - llast_proj_frame.rotation_angle
            return abs(current_angle) <= 2 * ldelta_angle, ldelta_angle

    @property
    def frames(self) -> typing.Union[None, tuple]:
        """return tuple of frames. Frames contains"""
        if self._frames is None:
            image_keys = self.image_key
            rotation_angles = self.rotation_angle
            x_translation = self.x_translation
            if x_translation is None and image_keys is not None:
                x_translation = [None] * len(image_keys)
            y_translation = self.y_translation
            if y_translation is None and image_keys is not None:
                y_translation = [None] * len(image_keys)
            z_translation = self.z_translation
            if z_translation is None and image_keys is not None:
                z_translation = [None] * len(image_keys)
            intensity_monitor = self.intensity_monitor
            if intensity_monitor is None and image_keys is not None:
                intensity_monitor = [None] * len(image_keys)
            if image_keys is not None and len(image_keys) != len(rotation_angles):
                raise ValueError(
                    "`rotation_angle` and `image_key` have "
                    "incoherent size (%s vs %s). Unable to "
                    "deduce frame properties" % (len(rotation_angles), len(image_keys))
                )
            self._frames = []

            delta_angle = None
            last_proj_frame = None
            return_already_reach = False

            if image_keys is None:
                # in the case there is no frame / image keys registered at all
                return self._frames

            for i_frame, rot_a, img_key, x_tr, y_tr, z_tr, i_m in zip(
                range(len(rotation_angles)),
                rotation_angles,
                image_keys,
                x_translation,
                y_translation,
                z_translation,
                intensity_monitor,
            ):
                url = DataUrl(
                    file_path=self.master_file,
                    data_slice=(i_frame),
                    data_path=self.get_detector_data_path(),
                    scheme="silx",
                )

                frame = TomoFrame(
                    index=i_frame,
                    url=url,
                    image_key=img_key,
                    rotation_angle=rot_a,
                    x_translation=x_tr,
                    y_translation=y_tr,
                    z_translation=z_tr,
                    intensity_monitor=i_m,
                )
                if self.image_key_control is not None:
                    try:
                        is_control_frame = (
                            ImageKey.from_value(
                                int(self.image_key_control[frame.index])
                            )
                            is ImageKey.ALIGNMENT
                        )
                    except Exception:
                        _logger.warning(
                            f"Unable to deduce if {frame.index} is a control frame. Consider it is not"
                        )
                        is_control_frame = False
                else:
                    return_already_reach, delta_angle = self._is_return_frame(
                        img_key=img_key,
                        lframe=frame,
                        llast_proj_frame=last_proj_frame,
                        ldelta_angle=delta_angle,
                        return_already_reach=return_already_reach,
                    )
                    is_control_frame = return_already_reach
                frame.is_control = is_control_frame
                self._frames.append(frame)
                last_proj_frame = frame
            self._frames = tuple(self._frames)
        return self._frames

    @docstring(TomoScanBase.get_proj_angle_url)
    def get_proj_angle_url(self) -> typing.Union[dict, None]:
        if self.frames is not None:
            res = {}
            for frame in self.frames:
                if frame.image_key is ImageKey.PROJECTION:
                    if frame.is_control is False:
                        res[frame.rotation_angle] = frame.url
                    else:
                        res[str(frame.rotation_angle) + "(1)"] = frame.url
            return res
        else:
            return None

    def _get_sinogram_ref_imp(self, line, subsampling=1):
        """call the reference implementation of get_sinogram.
        Used for unit test and insure the result is the same as get_sinogram
        """
        return TomoScanBase.get_sinogram(self, line=line, subsampling=subsampling)

    @docstring(TomoScanBase)
    def get_sinogram(
        self,
        line,
        subsampling=1,
        norm_method: typing.Union[None, str] = None,
        **kwargs,
    ) -> numpy.array:
        if (
            len(self.projections) is not None
            and self.dim_2 is not None
            and line > self.dim_2
        ) or line < 0:
            raise ValueError("requested line {} is not in the scan".format(line))

        if not isinstance(subsampling, int):
            raise TypeError("subsampling expected to be an int")
        if subsampling <= 0:
            raise ValueError("subsampling expected to be higher than 1")

        if self.projections is not None:
            # get the z line
            with HDF5File(self.master_file, mode="r") as h5f:
                raw_sinogram = h5f[self.get_detector_data_path()][:, line, :]

            assert raw_sinogram.ndim == 2
            ignored_projs = []
            if self.ignore_projections is not None:
                ignored_projs = self.ignore_projections

            def is_pure_projection(frame: TomoFrame):
                return (
                    frame.image_key is ImageKey.PROJECTION
                    and not frame.is_control
                    and frame.index not in ignored_projs
                )

            is_projection_array = numpy.array(
                [is_pure_projection(frame) for frame in self.frames]
            )
            # TODO: simplify & reduce with filter or map ?
            proj_indexes = []
            for x, y in zip(self.frames, is_projection_array):
                if bool(y) is True:
                    proj_indexes.append(x.index)

            raw_sinogram = raw_sinogram[is_projection_array, :]
            assert len(raw_sinogram) == len(
                proj_indexes
            ), "expect to get project indexes of the sinogram"
            assert raw_sinogram.ndim == 2, "sinogram is expected to be 2D"
            # now apply flat field correction on each line
            res = []
            for z_frame_raw_sino, proj_index in zip(raw_sinogram, proj_indexes):
                assert z_frame_raw_sino.ndim == 1
                line_corrected = self.flat_field_correction(
                    projs=(z_frame_raw_sino,),
                    proj_indexes=[
                        proj_index,
                    ],
                    line=line,
                )[0]
                assert isinstance(line_corrected, numpy.ndarray)
                assert line_corrected.ndim == 1
                res.append(line_corrected)
            sinogram = numpy.array(res)
            assert sinogram.ndim == 2
            # apply subsampling (could be speed up but not sure this is useful
            # compare to complexity that we would need to had
            return self._apply_sino_norm(
                sinogram[::subsampling].copy(),
                norm_method=norm_method,
                **kwargs,
            )
        else:
            return None

    def get_detector_data_path(self) -> str:
        return self.entry + "/instrument/detector/data"

    @property
    def projections_compacted(self):
        """
        Return a compacted view of projection frames.

        :return: Dictionary where the key is a list of indices, and the value
            is the corresponding `silx.io.url.DataUrl` with merged data_slice
        :rtype: dict
        """
        if self._projections_compacted is None:
            self._projections_compacted = get_compacted_dataslices(self.projections)
        return self._projections_compacted

    def __str__(self):
        return "hdf5 scan(master_file: %s, entry: %s)" % (
            os.sep.join(os.path.abspath(self.master_file).split(os.sep)[-3:]),
            self.entry,
        )

    @staticmethod
    def _get_value(node: h5py.Group, default_unit: Unit):
        """convert the value contained in the node to the adapted unit.
        Unit can be defined in on of the group attributes. It it is the case
        will pick this unit, otherwise will use the default unit
        """
        if not isinstance(default_unit, Unit):
            raise TypeError(
                f"default_unit must be an instance of {Unit}. Not {type(default_unit)}"
            )
        value = h5py_read_dataset(node)
        if "unit" in node.attrs:
            unit = node.attrs["unit"]
        elif "units" in node.attrs:
            unit = node.attrs["units"]
        else:
            unit = default_unit
        return value * default_unit.from_value(unit).value

    def _check_hdf5scan_validity(self):
        if self.master_file is None:
            raise ValueError("No master file provided")
        if self.entry is None:
            raise ValueError("No entry provided")
        with HDF5File(self.master_file, "r") as h5_file:
            if self._entry not in h5_file:
                raise ValueError(
                    "Given entry %s is not in the master "
                    "file %s" % (self._entry, self.master_file)
                )

    def get_flat_expected_location(self):
        return DataUrl(
            file_path=self.master_file,
            data_path=_get_nexus_paths(self.nexus_version).PROJ_PATH,
        ).path()

    def get_dark_expected_location(self):
        return DataUrl(
            file_path=self.master_file,
            data_path=_get_nexus_paths(self.nexus_version).PROJ_PATH,
        ).path()

    def get_projection_expected_location(self):
        return DataUrl(
            file_path=self.master_file,
            data_path=_get_nexus_paths(self.nexus_version).PROJ_PATH,
        ).path()

    def get_energy_expected_location(self):
        return DataUrl(
            file_path=self.master_file,
            data_path=_get_nexus_paths(self.nexus_version).ENERGY_PATH,
        ).path()

    def get_distance_expected_location(self):
        return DataUrl(
            file_path=self.master_file,
            data_path=_get_nexus_paths(self.nexus_version).ENERGY_PATH,
        ).path()

    def get_pixel_size_expected_location(self):
        return DataUrl(
            file_path=self.master_file,
            data_path=_get_nexus_paths(self.nexus_version).X_PIXEL_SIZE_PATH,
        ).path()

    @docstring(TomoScanBase.get_relative_file)
    def get_relative_file(
        self, file_name: str, with_dataset_prefix=True
    ) -> typing.Optional[str]:
        if self.path is not None:
            if with_dataset_prefix:
                basename = self.get_dataset_basename()
                basename = "_".join((basename, file_name))
                return os.path.join(self.path, basename)
            else:
                return os.path.join(self.path, file_name)
        else:
            return None

    def get_dataset_basename(self) -> str:
        basename, _ = os.path.splitext(self.master_file)
        return os.path.basename(basename)

    @docstring(TomoScanBase)
    def save_reduced_darks(
        self, darks: dict, output_urls: tuple = REDUCED_DARKS_DATAURLS
    ):
        """
        Dump computed dark (median / mean...) into files
        """
        super().save_reduced_darks(darks=darks, output_urls=output_urls)

    @docstring(TomoScanBase)
    def load_reduced_darks(
        self, inputs_urls: tuple = REDUCED_DARKS_DATAURLS, return_as_url: bool = False
    ) -> dict:
        """
        load computed dark (median / mean...) into files
        """
        return super().load_reduced_darks(
            inputs_urls=inputs_urls, return_as_url=return_as_url
        )

    @docstring(TomoScanBase)
    def save_reduced_flats(
        self, flats: dict, output_urls: tuple = REDUCED_FLATS_DATAURLS
    ) -> dict:
        """
        Dump computed flats (median / mean...) into files
        """
        super().save_reduced_flats(flats=flats, output_urls=output_urls)

    @docstring(TomoScanBase)
    def load_reduced_flats(
        self, inputs_urls: tuple = REDUCED_FLATS_DATAURLS, return_as_url: bool = False
    ) -> dict:
        """
        load computed dark (median / mean...) into files
        """
        return super().load_reduced_flats(
            inputs_urls=inputs_urls, return_as_url=return_as_url
        )

    @docstring(TomoScanBase.compute_reduced_flats)
    def compute_reduced_flats(
        self, reduced_method="median", overwrite=True, output_dtype=numpy.float32
    ):
        return super().compute_reduced_flats(
            reduced_method=reduced_method,
            overwrite=overwrite,
            output_dtype=output_dtype,
        )

    @docstring(TomoScanBase.compute_reduced_flats)
    def compute_reduced_darks(
        self, reduced_method="mean", overwrite=True, output_dtype=numpy.float32
    ):
        return super().compute_reduced_darks(
            reduced_method=reduced_method,
            overwrite=overwrite,
            output_dtype=output_dtype,
        )

    @staticmethod
    @docstring(TomoScanBase)
    def from_identifier(identifier):
        """Return the Dataset from a identifier"""
        if not isinstance(identifier, HDF5TomoScanIdentifier):
            raise TypeError(
                f"identifier should be an instance of {HDF5TomoScanIdentifier}"
            )
        return HDF5TomoScan(scan=identifier.file_path, entry=identifier.data_path)

    @docstring(TomoScanBase)
    def get_identifier(self) -> ScanIdentifier:
        return HDF5TomoScanIdentifier(
            object=self, hdf5_file=self.master_file, entry=self.entry
        )


class HDF5XRD3DScan(HDF5TomoScan):
    """
    Class used to read nexus file representing a 3D-XRD acquisition.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rocking = None
        self._base_tilt = None

    @property
    def rocking(self) -> typing.Union[None, tuple]:
        if self._rocking is None:
            self._check_hdf5scan_validity()
            with HDF5File(self.master_file, "r") as h5_file:
                _rocking = h5py_read_dataset(
                    h5_file[self._entry][self.nexus_path.ROCKING_PATH]
                )
                # cast in float
                self._rocking = tuple([float(r) for r in _rocking])
        return self._rocking

    @property
    def base_tilt(self) -> typing.Union[None, tuple]:
        if self._base_tilt is None:
            self._check_hdf5scan_validity()
            with HDF5File(self.master_file, "r") as h5_file:
                _base_tilt = h5py_read_dataset(
                    h5_file[self._entry][self.nexus_path.BASE_TILT_PATH]
                )
                # cast in float
                self._base_tilt = tuple([float(bt) for bt in _base_tilt])
        return self._base_tilt

    @property
    def frames(self) -> typing.Union[None, tuple]:
        """return tuple of frames. Frames contains"""
        if self._frames is None:
            image_keys = self.image_key
            rotation_angles = self.rotation_angle
            x_translation = self.x_translation
            if x_translation is None and image_keys is not None:
                x_translation = [None] * len(image_keys)
            y_translation = self.y_translation
            if y_translation is None and image_keys is not None:
                y_translation = [None] * len(image_keys)
            z_translation = self.z_translation
            if z_translation is None and image_keys is not None:
                z_translation = [None] * len(image_keys)
            rocking = self.rocking
            if rocking is None and image_keys is not None:
                rocking = [None] * len(image_keys)
            base_tilt = self.base_tilt
            if base_tilt is None and image_keys is not None:
                base_tilt = [None] * len(image_keys)
            if image_keys is not None and len(image_keys) != len(rotation_angles):
                raise ValueError(
                    "`rotation_angle` and `image_key` have "
                    "incoherent size (%s vs %s). Unable to "
                    "deduce frame properties" % (len(rotation_angles), len(image_keys))
                )
            self._frames = []

            delta_angle = None
            last_proj_frame = None
            return_already_reach = False
            for i_frame, rot_a, img_key, x_tr, y_tr, z_tr, rck, bt in zip(
                range(len(rotation_angles)),
                rotation_angles,
                image_keys,
                x_translation,
                y_translation,
                z_translation,
                rocking,
                base_tilt,
            ):
                url = DataUrl(
                    file_path=self.master_file,
                    data_slice=(i_frame),
                    data_path=self.get_detector_data_path(),
                    scheme="silx",
                )

                frame = XRD3DFrame(
                    index=i_frame,
                    url=url,
                    image_key=img_key,
                    rotation_angle=rot_a,
                    x_translation=x_tr,
                    y_translation=y_tr,
                    z_translation=z_tr,
                    rocking=rck,
                    base_tilt=bt,
                )
                if self.image_key_control is not None:
                    try:
                        is_control_frame = (
                            ImageKey.from_value(
                                int(self.image_key_control[frame.index])
                            )
                            is ImageKey.ALIGNMENT
                        )
                    except Exception:
                        _logger.warning(
                            f"Unable to deduce if {frame.index} is a control frame. Consider it is not"
                        )
                        is_control_frame = False
                else:
                    return_already_reach, delta_angle = self._is_return_frame(
                        img_key=img_key,
                        lframe=frame,
                        llast_proj_frame=last_proj_frame,
                        ldelta_angle=delta_angle,
                        return_already_reach=return_already_reach,
                    )
                    is_control_frame = return_already_reach
                frame._is_control_frame = is_control_frame
                self._frames.append(frame)
                last_proj_frame = frame
            self._frames = tuple(self._frames)
        return self._frames


class TomoFrame:
    """class to store all metadata information of a NXTomo frame"""

    def __init__(
        self,
        index: int,
        url: typing.Union[None, DataUrl] = None,
        image_key: typing.Union[None, ImageKey, int] = None,
        rotation_angle: typing.Union[None, float] = None,
        is_control_proj: bool = False,
        x_translation: typing.Union[None, float] = None,
        y_translation: typing.Union[None, float] = None,
        z_translation: typing.Union[None, float] = None,
        intensity_monitor: typing.Union[None, float] = None,
    ):
        assert type(index) is int
        self._index = index
        if image_key is not None:
            self._image_key = ImageKey.from_value(image_key)
        else:
            self._image_key = None
        self._rotation_angle = rotation_angle
        self._url = url
        self._is_control_frame = is_control_proj
        self._data = None
        self._x_translation = x_translation
        self._y_translation = y_translation
        self._z_translation = z_translation
        self._intensity_monitor = intensity_monitor

    @property
    def index(self) -> int:
        return self._index

    @property
    def image_key(self) -> ImageKey:
        return self._image_key

    @image_key.setter
    def image_key(self, image_key: ImageKey) -> None:
        if not isinstance(image_key, ImageKey):
            raise TypeError(f"{image_key} is expected to be an instance of {ImageKey}")
        self._image_key = image_key

    @property
    def rotation_angle(self) -> float:
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, angle: float) -> None:
        self._rotation_angle = angle

    @property
    def url(self) -> DataUrl:
        return self._url

    @property
    def is_control(self) -> bool:
        return self._is_control_frame

    @property
    def x_translation(self):
        return self._x_translation

    @property
    def y_translation(self):
        return self._y_translation

    @property
    def z_translation(self):
        return self._z_translation

    @property
    def intensity_monitor(self):
        return self._intensity_monitor

    @is_control.setter
    def is_control(self, is_return: bool):
        self._is_control_frame = is_return

    def __str__(self):
        return (
            "Frame {index},: image_key: {image_key},"
            "is_control: {is_control},"
            "rotation_angle: {rotation_angle},"
            "x_translation: {x_translation},"
            "y_translation: {y_translation},"
            "z_translation: {z_translation},"
            "url: {url}".format(
                index=self.index,
                image_key=self.image_key,
                is_control=self.is_control,
                rotation_angle=self.rotation_angle,
                url=self.url.path(),
                x_translation=self.x_translation,
                y_translation=self.y_translation,
                z_translation=self.z_translation,
            )
        )


class XRD3DFrame(TomoFrame):
    """class to store all metadata information of a 3d-xrd nexus frame"""

    def __init__(
        self,
        index: int,
        url: typing.Union[None, DataUrl] = None,
        image_key: typing.Union[None, ImageKey, int] = None,
        rotation_angle: typing.Union[None, float] = None,
        is_control_proj: bool = False,
        x_translation: typing.Union[None, float] = None,
        y_translation: typing.Union[None, float] = None,
        z_translation: typing.Union[None, float] = None,
        rocking: typing.Union[None, float] = None,
        base_tilt: typing.Union[None, float] = None,
    ):
        super().__init__(
            index=index,
            url=url,
            image_key=image_key,
            rotation_angle=rotation_angle,
            is_control_proj=is_control_proj,
            x_translation=x_translation,
            y_translation=y_translation,
            z_translation=z_translation,
        )
        self._rocking = rocking
        self._base_tilt = base_tilt

    @property
    def rocking(self) -> typing.Union[None, float]:
        return self._rocking

    @property
    def base_tilt(self) -> typing.Union[None, float]:
        return self._base_tilt

    def __str__(self):
        p_str = super(XRD3DFrame, self).__str__()
        p_str += "rocking: {rocking}," "base-tilt: {base_tilt}".format(
            rocking=self.rocking, base_tilt=self.base_tilt
        )
        return p_str
