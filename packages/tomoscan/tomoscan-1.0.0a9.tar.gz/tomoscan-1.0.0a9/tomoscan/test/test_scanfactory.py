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
__date__ = "24/01/2017"


import os
from tomoscan.esrf.edfscan import EDFTomoScan
from tomoscan.esrf.hdf5scan import HDF5TomoScan
from tomoscan.scanbase import TomoScanBase
from tomoscan.factory import Factory
from tomoscan.test.utils import UtilsTest
from tomoscan.esrf.mock import MockEDF
import tempfile
import pytest


def test_scan_edf():
    """can we create a TomoScanBase object from a folder containing a
    valid .edf acquisition"""
    scan_dir = UtilsTest.getDataset("test10")
    scan = Factory.create_scan_object(scan_dir)
    assert isinstance(scan, EDFTomoScan)


def test_one_nx():
    """Can we create a TomoScanBase from a .nx master file containing
    one acquisition"""
    file_name = "frm_edftomomill_oneentry.nx"
    master_file = UtilsTest.getH5Dataset(file_name)
    scan = Factory.create_scan_object(master_file)
    assert isinstance(scan, HDF5TomoScan)
    assert scan.path == os.path.dirname(master_file)
    assert scan.master_file == master_file
    assert scan.entry == "entry"


def test_one_two_nx():
    """Can we create a TomoScanBase from a .nx master file containing
    two acquisitions"""
    master_file = UtilsTest.getH5Dataset("frm_edftomomill_twoentries.nx")
    scan = Factory.create_scan_object(master_file)
    assert isinstance(scan, HDF5TomoScan)
    assert scan.path == os.path.dirname(master_file)
    assert scan.master_file == master_file
    assert scan.entry == "entry0000"


def test_two_nx():
    """Can we create two TomoScanBase from a .nx master file containing
    two acquisitions using the Factory"""
    master_file = UtilsTest.getH5Dataset("frm_edftomomill_twoentries.nx")
    scans = Factory.create_scan_objects(master_file)
    assert len(scans) == 2
    for scan, scan_entry in zip(scans, ("entry0000", "entry0001")):
        assert isinstance(scan, HDF5TomoScan) is True
        assert scan.path == os.path.dirname(master_file)
        assert scan.master_file == master_file
        assert scan.entry == scan_entry


def test_invalid_path():
    """Insure an error is raised if the path as no meaning"""
    with pytest.raises(ValueError):
        Factory.create_scan_object("toto")

    with pytest.raises(ValueError):
        Factory.create_scan_objects("toto")

    with tempfile.TemporaryDirectory() as scan_dir:
        with pytest.raises(ValueError):
            Factory.create_scan_object(scan_dir)


def test_edf_scan_creation():
    with tempfile.TemporaryDirectory() as folder:
        scan_dir = os.path.join(folder, "my_scan")
        MockEDF.mockScan(scanID=scan_dir, nRecons=10)
        scan = Factory.create_scan_object(scan_path=scan_dir)
        assert isinstance(scan, EDFTomoScan)
        scans = Factory.create_scan_objects(scan_path=scan_dir)
        assert len(scans) == 1
        assert isinstance(scans[0], EDFTomoScan)
        dict_ = scan.to_dict()
        Factory.create_scan_object_frm_dict(dict_)
        # test invalid dict
        dict_[TomoScanBase.DICT_TYPE_KEY] = "tata"
        with pytest.raises(ValueError):
            Factory.create_scan_object_frm_dict(dict_)
        del dict_[TomoScanBase.DICT_TYPE_KEY]
        with pytest.raises(ValueError):
            Factory.create_scan_object_frm_dict(dict_)
