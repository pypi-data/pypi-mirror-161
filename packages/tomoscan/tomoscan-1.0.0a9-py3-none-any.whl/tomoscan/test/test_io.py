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
__date__ = "18/09/2020"


import os
import h5py
import numpy
import shutil
import unittest
import tempfile
from tomoscan.io import check_virtual_sources_exist


class TestCheckVirtualSourcesExists(unittest.TestCase):
    """insure the check_virtual_sources_exist function exists"""

    def setUp(self) -> None:
        self.folder = tempfile.mkdtemp()
        self.h5_file = os.path.join(self.folder, "myfile.hdf5")

    def tearDown(self) -> None:
        shutil.rmtree(self.folder)

    def test_check_virtual_sources_exist_vds(self):
        with h5py.File(self.h5_file, mode="w") as h5f:
            h5f["data"] = numpy.random.random((120, 120))
        self.assertTrue(check_virtual_sources_exist(self.h5_file, "data"))

    def test_check_virtual_sources_exist_no_vds(self):
        # create some dataset
        for i in range(4):
            filename = os.path.join(self.folder, f"{i}.h5")
            with h5py.File(filename, mode="w") as h5f:
                h5f.create_dataset("data", (100,), "i4", numpy.arange(100))

        layout = h5py.VirtualLayout(shape=(4, 100), dtype="i4")
        for i in range(4):
            filename = os.path.join(self.folder, f"{i}.h5")
            layout[i] = h5py.VirtualSource(filename, "data", shape=(100,))

        with h5py.File(self.h5_file, mode="w") as h5f:
            # create the virtual dataset
            h5f.create_virtual_dataset("data", layout, fillvalue=-5)
        self.assertTrue(check_virtual_sources_exist(self.h5_file, "data"))
