# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility
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
__authors__ = [
    "H. Payno",
]
__license__ = "MIT"
__date__ = "28/04/2022"


from tomoscan.unitsystem.unit import Unit


class ElectricCurrentSystem(Unit):
    """Unit system for electric potential SI units (volt)"""

    AMPERE = 1.0

    MILLIAMPERE = AMPERE / 1000.0

    KILOAMPERE = AMPERE * 10e3

    @classmethod
    def from_str(cls, value: str):
        assert isinstance(value, str)
        if value.lower() in ("a", "ampere"):
            return ElectricCurrentSystem.AMPERE
        elif value.lower() in ("ma", "milliampere"):
            return ElectricCurrentSystem.MILLIAMPERE
        elif value.lower() in ("ka", "kiloampere"):
            return ElectricCurrentSystem.KILOAMPERE
        else:
            raise ValueError("Cannot convert: %s" % value)

    def __str__(self):
        if self == ElectricCurrentSystem.AMPERE:
            return "A"
        elif self == ElectricCurrentSystem.MILLIAMPERE:
            return "mA"
        elif self == ElectricCurrentSystem.KILOAMPERE:
            return "kA"
        else:
            raise ValueError("Cannot convert: to voltage system")


ampere = ElectricCurrentSystem.AMPERE
