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

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "10/01/2022"


class BaseIdentifier:

    TOMO_TYPE = None

    def __init__(self, object):
        self._dataset_builder = object.from_identifier

    @property
    def tomo_type(self):
        return self.TOMO_TYPE

    def recreate_object(self):
        """Recreate the dataset from the identifier"""
        return self._dataset_builder(self)

    def short_description(self) -> str:
        """short description of the identifier"""
        return ""

    @property
    def scheme(self) -> str:
        raise NotImplementedError("Base class")

    def to_str(self):
        return str(self)

    @staticmethod
    def from_str(identifier):
        raise NotImplementedError("base class")

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, BaseIdentifier):
            return __o.to_str() == self.to_str()
        elif isinstance(__o, str):
            return __o == self.to_str()
        else:
            return False


class ScanIdentifier(BaseIdentifier):
    TOMO_TYPE = "scan"


class VolumeIdentifier(BaseIdentifier):
    TOMO_TYPE = "volume"
