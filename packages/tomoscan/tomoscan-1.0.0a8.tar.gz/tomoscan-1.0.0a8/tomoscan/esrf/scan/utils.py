# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016-2022 European Synchrotron Radiation Facility
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
__date__ = "10/10/2019"


import os
import fabio
from silx.io.url import DataUrl
from silx.utils.deprecation import deprecated
from typing import Union
from typing import Iterable
import numpy
import logging
import sys
from tomoscan.io import HDF5File
import warnings
import contextlib
import fnmatch


_logger = logging.getLogger(__name__)


def get_parameters_frm_par_or_info(file_: str) -> dict:
    """
    Create a dictionary from the file with the information name as keys and
    their values as values

    :param file_: path to the file to parse
    :type file_: str
    :raises: ValueError when fail to parse some line.
    """
    assert os.path.exists(file_) and os.path.isfile(file_)
    ddict = {}
    f = open(file_, "r")
    lines = f.readlines()
    for line in lines:
        if "=" not in line:
            continue
        line_ = line.replace(" ", "")
        line_ = line_.rstrip("\n")
        # remove on the line comments
        if "#" in line_:
            line_ = line_.split("#")[0]
        if line_ == "":
            continue
        try:
            key, value = line_.split("=")
        except ValueError:
            raise ValueError('fail to extract information from "%s"' % line_)
        else:
            # try to cast the value on int, else float else don't
            try:
                value = int(value)
            except Exception:
                try:
                    value = float(value)
                except Exception:
                    pass
            ddict[key.lower()] = value
    return ddict


def extract_urls_from_edf(
    file_: str, start_index: Union[None, int], n_frames: Union[int, None] = None
) -> dict:
    """
    return one DataUrl for each frame contain in the file_

    :param file_: path to the file to parse
    :type file_: str
    :param n_frames: Number of frames in each edf file (inferred if not told)
    :type n_frames: Union[int, None]
    :param start_index:
    :type start_index: Union[None,start_index]
    """
    res = {}
    index = 0 if start_index is None else start_index
    if n_frames is None:
        with fabio.open(file_) as fabio_file:
            n_frames = fabio_file.nframes
    for i_frame in range(n_frames):
        res[index] = DataUrl(
            scheme="fabio",
            file_path=file_,
            data_slice=[
                i_frame,
            ],
        )
        index += 1
    return res


def get_compacted_dataslices(
    urls: dict,
    max_grp_size=None,
    return_merged_indices=False,
    return_url_set=False,
    subsampling=1,
):
    """
    Regroup urls to get the data more efficiently.
    Build a structure mapping files indices to information on
    how to load the data: `{indices_set: data_location}`
    where `data_location` contains contiguous indices.

    :param dict urls: Dictionary where the key is an integer and the value is
                      a silx `DataUrl`.
    :param max_grp_size: maximum size of url grps
    :type max_grp_size: None or int
    :param bool return_merged_indices: if True return the last merged indices.
                                       Deprecated
    :param bool return_url_set: return a set with url containing `urls` slices
                                and data path

    :return: Dictionary where the key is a list of indices, and the value is
             the corresponding `silx.io.url.DataUrl` with merged data_slice
    :rtype: dict
    """

    def _convert_to_slice(idx):
        if numpy.isscalar(idx):
            return slice(idx, idx + 1)
        # otherwise, assume already slice object
        return idx

    def is_contiguous_slice(slice1, slice2):
        if numpy.isscalar(slice1):
            slice1 = slice(slice1, slice1 + 1)
        if numpy.isscalar(slice2):
            slice2 = slice(slice2, slice2 + 1)
        return slice2.start == slice1.stop

    def merge_slices(slice1, slice2):
        return slice(slice1.start, slice2.stop)

    if return_merged_indices is True:
        warnings.warn(
            "return_merged_indices is deprecated. It will be removed in version 0.8"
        )

    if max_grp_size is None:
        max_grp_size = sys.maxsize

    if subsampling is None:
        subsampling = 1

    sorted_files_indices = sorted(urls.keys())
    idx0 = sorted_files_indices[0]
    first_url = urls[idx0]
    merged_indices = [[idx0]]
    data_location = [
        [
            first_url.file_path(),
            first_url.data_path(),
            _convert_to_slice(first_url.data_slice()),
            first_url.scheme(),
        ]
    ]
    pos = 0
    grp_size = 0
    curr_fp, curr_dp, curr_slice, curr_scheme = data_location[pos]
    for idx in sorted_files_indices[1:]:
        url = urls[idx]
        next_slice = _convert_to_slice(url.data_slice())
        if (
            (grp_size <= max_grp_size)
            and (url.file_path() == curr_fp)
            and (url.data_path() == curr_dp)
            and is_contiguous_slice(curr_slice, next_slice)
            and (url.scheme() == curr_scheme)
        ):
            merged_indices[pos].append(idx)
            merged_slices = merge_slices(curr_slice, next_slice)
            data_location[pos][-2] = merged_slices
            curr_slice = merged_slices
            grp_size += 1
        else:  # "jump"
            pos += 1
            merged_indices.append([idx])
            data_location.append(
                [
                    url.file_path(),
                    url.data_path(),
                    _convert_to_slice(url.data_slice()),
                    url.scheme(),
                ]
            )
            curr_fp, curr_dp, curr_slice, curr_scheme = data_location[pos]
            grp_size = 0

    # Format result
    res = {}
    for ind, dl in zip(merged_indices, data_location):
        res.update(
            dict.fromkeys(
                ind,
                DataUrl(
                    file_path=dl[0], data_path=dl[1], data_slice=dl[2], scheme=dl[3]
                ),
            )
        )

    # Subsample
    if subsampling > 1:
        next_pos = 0
        for idx in sorted_files_indices:
            url = res[idx]
            ds = url.data_slice()
            res[idx] = DataUrl(
                file_path=url.file_path(),
                data_path=url.data_path(),
                data_slice=slice(next_pos + ds.start, ds.stop, subsampling),
            )
            n_imgs = ds.stop - (ds.start + next_pos)
            next_pos = abs(-n_imgs % subsampling)

    if return_url_set:
        url_set = {}
        for _, url in res.items():
            path = url.file_path(), url.data_path(), str(url.data_slice())
            url_set[path] = url

        if return_merged_indices:
            return res, merge_slices, url_set
        else:
            return res, url_set

    if return_merged_indices:
        return res, merged_slices
    else:
        return res


