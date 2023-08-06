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


class TimeSystem(Unit):
    """Unit system for time in SI units (seconds)"""

    SECOND = 1.0
    MINUTE = 60.0 * SECOND
    HOUR = 60.0 * MINUTE
    DAY = 24.0 * HOUR
    MILLI_SECOND = SECOND * 1e-3
    MICRO_SECOND = SECOND * 1e-6
    NANO_SECOND = SECOND * 1e-9

    @classmethod
    def from_str(cls, value: str):
        assert isinstance(value, str)
        if value.lower() in ("s", "second"):
            return TimeSystem.SECOND
        elif value.lower() in ("m", "minute"):
            return TimeSystem.MINUTE
        elif value.lower() in ("h", "hour"):
            return TimeSystem.HOUR
        elif value.lower() in (
            "d",
            "day",
        ):
            return TimeSystem.DAY
        elif value.lower() in ("ns", "nanosecond", "nano-second"):
            return TimeSystem.NANO_SECOND
        elif value.lower() in ("microsecond", "micro-second"):
            return TimeSystem.MICRO_SECOND
        elif value.lower() in ("millisecond", "milli-second"):
            return TimeSystem.MILLI_SECOND
        else:
            raise ValueError("Cannot convert: %s" % value)

    def __str__(self):
        if self == TimeSystem.SECOND:
            return "second"
        elif self == TimeSystem.MINUTE:
            return "minute"
        elif self == TimeSystem.HOUR:
            return "hour"
        elif self == TimeSystem.DAY:
            return "day"
        elif self == TimeSystem.MILLI_SECOND:
            return "millisecond"
        elif self == TimeSystem.MICRO_SECOND:
            return "microsecond"
        elif self == TimeSystem.NANO_SECOND:
            return "nanosecond"
        else:
            raise ValueError("Cannot convert: to time system")


second = TimeSystem.SECOND
