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
"""module for giving information on process progress"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "07/08/2019"


from typing import Optional
from silx.utils.enum import Enum as _Enum
from tomoscan.scanbase import TomoScanBase
from numpy.core.numerictypes import generic as numy_generic
import numpy


class ReduceMethod(_Enum):
    MEAN = "mean"  # compute the mean of dark / flat frames serie
    MEDIAN = "median"  # compute the median of dark / flat frames serie
    FIRST = "first"  # take the first frame of the dark / flat serie
    LAST = "last"  # take the last frame of the dark / flat serie
    NONE = "none"


class REDUCER_TARGET(_Enum):
    DARKS = "darks"
    FLATS = "flats"


class FrameReducerBase:
    def __init__(
        self,
        scan: TomoScanBase,
        reduced_method: ReduceMethod,
        target: REDUCER_TARGET,
        output_dtype: Optional[numpy.dtype] = None,
        overwrite=False,
    ):
        self._reduced_method = ReduceMethod.from_value(reduced_method)
        if not isinstance(scan, TomoScanBase):
            raise TypeError(
                f"{scan} is expected to be an instance of TomoscanBase not {type(scan)}"
            )
        self._scan = scan
        self._reducer_target = REDUCER_TARGET.from_value(target)
        if not isinstance(overwrite, bool):
            raise TypeError(
                f"overwrite is expected to be a boolean not {type(overwrite)}"
            )
        self._overwrite = overwrite
        if output_dtype is not None and not issubclass(output_dtype, numy_generic):
            raise TypeError(
                f"output_dtype is expected to be None or a numpy.dtype, not {type(output_dtype)}"
            )
        self._output_dtype = output_dtype

    @property
    def reduced_method(self) -> ReduceMethod:
        return self._reduced_method

    @property
    def scan(self) -> TomoScanBase:
        return self._scan

    @property
    def reducer_target(self) -> REDUCER_TARGET:
        return self._reducer_target

    @property
    def overwrite(self):
        return self._overwrite

    @property
    def output_dtype(self) -> Optional[numpy.dtype]:
        return self._output_dtype

    def run(self):
        raise NotImplementedError
