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

__authors__ = ["W. DeNolf", "H. Payno"]
__license__ = "MIT"
__date__ = "12/05/2022"


from typing import Iterable, Tuple


class UrlSettings:
    FILE_PATH_KEY = "file_path"
    DATA_PATH_KEY = "data_path"
    FILE_PREFIX = "file_prefix"


def split_query(query: str) -> dict:
    result = dict()
    for s in query.split("&"):
        if not s:
            continue
        name, _, value = s.partition("=")
        prev_value = result.get(name)
        if prev_value:
            value = join_string(prev_value, value, "/")
        result[name] = value
    return result


def join_query(query_items: Iterable[Tuple[str, str]]) -> str:
    return "&".join(f"{k}={v}" for k, v in query_items)


def join_string(a: str, b: str, sep: str):
    aslash = a.endswith(sep)
    bslash = b.startswith(sep)
    if aslash and bslash:
        return a[:-1] + b
    elif aslash or bslash:
        return a + b
    else:
        return a + sep + b


def join_path(path_items: tuple) -> str:
    if not isinstance(path_items, tuple):
        raise TypeError
    return ":".join(path_items)


def split_path(path: str):
    return path.split(":")
