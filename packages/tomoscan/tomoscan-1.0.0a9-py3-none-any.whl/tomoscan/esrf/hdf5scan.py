from silx.utils.deprecation import deprecated_warning

deprecated_warning(
    "Module",
    name="tomoscan.esrf.hdf5scan",
    reason="Have been moved",
    replacement="tomoscan.esrf.scan.hdf5scan",
    only_once=True,
)

from .scan.hdf5scan import *  # noqa F401
