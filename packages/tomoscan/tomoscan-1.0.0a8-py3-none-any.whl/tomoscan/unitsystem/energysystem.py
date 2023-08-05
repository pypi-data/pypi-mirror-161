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
__authors__ = ["P. Paleo", "H. Payno"]
__license__ = "MIT"
__date__ = "09/02/2022"


from tomoscan.unitsystem.unit import Unit


# Constants
_elementary_charge_coulomb = 1.602176634e-19


_joule_si = 1.0


class EnergySI(Unit):
    """Util enum for energy in SI units (Joules)"""

    JOULE = _joule_si
    ELEMCHARGE = _elementary_charge_coulomb
    ELECTRONVOLT = _elementary_charge_coulomb

    KILOELECTRONVOLT = _elementary_charge_coulomb * 1e3
    MEGAELECTRONVOLT = _elementary_charge_coulomb * 1e6
    GIGAELECTRONVOLT = _elementary_charge_coulomb * 1e9
    KILOJOULE = 1e3 * _joule_si

    @classmethod
    def from_str(cls, value: str):
        if value.lower() in ("j", "joule"):
            return EnergySI.JOULE
        elif value.lower() in ("kj", "kilojoule"):
            return EnergySI.KILOJOULE
        elif value.lower() in ("ev", "electronvolt"):
            return EnergySI.ELECTRONVOLT
        elif value.lower() in ("kev", "kiloelectronvolt"):
            return EnergySI.KILOELECTRONVOLT
        elif value.lower() in ("mev", "megaelectronvolt"):
            return EnergySI.MEGAELECTRONVOLT
        elif value.lower() in ("gev", "gigaelectronvolt"):
            return EnergySI.GIGAELECTRONVOLT
        elif value.lower() in ("e", "qe"):
            return EnergySI.ELEMCHARGE
        else:
            raise ValueError("Cannot convert: %s" % value)

    def __str__(self):
        if self is EnergySI.JOULE:
            return "J"
        elif self is EnergySI.KILOJOULE:
            return "kJ"
        elif self is EnergySI.ELECTRONVOLT:
            return "eV"
        elif self is EnergySI.KILOELECTRONVOLT:
            return "keV"
        elif self is EnergySI.MEGAELECTRONVOLT:
            return "meV"
        elif self is EnergySI.GIGAELECTRONVOLT:
            return "geV"
        elif self is EnergySI.ELEMCHARGE:
            # in fact will never be called because EnergySI.ELEMCHARGE is EnergySI.ELECTRONVOLT
            return "e"
