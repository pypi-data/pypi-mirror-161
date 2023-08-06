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
"""Module containing proxy objects"""

__authors__ = ["V. Valls"]
__license__ = "MIT"
__date__ = "02/10/2017"


import functools
from contextlib import contextmanager, ExitStack
import threading


def _docstring(dest, origin):
    """Implementation of docstring decorator.

    It patches dest.__doc__.
    """
    if not isinstance(dest, type) and isinstance(origin, type):
        # func is not a class, but origin is, get the method with the same name
        try:
            origin = getattr(origin, dest.__name__)
        except AttributeError:
            raise ValueError("origin class has no %s method" % dest.__name__)

    dest.__doc__ = origin.__doc__
    return dest


def docstring(origin):
    """Decorator to initialize the docstring from another source.

    This is useful to duplicate a docstring for inheritance and composition.

    If origin is a method or a function, it copies its docstring.
    If origin is a class, the docstring is copied from the method
    of that class which has the same name as the method/function
    being decorated.

    :param origin:
        The method, function or class from which to get the docstring
    :raises ValueError:
        If the origin class has not method n case the
    """
    return functools.partial(_docstring, origin=origin)


class SharedLockPool:
    """
    Allows to acquire locks identified by name (hashable type) recursively.
    """

    def __init__(self):
        self.__locks = {}
        self.__locks_mutex = threading.Semaphore(value=1)

    def __len__(self):
        return len(self.__locks)

    @property
    def names(self):
        return list(self.__locks.keys())

    @contextmanager
    def _modify_locks(self):
        self.__locks_mutex.acquire()
        try:
            yield self.__locks
        finally:
            self.__locks_mutex.release()

    @contextmanager
    def acquire(self, name):
        with self._modify_locks() as locks:
            lock = locks.get(name, None)
            if lock is None:
                locks[name] = lock = threading.RLock()
        lock.acquire()
        try:
            yield
        finally:
            lock.release()
            with self._modify_locks() as locks:
                if name in locks:
                    locks.pop(name)

    @contextmanager
    def acquire_context_creation(self, name, contextmngr, *args, **kwargs):
        """
        Acquire lock only during context creation.

        This can be used for example to protect the opening of a file
        but not hold the lock while the file is open.
        """
        with ExitStack() as stack:
            with self.acquire(name):
                ret = stack.enter_context(contextmngr(*args, **kwargs))
            yield ret


class _BoundingBox:
    def __init__(self, v1, v2):
        self._min = min(v1, v2)
        self._max = max(v1, v2)

    @property
    def min(self) -> float:
        return self._min

    @property
    def max(self) -> float:
        return self._max

    def __str__(self):
        return f"({self.min}, {self.max})"

    def __eq__(self, other):
        if not isinstance(other, _BoundingBox):
            return False
        else:
            return self.min == other.min and self.max == other.max

    def get_overlap(self, other_bb):
        raise NotImplementedError("Base class")


class BoundingBox1D(_BoundingBox):
    def get_overlap(self, other_bb):
        if not isinstance(other_bb, BoundingBox1D):
            raise TypeError(f"Can't compare a {BoundingBox1D} with {type(other_bb)}")
        if (
            (self.max >= other_bb.min and self.min <= other_bb.max)
            or (other_bb.max >= self.min and other_bb.min <= self.max)
            or (other_bb.min <= self.min and other_bb.max >= self.max)
        ):
            return BoundingBox1D(
                max(self.min, other_bb.min), min(self.max, other_bb.max)
            )
        else:
            return None

    def __eq__(self, other):
        if isinstance(other, (tuple, list)):
            return len(other) == 2 and self.min == other[0] and self.max == other[1]
        else:
            return super().__eq__(other)
