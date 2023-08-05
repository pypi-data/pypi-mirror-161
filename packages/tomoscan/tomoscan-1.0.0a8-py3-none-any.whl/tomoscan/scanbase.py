# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016- 2020 European Synchrotron Radiation Facility
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
"""This modules contains base class for TomoScanBase"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "09/10/2019"


import fabio
import os
import typing
import logging
import h5py
import numpy
from typing import Union, Iterable, Optional
from collections import OrderedDict
import pathlib
from tomoscan.identifier import ScanIdentifier
from tomoscan.io import HDF5File
from tomoscan.utils import BoundingBox1D
from .unitsystem.metricsystem import MetricSystem
from silx.utils.enum import Enum as _Enum
from silx.io.url import DataUrl
from silx.io.utils import get_data
import silx.io.utils
from math import ceil
from .progress import Progress
from bisect import bisect_left
from tomoscan.normalization import (
    IntensityNormalization,
    Method as _IntensityMethod,
    normalize_chebyshev_2D,
    normalize_lsqr_spline_2D,
)
from silx.utils.deprecation import deprecated
from .tomoobject import TomoObject

_logger = logging.getLogger(__name__)


class FOV(_Enum):
    """Possible existing field of view"""

    @classmethod
    def from_value(cls, value):
        if isinstance(value, str):
            value = value.lower().title()

        return super().from_value(value)

    FULL = "Full"
    HALF = "Half"


# keep compatibility for some time
_FOV = FOV


class SourceType(_Enum):
    SPALLATION_NEUTRON = "Spallation Neutron Source"
    PULSED_REACTOR_NEUTRON_SOURCE = "Pulsed Reactor Neutron Source"
    REACTOR_NEUTRON_SOURCE = "Reactor Neutron Source"
    SYNCHROTRON_X_RAY_SOURCE = "Synchrotron X-ray Source"
    PULSED_MUON_SOURCE = "Pulsed Muon Source"
    ROTATING_ANODE_X_RAY = "Rotating Anode X-ray"
    FIXED_TUBE_X_RAY = "Fixed Tube X-ray"
    UV_LASER = "UV Laser"
    FREE_ELECTRON_LASER = "Free-Electron Laser"
    OPTICAL_LASER = "Optical Laser"
    ION_SOURCE = "Ion Source"
    UV_PLASMA_SOURCE = "UV Plasma Source"
    METAL_JET_X_RAY = "Metal Jet X-ray"


class Source:
    """Information regarding the x-ray storage ring/facility"""

    def __init__(self, name=None, type=None):
        self._name = name
        self._type = type

    @property
    def name(self) -> Union[None, str]:
        return self._name

    @name.setter
    def name(self, name: Union[str, None]):
        if not isinstance(name, (str, type(None))):
            raise TypeError("name is expected to be None or a str")
        self._name = name

    @property
    def type(self) -> Union[None, SourceType]:
        return self._type

    @type.setter
    def type(self, type_: Union[None, str, SourceType]):
        if type_ is None:
            self._type = None
        else:
            type_ = SourceType.from_value(type_)
            self._type = type_

    def __str__(self):
        return f"source (name: {self.name}, type: {self.type})"


class ComputeMethod(_Enum):
    MEAN = "mean"  # compute the mean of dark / flat frames serie
    MEDIAN = "median"  # compute the median of dark / flat frames serie
    FIRST = "first"  # take the first frame of the dark / flat serie
    LAST = "last"  # take the last frame of the dark / flat serie


class TomoScanBase(TomoObject):
    """
    Base Class representing a scan.
    It is used to obtain core information regarding an aquisition like
    projections, dark and flat field...

    :param scan: path to the root folder containing the scan.
    :type scan: Union[str,None]
    """

    DICT_TYPE_KEY = "type"

    DICT_PATH_KEY = "path"

    _SCHEME = None
    """scheme to read data url for this type of acquisition"""

    FRAME_REDUCER_CLASS = None
    """Frame reducer class to be use in order to compute reduced darks and reduced flats"""

    def __init__(
        self,
        scan: Union[None, str],
        type_: str,
        ignore_projections: Union[None, Iterable] = None,
    ):
        super().__init__()
        self.path = scan
        self._type = type_
        self._normed_flats = None
        """darks normed. When set a dict is expected with index as the key
           and median or median of darks serie as value"""
        self._normed_darks = None
        """flats normed. When set a dict is expected with index as the key
           and median or median of darks serie as value"""
        self._notify_ffc_rsc_missing = True
        """Should we notify the user if ffc fails because cannot find dark or
        flat. Used to avoid several warnings. Only display one"""
        self._projections = None
        self._alignment_projections = None
        self._flats_weights = None
        """list flats indexes to use for flat field correction and associate
        weights"""
        self.ignore_projections = ignore_projections
        """Extra information for normalization"""
        self._intensity_monitor = None
        """monitor of the intensity during acquisition. Can be a diode
        for example"""
        self._source = None
        self._intensity_normalization = IntensityNormalization()
        """Extra information for normalization"""
        self._electric_current = None

    def clear_caches(self):
        """clear caches. Might be call if some data changed after
        first read of data or metadata"""
        self._notify_ffc_rsc_missing = True
        self._alignment_projections = None
        self._flats_weights = None

    @property
    def normed_darks(self):
        return self._normed_darks

    def set_normed_darks(self, darks):
        self._normed_darks = darks

    @property
    def normed_flats(self):
        return self._normed_flats

    def set_normed_flats(self, flats):
        self._normed_flats = flats

    @property
    def path(self) -> Union[None, str]:
        """

        :return: path of the scan root folder.
        :rtype: Union[str,None]
        """
        return self._path

    @path.setter
    def path(self, path: Union[str, None]) -> None:
        if path is None:
            self._path = path
        else:
            if not isinstance(path, (str, pathlib.Path)):
                raise TypeError(
                    f"path is expected to be a str or a pathlib.Path not {type(path)}"
                )
            self._path = os.path.realpath(str(path))

    @property
    def type(self) -> str:
        """

        :return: type of the scanBase (can be 'edf' or 'hdf5' for now).
        :rtype: str
        """
        return self._type

    @staticmethod
    def is_tomoscan_dir(directory: str, **kwargs) -> bool:
        """
        Check if the given directory is holding an acquisition

        :param str directory:
        :return: does the given directory contains any acquisition
        :rtype: bool
        """
        raise NotImplementedError("Base class")

    def is_abort(self, **kwargs) -> bool:
        """

        :return: True if the acquisition has been abort
        :rtype: bool
        """
        raise NotImplementedError("Base class")

    @property
    def source(self):
        return self._source

    @property
    def flats(self) -> Union[None, dict]:
        """list of flats files"""
        return self._flats

    @flats.setter
    def flats(self, flats: Union[None, dict]) -> None:
        self._flats = flats

    @property
    def darks(self) -> Union[None, dict]:
        """list of darks files"""
        return self._darks

    @darks.setter
    def darks(self, darks: Union[None, dict]) -> None:
        self._darks = darks

    @property
    def projections(self) -> Union[None, dict]:
        """if found dict of projections urls with index during acquisition as
        key"""
        return self._projections

    @projections.setter
    def projections(self, projections: dict) -> None:
        self._projections = projections

    @property
    def alignment_projections(self) -> Union[None, dict]:
        """
        dict of projections made for alignment with acquisition index as key
        None if not found
        """
        return self._alignment_projections

    @alignment_projections.setter
    def alignment_projections(self, alignment_projs):
        self._alignment_projections = alignment_projs

    @property
    def dark_n(self) -> Union[None, int]:
        raise NotImplementedError("Base class")

    @property
    def tomo_n(self) -> Union[None, int]:
        """number of projection WITHOUT the return projections"""
        raise NotImplementedError("Base class")

    @deprecated(replacement="flat_n", since_version="0.7.0")
    @property
    def ref_n(self) -> Union[None, int]:
        return self.flat_n

    @property
    def flat_n(self) -> Union[None, int]:
        raise NotImplementedError("Base class")

    @property
    def pixel_size(self) -> Union[None, float]:
        raise NotImplementedError("Base class")

    def get_pixel_size(self, unit="m") -> Union[None, float]:
        if self.pixel_size:
            return self.pixel_size / MetricSystem.from_value(unit).value
        else:
            return None

    @property
    def instrument_name(self) -> Union[None, str]:
        """

        :return: instrument name
        """
        raise NotImplementedError("Base class")

    @property
    def dim_1(self) -> Union[None, int]:
        raise NotImplementedError("Base class")

    @property
    def dim_2(self) -> Union[None, int]:
        raise NotImplementedError("Base class")

    @property
    def ff_interval(self) -> Union[None, int]:
        raise NotImplementedError("Base class")

    @property
    def scan_range(self) -> Union[None, int]:
        raise NotImplementedError("Base class")

    @property
    def energy(self) -> Union[None, float]:
        """

        :return: incident beam energy in keV
        """
        raise NotImplementedError("Base class")

    @property
    def intensity_monitor(self):
        raise NotImplementedError("Base class")

    @property
    def distance(self) -> Union[None, float]:
        """

        :return: sample / detector distance in meter
        """
        raise NotImplementedError("Base class")

    @property
    def field_of_view(self):
        """

        :return: field of view of the scan. None if unknow else Full or Half
        """
        raise NotImplementedError("Base class")

    @property
    def estimated_cor_frm_motor(self):
        """

        :return: Estimated center of rotation estimated from motor position
        :rtype: Union[None, float]. If return value is in [-frame_width, +frame_width]
        """
        raise NotImplementedError("Base class")

    @property
    def x_translation(self) -> typing.Union[None, tuple]:
        raise NotImplementedError("Base class")

    @property
    def y_translation(self) -> typing.Union[None, tuple]:
        raise NotImplementedError("Base class")

    @property
    def z_translation(self) -> typing.Union[None, tuple]:
        raise NotImplementedError("Base class")

    def get_distance(self, unit="m") -> Union[None, float]:
        """

        :param Union[MetricSystem, str] unit: unit requested for the distance
        :return: sample / detector distance with the requested unit
        """
        if self.distance:
            return self.distance / MetricSystem.from_value(unit).value
        else:
            return None

    @property
    def x_pixel_size(self) -> Optional[float]:
        raise NotImplementedError("Base class")

    @property
    def y_pixel_size(self) -> Optional[float]:
        raise NotImplementedError("Base class")

    @property
    def magnification(self) -> Optional[float]:
        raise NotImplementedError("Base class")

    def get_bounding_box(self, axis: typing.Union[str, int]) -> BoundingBox1D:
        """
        Return the bounding box covered by the scan (only take into account the projections).
        axis is expected to be in (0, 1, 2) or (x==0, y==1, z==2)
        """
        raise NotImplementedError("Base class")

    def update(self) -> None:
        """Parse the root folder and files to update informations"""
        raise NotImplementedError("Base class")

    @property
    def sequence_name(self):
        """Return the sequence name"""
        raise NotImplementedError("Base class")

    @property
    def sample_name(self):
        """Return the sample name"""
        raise NotImplementedError("Base class")

    @property
    def group_size(self):
        """Used in the case of zseries for example. Return the number of
        sequence expected on the acquisition"""
        raise NotImplementedError("Base class")

    @property
    def electric_current(self) -> tuple:
        """Return the sample name"""
        raise NotImplementedError("Base class")

    @electric_current.setter
    def electric_current(self, current: Optional[tuple]) -> None:
        if not isinstance(current, (type(None), tuple)):
            raise TypeError(
                f"current is expected to be None or a tuple. Not {type(current)}"
            )
        self._electric_current = current

    def x_flipped(self) -> bool:
        """
        return True if  the frames are flip through x
        """
        raise NotImplementedError("Base class")

    @property
    def y_flipped(self) -> bool:
        """
        return True if  the frames are flip through y
        """
        raise NotImplementedError("Base class")

    def get_x_flipped(self, default=None):
        if self.x_flipped is None:
            return default
        else:
            return self.x_flipped

    def get_y_flipped(self, default=None):
        if self.y_flipped is None:
            return default
        else:
            return self.y_flipped

    def get_identifier(self) -> ScanIdentifier:
        """
        return the dataset identifier of the scan.
        The identifier is insure to be unique for each scan and
        allow the user to store the scan as a string identifier
        and to retrieve it later from this single identifier.
        """
        raise NotImplementedError("Base class")

    def to_dict(self) -> dict:
        """

        :return: convert the TomoScanBase object to a dictionary.
                 Used to serialize the object for example.
        :rtype: dict
        """
        res = dict()
        res[self.DICT_TYPE_KEY] = self.type
        res[self.DICT_PATH_KEY] = self.path
        return res

    def load_from_dict(self, _dict: dict):
        """
        Load properties contained in the dictionnary.

        :param _dict: dictionary to load
        :type _dict: dict
        :return: self
        :raises: ValueError if dict is invalid
        """
        raise NotImplementedError("Base class")

    def equal(self, other) -> bool:
        """

        :param :class:`.ScanBase` other: instance to compare with
        :return: True if instance are equivalent

        ..note:: we cannot use the __eq__ function because this object need to be
                 pickable
        """
        return (
            isinstance(other, self.__class__)
            or isinstance(self, other.__class__)
            and self.type == other.type
            and self.path == other.path
        )

    def get_proj_angle_url(self) -> dict:
        """
        return a dictionary of all the projection. key is the angle of the
        projection and value is the url.

        Keys are int for 'standard' projections and strings for return
        projections.

        :return dict: angles as keys, radios as value.
        """
        raise NotImplementedError("Base class")

    @staticmethod
    def map_urls_on_scan_range(urls, n_projection, scan_range) -> dict:
        """
        map given urls to an angle regarding scan_range and number of projection.
        We take the hypothesis that 'extra projection' are taken regarding the
        'id19' policy:

         * If the acquisition has a scan range of 360 then:

            * if 4 extra projection, the angles are (270, 180, 90, 0)

            * if 5 extra projection, the angles are (360, 270, 180, 90, 0)

         * If the acquisition has a scan range of 180 then:

            * if 2 extra projections: the angles are (90, 0)

            * if 3 extra projections: the angles are (180, 90, 0)

        ..warning:: each url should contain only one radio.

        :param urls: dict with all the urls. First url should be
                     the first radio acquire, last url should match the last
                     radio acquire.
        :type urls: dict
        :param n_projection: number of projection for the sample.
        :type n_projection: int
        :param scan_range: acquisition range (usually 180 or 360)
        :type scan_range: float
        :return: angle in degree as key and url as value
        :rtype: dict

        :raises: ValueError if the number of extra images found and scan_range
                 are incoherent
        """
        assert n_projection is not None
        ordered_url = OrderedDict(sorted(urls.items(), key=lambda x: x))

        res = {}
        # deal with the 'standard' acquisitions
        for proj_i in range(n_projection):
            url = list(ordered_url.values())[proj_i]
            if n_projection == 1:
                angle = 0.0
            else:
                angle = proj_i * scan_range / (n_projection - 1)
            if proj_i < len(urls):
                res[angle] = url

        if len(urls) > n_projection:
            # deal with extra images (used to check if the sampled as moved for
            # example)
            extraImgs = list(ordered_url.keys())[n_projection:]
            if len(extraImgs) in (4, 5):
                if scan_range < 360:
                    _logger.warning(
                        "incoherent data information to retrieve"
                        "scan extra images angle"
                    )
                elif len(extraImgs) == 4:
                    res["270(1)"] = ordered_url[extraImgs[0]]
                    res["180(1)"] = ordered_url[extraImgs[1]]
                    res["90(1)"] = ordered_url[extraImgs[2]]
                    res["0(1)"] = ordered_url[extraImgs[3]]
                else:
                    res["360(1)"] = ordered_url[extraImgs[0]]
                    res["270(1)"] = ordered_url[extraImgs[1]]
                    res["180(1)"] = ordered_url[extraImgs[2]]
                    res["90(1)"] = ordered_url[extraImgs[3]]
                    res["0(1)"] = ordered_url[extraImgs[4]]
            elif len(extraImgs) in (2, 3):
                if scan_range > 180:
                    _logger.warning(
                        "incoherent data information to retrieve"
                        "scan extra images angle"
                    )
                elif len(extraImgs) == 3:
                    res["180(1)"] = ordered_url[extraImgs[0]]
                    res["90(1)"] = ordered_url[extraImgs[1]]
                    res["0(1)"] = ordered_url[extraImgs[2]]
                else:
                    res["90(1)"] = ordered_url[extraImgs[0]]
                    res["0(1)"] = ordered_url[extraImgs[1]]
            elif len(extraImgs) == 1:
                res["0(1)"] = ordered_url[extraImgs[0]]
            else:
                raise ValueError(
                    "incoherent data information to retrieve scan" "extra images angle"
                )
        return res

    @property
    def intensity_normalization(self):
        return self._intensity_normalization

    @intensity_normalization.setter
    def intensity_normalization(self, value):
        try:
            method = _IntensityMethod.from_value(value)
        except ValueError:
            pass
        else:
            self._intensity_normalization.method = method

    def get_sinogram(
        self,
        line,
        subsampling=1,
        norm_method: typing.Union[None, str] = None,
        **kwargs,
    ):
        """
        extract the sinogram from projections

        :param int line: which sinogram we want
        :param int subsampling: subsampling to apply. Allows to skip some io

        :return: computed sinogram from projections
        :rtype: numpy.array
        """
        if (
            self.projections is not None
            and self.dim_2 is not None
            and line > self.dim_2
        ) or line < 0:
            raise ValueError("requested line {} is not in the scan".format(line))
        if self.projections is not None:
            y_dim = ceil(len(self.projections) / subsampling)
            sinogram = numpy.empty((y_dim, self.dim_1))
            _logger.debug(
                "compute sinogram for line {} of {} (subsampling: {})".format(
                    line, self.path, subsampling
                )
            )
            advancement = Progress(
                name="compute sinogram for {}, line={},"
                "sampling={}".format(os.path.basename(self.path), line, subsampling)
            )
            advancement.setMaxAdvancement(len(self.projections))
            projections = self.projections
            o_keys = list(projections.keys())
            o_keys.sort()
            for i_proj, proj_index in enumerate(o_keys):
                if i_proj % subsampling == 0:
                    proj_url = projections[proj_index]
                    proj = silx.io.utils.get_data(proj_url)
                    proj = self.flat_field_correction(
                        projs=[proj], proj_indexes=[proj_index]
                    )[0]
                    sinogram[i_proj // subsampling] = proj[line]
                advancement.increaseAdvancement(1)

            return self._apply_sino_norm(
                sinogram,
                norm_method=norm_method,
                subsampling=subsampling,
                **kwargs,
            )
        else:
            return None

    def _apply_sino_norm(
        self, sinogram, norm_method: _IntensityMethod, subsampling=1, **kwargs
    ):
        if norm_method is not None:
            norm_method = _IntensityMethod.from_value(norm_method)
        if norm_method in (None, _IntensityMethod.NONE):
            return sinogram
        elif norm_method is _IntensityMethod.CHEBYSHEV:
            return normalize_chebyshev_2D(sinogram)
        elif norm_method is _IntensityMethod.LSQR_SPLINE:
            return normalize_lsqr_spline_2D(sinogram)
        elif norm_method in (_IntensityMethod.DIVISION, _IntensityMethod.SUBTRACTION):
            if "value" in kwargs:
                _logger.info("Apply sinogram normalization from 'value' key")
                if numpy.isscalar(kwargs["value"]):
                    return sinogram - kwargs["value"]
                else:
                    for sl, sc in zip(
                        range(len(sinogram)), kwargs["value"][::subsampling]
                    ):
                        sinogram[sl] = sinogram[sl] - sc
                    return sinogram
            elif "dataset_url" in kwargs:
                _logger.info("Apply sinogram normalization from 'dataset_url' key")
                intensities = DataUrl(path=kwargs["dataset_url"])
                if intensities is None:
                    raise ValueError("No dataset for intensity monitoring found")
                else:
                    i_values = set(intensities.values())
                    if len(i_values) == 1 and list(i_values)[0] is None:
                        raise ValueError("No dataset for intensity monitoring found")

                    intensities = [
                        intensities[key] for key in sorted(intensities.keys())
                    ]
                    intensities = intensities[::subsampling]
                    for sl, sc in zip(range(len(sinogram)), intensities):
                        if sc is None:
                            _logger.warning(
                                "Intensity not found for line {sl}. won't normalize this line"
                            )
                            sinogram[sl] = sinogram[sl]
                        else:
                            sinogram[sl] = sinogram[sl] - sc
                    return sinogram
            else:
                raise KeyError(
                    f"{norm_method.value} requires a value or an url to be computed"
                )
        else:
            raise ValueError("norm method not handled", norm_method)

    def _frame_flat_field_correction(
        self,
        data: typing.Union[numpy.ndarray, DataUrl],
        dark,
        flat_weights: dict,
        line: Union[None, int] = None,
    ):
        """
        compute flat field correction for a provided data from is index
        one dark and two flats (require also indexes)
        """
        assert isinstance(data, (numpy.ndarray, DataUrl))
        if isinstance(data, DataUrl):
            data = get_data(data)
        can_process = True
        if flat_weights in (None, {}):
            if self._notify_ffc_rsc_missing:
                _logger.error(
                    f"cannot make flat field correction, flat not found from {self} or weights not computed"
                )
            can_process = False
        else:
            for flat_index, _ in flat_weights.items():
                if flat_index not in self.normed_flats:
                    _logger.error(
                        f"flat {flat_index} has been removed, unable to apply flat field"
                    )
                    can_process = False
                elif (
                    self.normed_flats is not None
                    and self.normed_flats[flat_index].ndim != 2
                ):
                    _logger.error(
                        "cannot make flat field correction, flat should be of dimension 2"
                    )
                    can_process = False

        if can_process is False:
            self._notify_ffc_rsc_missing = False
            if line is None:
                return data
            else:
                return data[line]

        if len(flat_weights) == 1:
            flat_value = self.normed_flats[list(flat_weights.keys())[0]]
        elif len(flat_weights) == 2:
            flat_keys = list(flat_weights.keys())
            flat_1 = flat_keys[0]
            flat_2 = flat_keys[1]
            flat_value = (
                self.normed_flats[flat_1] * flat_weights[flat_1]
                + self.normed_flats[flat_2] * flat_weights[flat_2]
            )
        else:
            raise ValueError(
                "no more than two flats are expected and"
                "at least one shuold be provided"
            )
        if line is None:
            assert data.ndim == 2
            div = flat_value - dark
            div[div == 0] = 1.0
            return (data - dark) / div
        else:
            assert data.ndim == 1
            div = flat_value[line] - dark[line]
            div[div == 0] = 1
            return (data - dark[line]) / div

    def flat_field_correction(
        self,
        projs: typing.Iterable,
        proj_indexes: typing.Iterable,
        line: Union[None, int] = None,
    ):
        """Apply flat field correction on the given data

        :param Iterable projs: list of projection (numpy array) to apply correction
                              on
        :param Iterable data proj_indexes: list of indexes of the projection in
                                         the acquisition sequence. Values can
                                         be int or None. If None then the
                                         index take will be the one in the
                                         middle of the flats taken.
        :param line: index of the line to apply flat filed. If not provided
                     consider we want to apply flat filed on the entire frame
        :type line: None or int
        :return: corrected data: list of numpy array
        :rtype: list
        """
        assert isinstance(projs, typing.Iterable)
        assert isinstance(proj_indexes, typing.Iterable)
        assert isinstance(line, (type(None), int))

        def has_missing_keys():
            if proj_indexes is None:
                return False
            for proj_index in proj_indexes:
                if proj_index not in self._flats_weights:
                    return False
            return True

        def return_without_correction():
            def load_data(proj):
                if isinstance(proj, DataUrl):
                    return get_data(proj)
                else:
                    return proj

            if line is not None:
                res = [
                    load_data(proj)[line] if isinstance(proj, DataUrl) else proj
                    for proj in projs
                ]
            else:
                res = [
                    load_data(proj) if isinstance(proj, DataUrl) else proj
                    for proj in projs
                ]

            return res

        if self._flats_weights in (None, {}) or has_missing_keys():
            self._flats_weights = self._get_flats_weights()

        if self._flats_weights in (None, {}):
            if self._notify_ffc_rsc_missing:
                _logger.error("Unable to compute flat weights")
                self._notify_ffc_rsc_missing = False
            return return_without_correction()

        darks = self._normed_darks
        if darks is not None and len(darks) > 0:
            # take only one dark into account for now
            dark = list(darks.values())[0]
        else:
            dark = None

        if dark is None:
            if self._notify_ffc_rsc_missing:
                _logger.error("cannot make flat field correction, dark not found")
                self._notify_ffc_rsc_missing = False
            return return_without_correction()

        if dark is not None and dark.ndim != 2:
            if self._notify_ffc_rsc_missing:
                _logger.error(
                    "cannot make flat field correction, dark should be of "
                    "dimension 2"
                )
                self._notify_ffc_rsc_missing = False
                return return_without_correction()
        return numpy.array(
            [
                self._frame_flat_field_correction(
                    data=frame,
                    dark=dark,
                    flat_weights=self._flats_weights[proj_i]
                    if proj_i in self._flats_weights
                    else None,
                    line=line,
                )
                for frame, proj_i in zip(projs, proj_indexes)
            ]
        )

    def _get_flats_weights(self):
        """compute flats indexes to use and weights for each projection"""
        if self.normed_flats is None:
            return None
        flats_indexes = sorted(self.normed_flats.keys())

        def get_weights(proj_index):
            if proj_index in flats_indexes:
                return {proj_index: 1.0}
            pos = bisect_left(flats_indexes, proj_index)
            left_pos = flats_indexes[pos - 1]
            if pos == 0:
                return {flats_indexes[0]: 1.0}
            elif pos > len(flats_indexes) - 1:
                return {flats_indexes[-1]: 1.0}
            else:
                right_pos = flats_indexes[pos]
                delta = right_pos - left_pos
                return {
                    left_pos: 1 - (proj_index - left_pos) / delta,
                    right_pos: 1 - (right_pos - proj_index) / delta,
                }

        if self.normed_flats is None or len(self.normed_flats) == 0:
            return {}
        else:
            res = {}
            for proj_index in self.projections:
                res[proj_index] = get_weights(proj_index=proj_index)
            return res

    def get_projections_intensity_monitor(self):
        """return intensity monitor values for projections"""
        raise NotImplementedError("Base class")

    def get_flat_expected_location(self):
        raise NotImplementedError("Base class")

    def get_dark_expected_location(self):
        raise NotImplementedError("Base class")

    def get_projection_expected_location(self):
        raise NotImplementedError("Base class")

    def get_energy_expected_location(self):
        raise NotImplementedError("Base class")

    def get_distance_expected_location(self):
        raise NotImplementedError("Base class")

    def get_pixel_size_expected_location(self):
        raise NotImplementedError("Base class")

    def get_relative_file(
        self, file_name: str, with_dataset_prefix=True
    ) -> Optional[str]:
        """
        :param str file_name: name of the file to create
        :param bool with_dataset_prefix: If True will prefix the requested file by the dataset name like datasetname_file_name

        :return: path to the requested file according to the 'Scan' / 'dataset' location. Return none if Scan has no path
        :rtype: Optional[str]
        """
        raise NotImplementedError("Base class")

    def get_dataset_basename(self) -> str:
        raise NotImplementedError("Base class")

    def _dump_frame_dict(self, frames: dict, output_urls):
        """
        utils function to save some frames in set of output_urls
        """
        if not isinstance(frames, dict):
            raise TypeError(
                f"inputs `frames` is expected to be a dict not {type(frames)}"
            )
        if not isinstance(output_urls, (list, tuple, set)):
            raise TypeError(
                f"output_urls is expected to be a tuple not a {type(output_urls)}"
            )
        if self.path is None:
            raise ValueError("No dataset path provided")

        entry = "entry"
        if hasattr(self, "entry"):
            entry = self.entry
        for url in output_urls:
            cleaned_hdf5_parent_grp = False
            # small hack to insure 'flats' or 'darks' group are cleaned when start to write in
            for idx, frame in frames.items():
                if not isinstance(frame, numpy.ndarray):
                    raise TypeError("frames are expected to be 2D numpy.ndarray")
                elif frame.ndim == 3 and frame.shape[0] == 1:
                    frame = frame.reshape([frame.shape[1], frame.shape[2]])
                elif frame.ndim != 2:
                    raise ValueError("frames are expected to be 2D numpy.ndarray")
                idx_zfill4 = str(idx).zfill(4)
                data_path = url.data_path()
                if data_path is not None:
                    path_to_clean = data_path.format(
                        index="{index}", index_zfill4="{index_zfill4}", entry=entry
                    )
                    path_to_clean = path_to_clean.replace("{index}", "")
                    path_to_clean = path_to_clean.replace("{index_zfill4}", "")
                    if path_to_clean.endswith("/"):
                        path_to_clean = path_to_clean[:-1]

                    data_path = data_path.format(
                        index=str(idx), index_zfill4=idx_zfill4, entry=entry
                    )

                file_path = url.file_path()
                if file_path is not None:
                    file_path = file_path.format(
                        index=str(idx),
                        index_zfill4=idx_zfill4,
                        entry=entry,
                        scan_prefix=self.get_dataset_basename(),
                    )

                if not os.path.isabs(file_path):
                    file_path = os.path.join(self.path, file_path)
                scheme = url.scheme()

                if scheme == "fabio":
                    if data_path is not None:
                        raise ValueError("fabio does not handle data_path")
                    else:
                        edf_writer = fabio.edfimage.EdfImage(
                            data=frame,
                        )
                        edf_writer.write(file_path)
                elif scheme in ("hdf5", "silx"):
                    with HDF5File(file_path, mode="a") as h5s:
                        if not cleaned_hdf5_parent_grp:
                            cleaned_hdf5_parent_grp = True
                            if path_to_clean in h5s:
                                del h5s[path_to_clean]
                    with HDF5File(file_path, mode="a") as h5s:
                        h5s[data_path] = frame
                        h5s[data_path].attrs["interpretation"] = "image"
                else:
                    raise ValueError(
                        f"scheme {scheme} is not handled. Should be fabio, silx of hdf5"
                    )

    def _load_frame_dict(self, inputs_urls, return_as_url=False) -> dict:
        """
        :note: note on pattern:
            * handled patterns are:
                * file_path pattern:
                    * {index}: only handled for edf files
                    * {index_zfill4}: only handled for edf files
                    * Only one usage of index and index_zfill4 can be done. Having several {index} or one {index} and one {index_zfill4} will fail
                * data_path pattern:
                    * {entry}
                    * {index}: works only if set at the end of the path (as dataset name)
                    * {index_zfill4}: works only if set at the end of the path (as dataset name)
        :return: dict with frame index in the acquisition sequence as key. Value is the frame as a numpy array if return_as_url is False else this is a DataUrl to the frame
        :rtype: dict
        """
        from tomoscan.esrf.scan.utils import (
            get_files_from_pattern,
        )  # avoid cyclic import

        if self.path is None:
            raise ValueError("No dataset path provided")

        res = {}
        entry = "entry"
        if hasattr(self, "entry"):
            entry = self.entry

        for url in inputs_urls:
            data_path = url.data_path()
            if data_path is not None:
                data_path = data_path.format(
                    entry=entry, index_zfill4="{index_zfill4}", index="{index}"
                )
                # we don't want to handle index_zfill4 and index at this level
            file_pattern = url.file_path()
            if file_pattern is not None:
                file_pattern = file_pattern.format(
                    entry,
                    entry,
                    index_zfill4="{index_zfill4}",
                    index="{index}",
                    scan_prefix=self.get_dataset_basename(),
                )
                # we don't want to handle index_zfill4 and index at this level
            scheme = url.scheme()

            frames_path_and_index = []
            # list of tuples (frame_file, frame_index). frame_index can be None if not found
            patterns = ("index_zfill4", "index")
            contains_patterns = False
            for pattern in patterns:
                if pattern in file_pattern:
                    contains_patterns = True
                    files_from_pattern = get_files_from_pattern(
                        file_pattern=file_pattern,
                        pattern=pattern,
                        research_dir=self.path,
                    )
                    for frame_index, frame_file in files_from_pattern.items():
                        frames_path_and_index.append(
                            (os.path.join(self.path, frame_file), frame_index)
                        )
            if not contains_patterns:
                frames_path_and_index.append(
                    (os.path.join(self.path, file_pattern), None)
                )
            for (frame_file_path, frame_index) in frames_path_and_index:
                if scheme == "fabio":
                    if not os.path.exists(frame_file_path):
                        continue
                    try:
                        handler = fabio.open(frame_file_path)
                        with fabio.open(frame_file_path) as handler:
                            if handler.nframes > 1:
                                _logger.warning(
                                    f"{frame_file_path} is expected to have one frame. Only the first one will be picked"
                                )
                            if frame_index in res:
                                _logger.error(
                                    f"two frames found with the same index {frame_index}: {frame_file_path} and {res[frame_index]}"
                                )
                            if return_as_url:
                                res[frame_index] = DataUrl(
                                    file_path=frame_file_path, scheme="fabio"
                                )
                            else:
                                res[frame_index] = handler.data
                    except OSError as e:
                        _logger.error(e)
                elif scheme in ("hdf5", "silx"):
                    index_zfill4_pattern = False
                    if data_path.endswith("{index_zfill4}"):
                        index_zfill4_pattern = True
                        data_path = data_path[: -len("{index_zfill4}")]
                    if data_path.endswith("{index}"):
                        data_path = data_path[: -len("{index}")]
                    if data_path.endswith("/"):
                        data_path = data_path[:-1]

                    if not os.path.exists(frame_file_path):
                        continue
                    with HDF5File(frame_file_path, mode="r") as h5s:
                        dataset_or_group = h5s[data_path]
                        if isinstance(dataset_or_group, h5py.Dataset):
                            idx = None
                            if dataset_or_group.name.isnumeric():
                                try:
                                    idx = int(dataset_or_group)
                                except ValueError:
                                    idx = None
                            if return_as_url:
                                res[idx] = DataUrl(
                                    file_path=frame_file_path,
                                    data_path=data_path,
                                    scheme="silx",
                                )
                            else:
                                res[idx] = dataset_or_group[()]
                        else:
                            assert isinstance(
                                dataset_or_group, h5py.Group
                            ), f"expect a group not {type(dataset_or_group)}"
                            # browse childrens
                            for (name, item) in dataset_or_group.items():
                                if isinstance(item, h5py.Dataset):
                                    if name.isnumeric():
                                        if index_zfill4_pattern and not len(name) == 4:
                                            continue
                                        else:
                                            try:
                                                idx = int(name)
                                            except ValueError:
                                                _logger.info(
                                                    f"fail to cast {name} as a integer"
                                                )
                                                continue
                                            if return_as_url:
                                                res[idx] = DataUrl(
                                                    file_path=frame_file_path,
                                                    data_path=data_path + "/" + name,
                                                    scheme="silx",
                                                )
                                            else:
                                                res[idx] = dataset_or_group[name][()]
                else:
                    raise ValueError(
                        f"scheme {scheme} is not handled. Should be fabio, silx of hdf5"
                    )

        return res

    def save_reduced_darks(self, darks: dict, output_urls: tuple) -> dict:
        """
        Dump computed dark (median / mean...) into files
        """
        self._dump_frame_dict(frames=darks, output_urls=output_urls)

    def load_reduced_darks(
        self, inputs_urls: tuple, return_as_url: bool = False
    ) -> dict:
        """
        load computed dark (median / mean...) into files
        """
        return self._load_frame_dict(
            inputs_urls=inputs_urls, return_as_url=return_as_url
        )

    def save_reduced_flats(
        self,
        flats: dict,
        output_urls=(DataUrl(file_path="refHST{index}.edf", scheme="fabio")),
    ):
        """ """
        self._dump_frame_dict(frames=flats, output_urls=output_urls)

    def load_reduced_flats(
        self, inputs_urls: tuple, return_as_url: bool = False
    ) -> dict:
        """
        load computed dark (median / mean...) into files
        """
        return self._load_frame_dict(
            inputs_urls=inputs_urls, return_as_url=return_as_url
        )

    def compute_reduced_flats(
        self, reduced_method="median", overwrite=True, output_dtype=None
    ):
        """
        :param ReduceMethod method: method to compute the flats
        :param bool overwrite: if some flats have already been computed will overwrite them
        """
        if self.FRAME_REDUCER_CLASS is None:
            raise ValueError("no frame reducer class provided")
        frame_reducer = self.FRAME_REDUCER_CLASS(
            scan=self,
            reduced_method=reduced_method,
            target="flats",
            overwrite=overwrite,
            output_dtype=output_dtype,
        )
        return frame_reducer.run()

    def compute_reduced_darks(
        self, reduced_method="mean", overwrite=True, output_dtype=None
    ):
        """
        :param ReduceMethod method: method to compute the flats
        :param bool overwrite: if some darks have already been computed will overwrite them
        """
        if self.FRAME_REDUCER_CLASS is None:
            raise ValueError("no frame reducer class provided")
        frame_reducer = self.FRAME_REDUCER_CLASS(
            scan=self,
            reduced_method=reduced_method,
            target="darks",
            overwrite=overwrite,
            output_dtype=output_dtype,
        )
        return frame_reducer.run()

    @staticmethod
    def get_volume_output_file_name(z=None, suffix=None):
        """if used by tomwer and nabu this should help for tomwer to find out the output files of anbu from a configuration file. Could help to get some normalization there"""
        raise NotImplementedError
