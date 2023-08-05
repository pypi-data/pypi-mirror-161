#!/usr/bin/python
# coding: utf-8
#
#    Project: Azimuthal integration
#             https://github.com/pyFAI/pyFAI
#
#    Copyright (C) 2015-2022 European Synchrotron Radiation Facility, Grenoble, France
#
#    Principal author:       Jérôme Kieffer (Jerome.Kieffer@ESRF.eu)
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


__doc__ = """test modules for pyFAI."""
__authors__ = ["Jérôme Kieffer", "Valentin Valls", "Henri Payno"]
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "07/02/2017"

import os
import shutil
from urllib.request import urlopen, ProxyHandler, build_opener
from tomoscan.esrf.mock import MockHDF5
import logging
import tempfile

try:
    from contextlib import AbstractContextManager
except ImportError:
    from tomwer.third_party.contextlib import AbstractContextManager

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class UtilsTest(object):
    """
    Static class providing useful stuff for preparing tests.
    """

    timeout = 100  # timeout in seconds for downloading datasets.tar.bz2

    def __init__(self):
        self.installed = False

    @classmethod
    def dataDownloaded(cls, archive_folder, archive_file):
        return cls.dataIsHere(archive_folder=archive_folder) or cls.dataIsDownloaded(
            archive_file=archive_file
        )

    @classmethod
    def dataIsHere(cls, archive_folder):
        return os.path.isdir(archive_folder)

    @classmethod
    def dataIsDownloaded(cls, archive_file):
        return os.path.isfile(archive_file)

    @classmethod
    def getH5Dataset(cls, folderID):
        path = os.path.abspath(
            os.path.join(cls.getDatasets(name="h5_datasets"), folderID)
        )
        if os.path.exists(path):
            return path
        else:
            raise RuntimeError("Coul'd find folder containing scan %s" % folderID)

    @classmethod
    def getOrangeTestFile(cls, folderID):
        path = os.path.abspath(os.path.join(cls.getOrangeTestFiles(), folderID))
        if os.path.isfile(path):
            return path
        else:
            raise RuntimeError("Coul'd find folder containing scan %s" % folderID)

    @classmethod
    def getOrangeTestFiles(cls):
        return cls.getDatasets(name="orangetestfiles")

    @classmethod
    def getDataset(cls, name):
        return cls.getDatasets(name=name)

    @classmethod
    def getDatasets(cls, name="datasets"):
        """
        Downloads the requested image from Forge.EPN-campus.eu

        @param: name of the image.
        For the RedMine forge, the filename contains a directory name that is removed
        @return: full path of the locally saved file
        """
        archive_file = name + ".tar.bz2"
        archive_folder = "".join((os.path.dirname(__file__), "/" + name + "/"))
        archive_file = os.path.join(archive_folder, archive_file)

        # download if needed
        if not cls.dataDownloaded(
            archive_folder=archive_folder, archive_file=archive_file
        ):
            DownloadDataset(
                dataset=os.path.basename(archive_file),
                output_folder=archive_folder,
                timeout=cls.timeout,
            )

            if not os.path.isfile(archive_file):
                raise RuntimeError(
                    "Could not automatically "
                    f"download test images {archive_file}.\n If you are behind a firewall, "
                    "please set both environment variable http_proxy and https_proxy. "
                    "This even works under windows ! \n "
                    f"Otherwise please try to download the images manually from {url_base} / {archive_file}"
                )

        # decompress if needed
        if os.path.isfile(archive_file):
            logger.info("decompressing %s." % archive_file)
            outdir = "".join((os.path.dirname(__file__)))
            shutil.unpack_archive(archive_file, extract_dir=outdir, format="bztar")
            os.remove(archive_file)
        else:
            logger.info("not trying to decompress it")
        return archive_folder

    @classmethod
    def hasInternalTest(cls, dataset):
        """
        The id of the internal test is to have some large scan accessible
        which are stored locally. This should be used only for unit test that
        can be skipped
        """
        if "TOMWER_ADDITIONAL_TESTS_DIR" not in os.environ:
            return False
        else:
            dir = os.path.join(os.environ["TOMWER_ADDITIONAL_TESTS_DIR"], dataset)
        return os.path.isdir(dir)

    @classmethod
    def getInternalTestDir(cls, dataset):
        if cls.hasInternalTest(dataset) is False:
            return None
        else:
            return os.path.join(os.environ["TOMWER_ADDITIONAL_TESTS_DIR"], dataset)


url_base = "http://www.edna-site.org/pub/tomoscan/"


def DownloadDataset(dataset, output_folder, timeout, unpack=False):
    # create if needed path scan
    url = url_base + dataset

    logger.info("Trying to download scan %s, timeout set to %ss", dataset, timeout)
    dictProxies = {}
    if "http_proxy" in os.environ:
        dictProxies["http"] = os.environ["http_proxy"]
        dictProxies["https"] = os.environ["http_proxy"]
    if "https_proxy" in os.environ:
        dictProxies["https"] = os.environ["https_proxy"]
    if dictProxies:
        proxy_handler = ProxyHandler(dictProxies)
        opener = build_opener(proxy_handler).open
    else:
        opener = urlopen
    logger.info("wget %s" % url)
    data = opener(url, data=None, timeout=timeout).read()
    logger.info("Image %s successfully downloaded." % dataset)

    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)

    try:
        archive_folder = os.path.join(output_folder, os.path.basename(dataset))
        with open(archive_folder, "wb") as outfile:
            outfile.write(data)
    except IOError:
        raise IOError(
            "unable to write downloaded \
                        data to disk at %s"
            % archive_folder
        )

    if unpack is True:
        shutil.unpack_archive(archive_folder, extract_dir=output_folder, format="bztar")
        os.remove(archive_folder)


class _MockContext(AbstractContextManager):
    def __init__(self, output_folder):
        self._output_folder = output_folder
        if self._output_folder is None:
            tempfile.mkdtemp()
            self._output_folder_existed = False
        elif not os.path.exists(self._output_folder):
            os.makedirs(self._output_folder)
            self._output_folder_existed = False
        else:
            self._output_folder_existed = True
        super().__init__()

    def __init_subclass__(cls, **kwargs):
        mock_class = kwargs.get("mock_class", None)
        if mock_class is None:
            raise KeyError("mock_class should be provided to the " "metaclass")
        cls._mock_class = mock_class

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._output_folder_existed:
            shutil.rmtree(self._output_folder)


class HDF5MockContext(_MockContext, mock_class=MockHDF5):
    """
    Util class to provide a context with a new Mock HDF5 file
    """

    def __init__(self, scan_path, n_proj, **kwargs):
        super().__init__(output_folder=os.path.dirname(scan_path))
        self._n_proj = n_proj
        self._mocks_params = kwargs
        self._scan_path = scan_path

    def __enter__(self):
        return MockHDF5(
            scan_path=self._scan_path, n_proj=self._n_proj, **self._mocks_params
        ).scan
