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
__date__ = "04/01/2022"


from silx.io.url import DataUrl
from tomoscan.framereducerbase import (
    REDUCER_TARGET,
    FrameReducerBase,
    ReduceMethod,
)
from tomoscan.esrf.scan.utils import get_compacted_dataslices
from silx.io.utils import get_data
import numpy
import logging

_logger = logging.getLogger(__name__)


class HDF5FrameReducer(FrameReducerBase):
    """Frame reducer dedicated to HDF5"""

    def get_series(self, scan, target: REDUCER_TARGET) -> list:
        """return a list of dictionary. Dictionaries keys are indexes in the acquisition.
        Values are url

        :param HDF5TomoScan scan: scan containing frames to reduce
        :param REDUCER_TARGET target: dark of flat to be reduced
        """
        target = REDUCER_TARGET.from_value(target)
        if target is REDUCER_TARGET.DARKS:
            raw_what = scan.darks
        elif target is REDUCER_TARGET.FLATS:
            raw_what = scan.flats
        else:
            raise ValueError(f"{target} is not handled")
        if len(raw_what) == 0:
            return []
        else:
            series = []
            indexes = sorted(raw_what.keys())
            # a serie is defined by contiguous indexes
            current_serie = {indexes[0]: raw_what[indexes[0]]}
            current_index = indexes[0]
            for index in indexes[1:]:
                if index == current_index + 1:
                    current_index = index
                else:
                    series.append(current_serie)
                    current_serie = {}
                    current_index = index
                current_serie[index] = raw_what[index]
            if len(current_serie) > 0:
                series.append(current_serie)
            return series

    def load_data_serie(self, urls) -> dict:
        """load all urls. Trying to reduce load time by calling get_compacted_dataslices"""
        # handle cases where we only have to load one frame for methods is FIRST or LAST
        if self.reduced_method is ReduceMethod.FIRST and len(urls) > 0:
            urls_keys = sorted(urls.keys())
            urls = {
                urls_keys[0]: urls[urls_keys[0]],
            }
        if self.reduced_method is ReduceMethod.LAST and len(urls) > 0:
            urls_keys = sorted(urls.keys())
            urls = {
                urls_keys[-1]: urls[urls_keys[-1]],
            }

        # active loading
        cpt_slices = get_compacted_dataslices(urls)
        url_set = {}
        for url in cpt_slices.values():
            path = url.file_path(), url.data_path(), str(url.data_slice())
            url_set[path] = url

        n_elmts = 0
        for url in url_set.values():
            my_slice = url.data_slice()
            n_elmts += my_slice.stop - my_slice.start

        data = None
        start_z = 0
        for url in url_set.values():
            my_slice = url.data_slice()
            my_slice = slice(my_slice.start, my_slice.stop, 1)
            new_url = DataUrl(
                file_path=url.file_path(),
                data_path=url.data_path(),
                data_slice=my_slice,
                scheme="silx",
            )
            loaded_data = get_data(new_url)

            # init data if dim is not know
            if data is None:
                data = numpy.empty(
                    shape=(
                        n_elmts,
                        self.scan.dim_2 or loaded_data.shape[-2],
                        self.scan.dim_1 or loaded_data.shape[-1],
                    )
                )
            if loaded_data.ndim == 2:
                data[start_z, :, :] = loaded_data
                start_z += 1
            elif loaded_data.ndim == 3:
                delta_z = my_slice.stop - my_slice.start
                data[start_z:delta_z, :, :] = loaded_data
                start_z += delta_z
            else:
                raise ValueError("Dark and ref raw data should be 2D or 3D")

        return data

    def run(self) -> dict:
        if self.reduced_method is ReduceMethod.MEDIAN:
            method_ = numpy.median
        elif self.reduced_method is ReduceMethod.MEAN:
            method_ = numpy.mean
        elif self.reduced_method is ReduceMethod.NONE:
            return {}
        elif self.reduced_method in (ReduceMethod.FIRST, ReduceMethod.LAST):
            method_ = "raw"
        else:
            raise ValueError(
                f"Mode {self.reduced_method} for {self.reducer_target} is not managed"
            )
        raw_series = self.get_series(self.scan, self.reducer_target)
        if len(raw_series) == 0:
            _logger.warning(
                f"No raw data found for {self.scan} in order to reduce {self.reducer_target}"
            )
            return {}

        res = {}
        # res: key is serie index (first serie frame index), value is the numpy.array of the reduced frame

        for serie_ in raw_series:
            serie_index = min(serie_)
            if self.reducer_target is REDUCER_TARGET.DARKS and len(res) > 0:
                continue

            serie_data = self.load_data_serie(serie_)
            if method_ == "raw":
                # i method is raw then only the targetted frame (first or last) will be loaded
                data = res[serie_index] = serie_data.reshape(-1, serie_data.shape[-1])
            else:
                data = method_(serie_data, axis=0)
            if self.output_dtype is not None:
                data = data.astype(self.output_dtype)
            res[serie_index] = data

        return res
