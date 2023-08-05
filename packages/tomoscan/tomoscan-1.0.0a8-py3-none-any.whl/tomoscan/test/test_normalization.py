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
__date__ = "31/08/2021"


from tomoscan.test.utils import HDF5MockContext
from tomoscan.nexus.paths.nxtomo import nx_tomo_path_latest
import tomoscan.esrf.hdf5scan
import tomoscan.normalization
import os
import tempfile
import numpy
import pytest

try:
    import scipy.interpolate  # noqa F401
except ImportError:
    has_scipy = False
else:
    has_scipy = True


@pytest.mark.parametrize("method", ["subtraction", "division"])
def test_normalization_scalar_normalization(method):
    """test scalar normalization"""
    with HDF5MockContext(
        scan_path=os.path.join(tempfile.mkdtemp(), "scan_test"),
        n_proj=10,
        n_ini_proj=10,
    ) as scan:
        with pytest.raises(KeyError):
            scan.get_sinogram(line=2, norm_method=method)

        scan.get_sinogram(line=2, norm_method=method, value=12.2)


def test_normalize_chebyshev_2D():
    """Test checbychev 2D normalization"""
    with HDF5MockContext(
        scan_path=os.path.join(tempfile.mkdtemp(), "scan_test"),
        n_proj=10,
        n_ini_proj=10,
    ) as scan:
        sinogram = scan.get_sinogram(line=2)
        tomoscan.normalization.normalize_chebyshev_2D(sinogram)
        sinogram_2 = scan.get_sinogram(line=2, norm_method="chebyshev")
        assert numpy.array_equal(sinogram, sinogram_2)


@pytest.mark.skipif(condition=not has_scipy, reason="scipy missing")
def test_normalize_lsqr_spline_2D():
    """test lsqr_spline_2D normalization"""
    with HDF5MockContext(
        scan_path=os.path.join(tempfile.mkdtemp(), "scan_test"),
        n_proj=10,
        n_ini_proj=10,
    ) as scan:
        sinogram = scan.get_sinogram(line=2)
        tomoscan.normalization.normalize_lsqr_spline_2D(sinogram)
        sinogram_2 = scan.get_sinogram(line=2, norm_method="lsqr spline")
        assert numpy.array_equal(sinogram, sinogram_2)


def test_normalize_dataset():
    """Test extra information that can be provided relative to a dataset"""
    with HDF5MockContext(
        scan_path=os.path.join(tempfile.mkdtemp(), "scan_test"),
        n_proj=10,
        n_ini_proj=10,
        dim=100,
        intensity_monitor=True,
    ) as scan:
        datasetinfo = tomoscan.normalization._DatasetInfos()
        datasetinfo.file_path = scan.master_file
        datasetinfo.data_path = "/".join(
            [scan.entry, nx_tomo_path_latest.INTENSITY_MONITOR_PATH]
        )
        assert isinstance(datasetinfo.data_path, str)
        assert isinstance(datasetinfo.file_path, str)
        datasetinfo.scope = tomoscan.normalization._DatasetScope.GLOBAL
        assert isinstance(datasetinfo.scope, tomoscan.normalization._DatasetScope)
        scan.intensity_normalization.set_extra_infos(datasetinfo)


def test_normalize_roi():
    """Test extra information that can be provided relative to a roi"""
    with HDF5MockContext(
        scan_path=os.path.join(tempfile.mkdtemp(), "scan_test"),
        n_proj=10,
        n_ini_proj=10,
        dim=100,
        intensity_monitor=True,
    ) as scan:
        roi_info = tomoscan.normalization._ROIInfo()
        scan.intensity_normalization.set_extra_infos(roi_info)
        scan.intensity_normalization.method = None
        scan.intensity_normalization.method = "lsqr spline"
        assert isinstance(
            scan.intensity_normalization.method, tomoscan.normalization.Method
        )
        str(scan.intensity_normalization)
