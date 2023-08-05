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
"""Module with utils in order to define series of scan (TomoScanBase)"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "10/01/2021"


from typing import Iterable, Optional
from tomoscan.scanbase import TomoScanBase
from tomoscan.tomoobject import TomoObject
from .factory import Factory
from .identifier import BaseIdentifier
import logging

_logger = logging.getLogger(__name__)


class Serie(list):
    """
    A serie can be view as an extented list of :class:`TomoObject`.
    This allow the user to define a relation between scans like:

    .. image:: img/scan_serie_class_diagram.png
    """

    def __init__(
        self, name: Optional[str] = None, iterable=None, use_identifiers=False
    ) -> None:
        self._name = "Unknow" if name is None else name
        self.__use_identifiers = use_identifiers
        if iterable is None:
            iterable = []
        super().__init__()
        for item in iterable:
            self.append(item)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        if not isinstance(name, str):
            raise TypeError("name is expected to be an instance of str")
        else:
            self._name = name

    @property
    def use_identifiers(self):
        return self.__use_identifiers

    def append(self, object: TomoObject):
        if not isinstance(object, TomoObject):
            raise TypeError(
                f"object is expected to be an instance of {TomoObject} not {type(object)}"
            )
        if self.use_identifiers:
            super().append(object.get_identifier().to_str())
        else:
            super().append(object)

    def remove(self, object: TomoObject):
        if not isinstance(object, TomoObject):
            raise TypeError(
                f"object is expected to be an instance of {TomoObject} not {type(object)}"
            )
        if self.use_identifiers:
            super().remove(object.get_identifier().to_str())
        else:
            super().remove(object)

    def to_dict_of_str(self) -> dict:
        """
        call for each scan DatasetIdentifier.to_str() if use dataset identifier.
        Otherwise return a default list with dataset identifiers
        """
        objects = []
        for dataset in self:
            if self.use_identifiers:
                objects.append(dataset)
            else:
                objects.append(dataset.get_identifier().to_str())
        return {
            "objects": objects,
            "name": self.name,
            "use_identifiers": self.use_identifiers,
        }

    @staticmethod
    def from_dict_of_str(
        dict_, factory=Factory, use_identifiers: Optional[bool] = None
    ):
        """
        create a Serie from it definition from a dictionary

        :param dict dict_: dictionary containing the serie to create
        :param factory: factory to use in order to create scans defined from there Identifier (as an instance of DatasetIdentifier or is str representation)
        :type factory: Factory
        :param Optional[bool] use_identifiers: use_identifiers can be overwrite when creating the serie

        :return: created Serie
        :rtype: Serie
        """
        name = dict_["name"]
        objects = dict_["objects"]
        if use_identifiers is None:
            use_identifiers = dict_.get("use_identifiers", False)
        instanciated_scans = []
        for tomo_obj in objects:
            if isinstance(tomo_obj, (str, BaseIdentifier)):
                instanciated_scans.append(
                    factory.create_tomo_object_from_identifier(identifier=tomo_obj)
                )
            else:
                raise TypeError(
                    f"elements of dict_['objects'] are expected to be an instance of TomoObject, DatasetIdentifier or str representing a DatasetIdentifier. Not {type(tomo_obj)}"
                )

        return Serie(
            name=name, use_identifiers=use_identifiers, iterable=instanciated_scans
        )

    def __contains__(self, tomo_obj: BaseIdentifier):
        if self.use_identifiers:
            key = tomo_obj.get_identifier().to_str()
        else:
            key = tomo_obj
        return super().__contains__(key)

    def __eq__(self, other):
        if not isinstance(other, Serie):
            return False
        return self.name == other.name and super().__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)


def sequences_to_series_from_sample_name(scans: Iterable) -> tuple:
    """
    create a serie with the same sample name

    :param Iterable scans:
    :return: tuple of serie if as_tuple_of_list is false else a tuple of list (of TomoScanBase)
    """
    series = {}
    for scan in scans:
        if not isinstance(scan, TomoScanBase):
            raise TypeError("Elements are expected to be instances of TomoScanBase")
        if scan.sample_name is None:
            _logger.warning(f"no scan sample found for {scan}")
        if scan.sample_name not in series:
            series[scan.sample_name] = Serie(use_identifiers=False)
        series[scan.sample_name].append(scan)
    return tuple(series.values())


def check_serie_is_consistant_frm_sample_name(scans: Iterable):
    """
    Insure the provided group of scan is valid. Otherwise raise an error

    :param Iterable scans: group of TomoScanBAse to check
    """
    l_scans = set()
    for scan in scans:
        if not isinstance(scan, TomoScanBase):
            raise TypeError("Elements are expected to be instance of TomoScanBase")
        if scan in l_scans:
            raise ValueError("{} is present at least twice")
        elif len(l_scans) > 0:
            first_scan = next(iter((l_scans)))
            if first_scan.sample_name != scan.sample_name:
                raise ValueError(
                    f"{scan} and {first_scan} are from two different sample: {scan.sample_name} and {first_scan.sample_name}"
                )
        l_scans.add(scan)


def serie_is_complete_from_group_size(scans: Iterable) -> bool:
    """
    Insure the provided group of scan is valid. Otherwise raise an error

    :param Iterable scans: group of TomoScanBAse to check
    :return: True if the group is complete
    :rtype: bool
    """
    if len(scans) == 0:
        return True
    try:
        check_serie_is_consistant_frm_sample_name(scans=scans)
    except Exception as e:
        _logger.error("provided group is invalid. {}".format(e))
        raise e
    else:
        group_size = next(iter(scans)).group_size
        if group_size is None:
            _logger.warning("No information found regarding group size")
            return True
        elif group_size == len(scans):
            return True
        elif group_size < len(scans):
            _logger.warning("more scans found than group_size")
            return True
        else:
            return False
