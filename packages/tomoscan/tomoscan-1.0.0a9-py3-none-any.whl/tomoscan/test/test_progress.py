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
"""module for giving information on process progress"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "31/08/2021"


import tomoscan.progress


def test_progress():
    """Simple test of the Progress API"""
    progress = tomoscan.progress.Progress("this is progress")
    progress.reset()
    progress.startProcess()
    progress.setMaxAdvancement(80)
    for adv in (10, 20, 50, 70):
        progress.setAdvancement(adv)
    for i in range(10):
        progress.increaseAdvancement(1)


def test_advancement():
    """Simple test of the _Advancement API"""
    for i in range(4):
        tomoscan.progress._Advancement.getNextStep(
            tomoscan.progress._Advancement.getStep(i)
        )