@deprecated(
    replacement="tomoscan.serie.from_sequences_to_series", since_version="0.8.0"
)
def from_sequences_to_grps(scans: Iterable) -> tuple:
    from tomoscan.serie import sequences_to_series_from_sample_name

    return sequences_to_series_from_sample_name(scans)


@deprecated(replacement="tomoscan.serie.check_serie_is_valid", since_version="0.8.0")
def check_grp_is_valid(scans: Iterable):
    from tomoscan.serie import check_serie_is_consistant_frm_sample_name

    return check_serie_is_consistant_frm_sample_name(scans)


@deprecated(replacement="tomoscan.serie.serie_is_complete", since_version="0.8.0")
def grp_is_complete(scans: Iterable) -> bool:
    from tomoscan.serie import serie_is_complete_from_group_size

    return serie_is_complete_from_group_size(scans)


def dataset_has_broken_vds(url: DataUrl):
    """
    check that the provided url is not a VDS with broken links.
    """
    if not isinstance(url, DataUrl):
        raise TypeError(f"{url} is expected to be an instance of {DataUrl}")
    with HDF5File(url.file_path(), mode="r") as h5f:
        dataset = h5f[url.data_path()]
        if not dataset.is_virtual:
            return False
        else:
            for file_ in get_unique_files_linked(url=url):
                if not os.path.exists(file_):
                    _logger.warning(f"{file_} does not exists")
                    return True
    return False


def get_datasets_linked_to_vds(url: DataUrl):
    """
    Return set([file-path, data_path]) linked to the provided url
    """
    if not isinstance(url, DataUrl):
        raise TypeError(f"{url} is expected to be an instance of {DataUrl}")
    start_file_path = url.file_path()
    start_dataset_path = url.data_path()
    start_dataset_slice = url.data_slice()
    if isinstance(start_dataset_slice, slice):
        start_dataset_slice = tuple(
            range(
                start_dataset_slice.start,
                start_dataset_slice.stop,
                start_dataset_slice.step or 1,
            )
        )
    virtual_dataset_to_treat = set()
    final_dataset = set()
    already_checked = set()

    # first datasets to be tested
    virtual_dataset_to_treat.add(
        (start_file_path, start_dataset_path, start_dataset_slice),
    )

    while len(virtual_dataset_to_treat) > 0:
        to_treat = list(virtual_dataset_to_treat)
        virtual_dataset_to_treat.clear()

        for (file_path, dataset_path, dataset_slice) in to_treat:
            if (file_path, dataset_path, dataset_slice) in already_checked:
                continue
            if os.path.exists(file_path):
                with HDF5File(file_path, mode="r") as h5f:
                    dataset = h5f[dataset_path]
                    if dataset.is_virtual:
                        for vs_info in dataset.virtual_sources():
                            min_frame_bound = vs_info.vspace.get_select_bounds()[0][0]
                            max_frame_bound = vs_info.vspace.get_select_bounds()[1][0]
                            if isinstance(dataset_slice, int):
                                if (
                                    not min_frame_bound
                                    <= dataset_slice
                                    <= max_frame_bound
                                ):
                                    continue
                            elif isinstance(dataset_slice, tuple):
                                if (
                                    min_frame_bound > dataset_slice[-1]
                                    or max_frame_bound < dataset_slice[0]
                                ):
                                    continue

                            with cwd_context():
                                os.chdir(os.path.dirname(file_path))
                                # Fixme: For now will look at the entire dataset of the n +1 file.
                                # if those can also contains virtual dataset and we want to handle
                                # the case a part of it is broken but not ours this should handle
                                # hyperslab
                                virtual_dataset_to_treat.add(
                                    (
                                        os.path.realpath(vs_info.file_name)
                                        if vs_info.file_name != "."
                                        else os.path.abspath(url.file_path()),
                                        # avoid calling os.path.realpath if the dataset is in the same file. Otherwise mess up with paths
                                        vs_info.dset_name,
                                        None,
                                    )
                                )
                    else:
                        final_dataset.add((file_path, dataset_path, dataset_slice))
            else:
                final_dataset.add((file_path, dataset_path, dataset_slice))
            already_checked.add((file_path, dataset_path, dataset_slice))
    return final_dataset


