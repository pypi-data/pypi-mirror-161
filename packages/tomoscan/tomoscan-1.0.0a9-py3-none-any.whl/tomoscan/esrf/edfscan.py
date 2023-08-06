from silx.utils.deprecation import deprecated_warning

deprecated_warning(
    "Module",
    name="tomoscan.esrf.edfscan",
    reason="Have been moved",
    replacement="tomoscan.esrf.scan.edfscan",
    only_once=True,
)

from .scan.edfscan import *  # noqa F401
