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
"""Module containing validators"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "07/07/2022"


from tomoscan.volumebase import VolumeBase
import pytest


def test_volume_base():
    """Test VolumeBase file"""

    class UnplemetnedVolumeBase(VolumeBase):
        def deduce_data_and_metadata_urls(self, url):
            return None, None

    volume_base = UnplemetnedVolumeBase()

    with pytest.raises(NotImplementedError):
        volume_base.example_defined_from_str_identifier()

    with pytest.raises(NotImplementedError):
        volume_base.get_identifier()

    with pytest.raises(NotImplementedError):
        VolumeBase.from_identifier("")

    with pytest.raises(NotImplementedError):
        volume_base.save_data()

    with pytest.raises(NotImplementedError):
        volume_base.save_metadata()

    with pytest.raises(NotImplementedError):
        volume_base.save()

    with pytest.raises(NotImplementedError):
        volume_base.load_data()

    with pytest.raises(NotImplementedError):
        volume_base.load_metadata()

    with pytest.raises(NotImplementedError):
        volume_base.load()

    with pytest.raises(NotImplementedError):
        volume_base.browse_data_files()

    with pytest.raises(NotImplementedError):
        volume_base.browse_metadata_files()

    with pytest.raises(NotImplementedError):
        volume_base.browse_data_urls()