def get_unique_files_linked(url: DataUrl):
    """
    Return the list of unique files linked to the DataUrl without depth limitation
    """
    unique_files = set()
    datasets_linked = get_datasets_linked_to_vds(url=url)
    [unique_files.add(file_path) for (file_path, _, _) in datasets_linked]
    return unique_files


@contextlib.contextmanager
def cwd_context():
    curdir = os.getcwd()
    try:
        yield
    finally:
        os.chdir(curdir)


def get_files_from_pattern(file_pattern: str, pattern: str, research_dir: str) -> dict:
    """
    return: all files using a {pattern} to store the index. Key is the index and value is the file name
    :rtype: dict
    """
    files_frm_patterm = {}
    if ("{" + pattern + "}") not in file_pattern:
        return files_frm_patterm
    if not isinstance(file_pattern, str):
        raise TypeError(f"file_pattern is expected to be str not {type(file_pattern)}")
    if not isinstance(pattern, str):
        raise TypeError(f"pattern is expected to be str not {type(pattern)}")
    if not isinstance(research_dir, str):
        raise TypeError(
            f"research_dir is expected to be a str not {type(research_dir)}"
        )
    if not os.path.exists(research_dir):
        raise FileNotFoundError(f"{research_dir} does not exists")
    # look for some index_zfill4
    file_path_fn = file_pattern.format(**{pattern: "*"})
    for file in os.listdir(research_dir):
        if fnmatch.fnmatch(file.lower(), file_path_fn.lower()):
            # try to deduce the index from pattern
            idx_start = file_pattern.find("{" + pattern + "}")
            idx_end = len(file_pattern.replace("{" + pattern + "}", "")) - idx_start
            idx_as_str = file[idx_start:-idx_end]
            if idx_as_str != "":  # handle case of an empty string
                try:
                    idx_as_int = int(idx_as_str)
                except ValueError:
                    _logger.warning("Could not determined")
                else:
                    files_frm_patterm[idx_as_int] = file

    return files_frm_patterm


def dump_info_file(
    file_path,
    tomo_n,
    scan_range,
    flat_n,
    flat_on,
    dark_n,
    dim_1,
    dim_2,
    col_beg,
    col_end,
    row_beg,
    row_end,
    pixel_size,
    distance,
    energy,
):
    # write the info file
    with open(file_path, "w") as info_file:
        info_file.write("TOMO_N=    " + str(tomo_n) + "\n")
        info_file.write("ScanRange= " + str(scan_range) + "\n")
        info_file.write("REF_N=     " + str(flat_n) + "\n")
        info_file.write("REF_ON=    " + str(flat_on) + "\n")
        info_file.write("DARK_N=    " + str(dark_n) + "\n")
        info_file.write("Dim_1=     " + str(dim_1) + "\n")
        info_file.write("Dim_2=     " + str(dim_2) + "\n")
        info_file.write("Col_beg=   " + str(col_beg) + "\n")
        info_file.write("Col_end=   " + str(col_end) + "\n")
        info_file.write("Row_beg=   " + str(row_beg) + "\n")
        info_file.write("Row_end=   " + str(row_end) + "\n")
        info_file.write("PixelSize= " + str(pixel_size) + "\n")
        info_file.write("Distance=  " + str(distance) + "\n")
        info_file.write("Energy=    " + str(energy) + "\n")
