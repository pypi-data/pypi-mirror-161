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
"""module to mock volume"""


from typing import Sized, Union
import numpy
from silx.utils.enum import Enum as _Enum
from silx.image.phantomgenerator import PhantomGenerator


class Scene(_Enum):
    SHEPP_LOGAN = "Shepp-Logan"


def create_volume(
    frame_dims: Union[int, tuple], z_size: int, scene: Scene = Scene.SHEPP_LOGAN
) -> numpy.ndarray:
    """
    create a numpy array of the requested schene for a total of frames_dimes*z_size elements

    :param tuple frame_dims: 2d tuple of frame dimensions
    :param int z_size: number of elements on the volume on z axis
    :param Scene scene: scene to compose
    """
    scene = Scene.from_value(scene)
    if not isinstance(z_size, int):
        raise TypeError(
            f"z_size is expected to be an instance of int not {type(z_size)}"
        )
    if scene is Scene.SHEPP_LOGAN:
        if isinstance(frame_dims, Sized):
            if not len(frame_dims) == 2:
                raise ValueError(
                    f"frame_dims is expected to be an integer or a list of two integers. Not {frame_dims}"
                )
            if frame_dims[0] != frame_dims[1]:
                raise ValueError(
                    f"{scene} only handle square frame. Frame width and height should be the same"
                )
            else:
                dim = frame_dims[0]
        elif isinstance(frame_dims, int):
            dim = frame_dims
        else:
            raise TypeError(
                f"frame_dims is expected to be a list of two integers or an integer. Not {frame_dims}"
            )
        return numpy.asarray(
            [PhantomGenerator.get2DPhantomSheppLogan(dim) * 10000.0] * z_size
        )
    else:
        raise NotImplementedError
