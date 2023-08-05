# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016 European Synchrotron Radiation Facility
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


__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "09/08/2018"

from .scan.hdf5scan import HDF5TomoScan  # noqa F401
from .scan.hdf5scan import HDF5XRD3DScan  # noqa F401
from .scan.edfscan import EDFTomoScan  # noqa F401

from .volume.hdf5volume import HDF5Volume  # noqa F401
from .volume.edfvolume import EDFVolume  # noqa F401
from .volume.tiffvolume import TIFFVolume  # noqa F401
from .volume.tiffvolume import MultiTIFFVolume  # noqa F401
from .volume.jp2kvolume import JP2KVolume  # noqa F401

from .volume.jp2kvolume import has_glymur  # noqa F401
from .volume.tiffvolume import has_tifffile  # noqa F401

TYPES = ["EDF", "HDF5"]
