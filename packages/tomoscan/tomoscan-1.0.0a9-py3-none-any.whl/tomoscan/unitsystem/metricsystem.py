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
__authors__ = ["P. Paleo", "H. Payno"]
__license__ = "MIT"
__date__ = "09/02/2022"


from silx.utils.deprecation import deprecated_warning
from tomoscan.unitsystem.energysystem import (
    EnergySI,
)  # noqa F401  kept for bacward compatibility
from tomoscan.unitsystem.unit import Unit

# Default units:
#  - lenght: meter (m)
#  - energy: kilo Electronvolt (keV)
_meter = 1.0
_kev = 1.0


class MetricSystem(Unit):
    """Util enum to retrieve metric"""

    METER = _meter
    m = _meter
    CENTIMETER = _meter / 100.0
    MILLIMETER = _meter / 1000.0
    MICROMETER = _meter * 1e-6
    NANOMETER = _meter * 1e-9

    KILOELECTRONVOLT = _kev
    ELECTRONVOLT = _kev * 1e-3
    JOULE = _kev / EnergySI.KILOELECTRONVOLT.value
    KILOJOULE = _kev / EnergySI.KILOELECTRONVOLT.value * 1e3

    @classmethod
    def from_str(cls, value: str):
        assert isinstance(value, str)
        if value.lower() in ("m", "meter"):
            return MetricSystem.METER
        elif value.lower() in ("cm", "centimeter"):
            return MetricSystem.CENTIMETER
        elif value.lower() in ("mm", "millimeter"):
            return MetricSystem.MILLIMETER
        elif value.lower() in ("um", "micrometer", "microns"):
            return MetricSystem.MICROMETER
        elif value.lower() in ("nm", "nanometer"):
            deprecated_warning(
                "Function",
                "MetricSystem.from_str for energies",
                reason="Must be part of EnergySI instead",
                replacement="EnergySI.from_str",
                since_version="0.8.0",
            )
            return MetricSystem.NANOMETER
        elif value.lower() in ("kev", "kiloelectronvolt"):
            deprecated_warning(
                "Function",
                "MetricSystem.from_str for energies",
                reason="Must be part of EnergySI instead",
                replacement="EnergySI.from_str",
                since_version="0.8.0",
            )
            return MetricSystem.KILOELECTRONVOLT
        elif value.lower() in ("ev", "electronvolt"):
            deprecated_warning(
                "Function",
                "MetricSystem.from_str for energies",
                reason="Must be part of EnergySI instead",
                replacement="EnergySI.from_str",
                since_version="0.8.0",
            )
            return MetricSystem.ELECTRONVOLT
        elif value.lower() in ("j", "joule"):
            deprecated_warning(
                "Function",
                "MetricSystem.from_str for energies",
                reason="Must be part of EnergySI instead",
                replacement="EnergySI.from_str",
                since_version="0.8.0",
            )
            return MetricSystem.JOULE
        elif value.lower() in ("kj", "kilojoule"):
            deprecated_warning(
                "Function",
                "MetricSystem.from_str for energies",
                reason="Must be part of EnergySI instead",
                replacement="EnergySI.from_str",
                since_version="0.8.0",
            )
            return MetricSystem.KILOJOULE
        else:
            raise ValueError("Cannot convert: %s" % value)

    def __str__(self):
        if self == MetricSystem.METER:
            return "m"
        elif self == MetricSystem.CENTIMETER:
            return "cm"
        elif self == MetricSystem.MILLIMETER:
            return "mm"
        elif self == MetricSystem.MICROMETER:
            return "um"
        elif self == MetricSystem.NANOMETER:
            return "nm"
        elif self == MetricSystem.KILOELECTRONVOLT:
            deprecated_warning(
                "Function",
                "MetricSystem.__str__ for energies",
                reason="Must be part of EnergySI instead",
                replacement="EnergySI.__str__",
                since_version="0.8.0",
            )
            return "keV"
        elif self == MetricSystem.ELECTRONVOLT:
            deprecated_warning(
                "Function",
                "MetricSystem.__str__ for energies",
                reason="Must be part of EnergySI instead",
                replacement="EnergySI.__str__",
                since_version="0.8.0",
            )
            return "eV"
        elif self == MetricSystem.JOULE:
            deprecated_warning(
                "Function",
                "MetricSystem.__str__ for energies",
                reason="Must be part of EnergySI instead",
                replacement="EnergySI.__str__",
                since_version="0.8.0",
            )
            return "J"
        elif self == MetricSystem.KILOJOULE:
            deprecated_warning(
                "Function",
                "MetricSystem.__str__ for energies",
                reason="Must be part of EnergySI instead",
                replacement="EnergySI.__str__",
                since_version="0.8.0",
            )
            return "kJ"
        else:
            raise ValueError(f"Cannot convert: {self}")


m = MetricSystem.METER
meter = MetricSystem.METER

centimeter = MetricSystem.CENTIMETER
cm = centimeter

millimeter = MetricSystem.MILLIMETER
mm = MetricSystem.MILLIMETER

micrometer = MetricSystem.MICROMETER

nanometer = MetricSystem.NANOMETER
