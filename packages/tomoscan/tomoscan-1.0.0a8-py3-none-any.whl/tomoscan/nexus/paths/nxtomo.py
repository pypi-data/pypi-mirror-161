from typing import Optional
from . import nxdetector
from . import nxinstrument
from . import nxsample
from . import nxsource
from . import nxmonitor
from silx.utils.deprecation import deprecated
import logging
import tomoscan

_logger = logging.getLogger(__name__)


LATEST_VERSION = 1.2


class NXtomo_PATH:
    # list all path that can be used by an nxtomo entry and read by tomoscan.
    # this is also used by nxtomomill to know were to save data

    _NX_DETECTOR_PATHS = None
    _NX_INSTRUMENT_PATHS = None
    _NX_SAMPLE_PATHS = None
    _NX_SOURCE_PATHS = None
    _NX_CONTROL_PATHS = None

    VERSION = None

    @property
    def nx_detector_paths(self):
        return self._NX_DETECTOR_PATHS

    @property
    def nx_instrument_paths(self):
        return self._NX_INSTRUMENT_PATHS

    @property
    def nx_sample_paths(self):
        return self._NX_SAMPLE_PATHS

    @property
    def nx_source_paths(self):
        return self._NX_SOURCE_PATHS

    @property
    def nx_monitor_paths(self):
        return self._NX_CONTROL_PATHS

    @property
    def PROJ_PATH(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.DETECTOR_PATH,
                self.nx_detector_paths.DATA,
            ]
        )

    @property
    def SCAN_META_PATH(self) -> str:
        # for now scan_meta and technique are not link to any nxtomo...
        return "scan_meta/technique/scan"

    @property
    def INSTRUMENT_PATH(self) -> str:
        return "instrument"

    @property
    def CONTROL_PATH(self) -> str:
        return "control"

    @property
    def DET_META_PATH(self) -> str:
        return "scan_meta/technique/detector"

    @property
    def ROTATION_ANGLE_PATH(self):
        return "/".join(["sample", self.nx_sample_paths.ROTATION_ANGLE])

    @property
    def SAMPLE_PATH(self) -> str:
        return "sample"

    @property
    def NAME_PATH(self) -> str:
        return "sample/name"

    @property
    def GRP_SIZE_ATTR(self) -> str:
        return "group_size"

    @property
    def SAMPLE_NAME_PATH(self) -> str:
        return "/".join([self.SAMPLE_PATH, self.nx_sample_paths.NAME])

    @property
    def X_TRANS_PATH(self) -> str:
        return "/".join([self.SAMPLE_PATH, self.nx_sample_paths.X_TRANSLATION])

    @property
    def Y_TRANS_PATH(self) -> str:
        return "/".join([self.SAMPLE_PATH, self.nx_sample_paths.Y_TRANSLATION])

    @property
    def Z_TRANS_PATH(self) -> str:
        return "/".join([self.SAMPLE_PATH, self.nx_sample_paths.Z_TRANSLATION])

    @property
    def IMG_KEY_PATH(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.DETECTOR_PATH,
                self.nx_detector_paths.IMAGE_KEY,
            ]
        )

    @property
    def IMG_KEY_CONTROL_PATH(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.DETECTOR_PATH,
                self.nx_detector_paths.IMAGE_KEY_CONTROL,
            ]
        )

    @property
    def X_PIXEL_SIZE_PATH(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.DETECTOR_PATH,
                self.nx_detector_paths.X_PIXEL_SIZE,
            ]
        )

    @property
    def Y_PIXEL_SIZE_PATH(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.DETECTOR_PATH,
                self.nx_detector_paths.Y_PIXEL_SIZE,
            ]
        )

    @property
    def X_PIXEL_MAG_SIZE_PATH(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.DETECTOR_PATH,
                self.nx_detector_paths.X_PIXEL_SIZE_MAGNIFIED,
            ]
        )

    @property
    def Y_PIXEL_MAG_SIZE_PATH(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.DETECTOR_PATH,
                self.nx_detector_paths.Y_PIXEL_SIZE_MAGNIFIED,
            ]
        )

    @property
    def DISTANCE_PATH(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.DETECTOR_PATH,
                self.nx_detector_paths.DISTANCE,
            ]
        )

    @property
    def FOV_PATH(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.DETECTOR_PATH,
                self.nx_detector_paths.FOV,
            ]
        )

    @property
    def EXPOSURE_TIME_PATH(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.DETECTOR_PATH,
                self.nx_detector_paths.EXPOSURE_TIME,
            ]
        )

    @property
    def ELECTRIC_CURRENT_PATH(self) -> str:
        return "/".join(
            [
                self.CONTROL_PATH,
                self.nx_monitor_paths.DATA_PATH,
            ]
        )

    @property
    def ESTIMATED_COR_FRM_MOTOR_PATH(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.DETECTOR_PATH,
                self.nx_detector_paths.ESTIMATED_COR_FRM_MOTOR,
            ]
        )

    @property
    def TOMO_N_SCAN(self) -> str:
        return "/".join(
            [self.INSTRUMENT_PATH, self.nx_instrument_paths.DETECTOR_PATH, "tomo_n"]
        )

    @property
    def BEAM_PATH(self) -> str:
        return "beam"

    @property
    def ENERGY_PATH(self) -> str:
        return f"{self.BEAM_PATH}/incident_energy"

    @property
    def START_TIME_PATH(self) -> str:
        return "start_time"

    @property
    def END_TIME_PATH(self) -> str:
        return "end_time"

    @property
    @deprecated(replacement="END_TIME_PATH", reason="typo", since_version="0.8.0")
    def END_TIME_START(self) -> str:
        return self.END_TIME_PATH

    @property
    def INTENSITY_MONITOR_PATH(self) -> str:
        return "diode/data"

    @property
    @deprecated(
        replacement="", reason="will be removed. Not used", since_version="0.8.0"
    )
    def EPSILON_ROT_ANGLE(self) -> float:
        return 0.02

    @property
    def SOURCE_NAME(self) -> Optional[str]:
        return None

    @property
    def SOURCE_TYPE(self) -> Optional[str]:
        return None

    @property
    def SOURCE_PROBE(self) -> Optional[str]:
        return None

    @property
    def INSTRUMENT_NAME(self) -> Optional[str]:
        return None

    @property
    def ROCKING_PATH(self) -> str:
        return "/".join([self.SAMPLE_PATH, self.nx_sample_paths.ROCKING])

    @property
    def BASE_TILT_PATH(self) -> str:
        return "/".join([self.SAMPLE_PATH, self.nx_sample_paths.BASE_TILT])


class NXtomo_PATH_v_1_0(NXtomo_PATH):

    VERSION = 1.0

    _NX_DETECTOR_PATHS = nxdetector.NEXUS_DETECTOR_PATH_V_1_0
    _NX_INSTRUMENT_PATHS = nxinstrument.NEXUS_INSTRUMENT_PATH_V_1_0
    _NX_SAMPLE_PATHS = nxsample.NEXUS_SAMPLE_PATH_V_1_0
    _NX_SOURCE_PATHS = nxsource.NEXUS_SOURCE_PATH_V_1_0
    _NX_CONTROL_PATHS = nxmonitor.NEXUS_MONITOR_PATH_V_1_1


nx_tomo_path_v_1_0 = NXtomo_PATH_v_1_0()


class NXtomo_PATH_v_1_1(NXtomo_PATH_v_1_0):

    VERSION = 1.1

    _NX_DETECTOR_PATHS = nxdetector.NEXUS_DETECTOR_PATH_V_1_1
    _NX_INSTRUMENT_PATHS = nxinstrument.NEXUS_INSTRUMENT_PATH_V_1_1
    _NX_SAMPLE_PATHS = nxsample.NEXUS_SAMPLE_PATH_V_1_1
    _NX_SOURCE_PATHS = nxsource.NEXUS_SOURCE_PATH_V_1_1

    @property
    def NAME_PATH(self) -> str:
        return "title"

    @property
    def BEAM_PATH(self) -> str:
        return "/".join([self.INSTRUMENT_PATH, self.nx_instrument_paths.BEAM])

    @property
    def SOURCE_NAME(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.SOURCE,
                self.nx_source_paths.NAME,
            ]
        )

    @property
    def SOURCE_TYPE(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.SOURCE,
                self.nx_source_paths.TYPE,
            ]
        )

    @property
    def SOURCE_PROBE(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.SOURCE,
                self.nx_source_paths.PROBE,
            ]
        )

    @property
    def INSTRUMENT_NAME(self) -> str:
        return "/".join([self.INSTRUMENT_PATH, self.nx_instrument_paths.NAME])


nx_tomo_path_v_1_1 = NXtomo_PATH_v_1_1()


class NXtomo_PATH_v_1_2(NXtomo_PATH_v_1_1):

    VERSION = 1.2

    _NX_DETECTOR_PATHS = nxdetector.NEXUS_DETECTOR_PATH_V_1_2
    _NX_INSTRUMENT_PATHS = nxinstrument.NEXUS_INSTRUMENT_PATH_V_1_2
    _NX_SAMPLE_PATHS = nxsample.NEXUS_SAMPLE_PATH_V_1_2
    _NX_SOURCE_PATHS = nxsource.NEXUS_SOURCE_PATH_V_1_2

    @property
    def INTENSITY_MONITOR_PATH(self) -> str:
        return "/".join(
            [
                self.INSTRUMENT_PATH,
                self.nx_instrument_paths.DIODE,
                self.nx_detector_paths.DATA,
            ]
        )


nx_tomo_path_v_1_2 = NXtomo_PATH_v_1_2()

nx_tomo_path_latest = nx_tomo_path_v_1_2


def get_paths(version: Optional[float]) -> NXtomo_PATH:
    if version is None:
        version = LATEST_VERSION
        _logger.warning(
            f"version of the NXtomo not found. Will take the latest one ({LATEST_VERSION})"
        )
    versions_dict = {
        1.0: nx_tomo_path_v_1_0,
        1.1: nx_tomo_path_v_1_1,
        1.2: nx_tomo_path_v_1_2,
    }
    if version not in versions_dict:
        if int(version) == 1:
            _logger.warning(
                f"nexus path {version} requested but unknow from this version of tomoscan {tomoscan.__version__}. Pick latest one of this major version. You might miss some information"
            )
            version = LATEST_VERSION
        else:
            raise ValueError(f"Unknow major version of the nexus path ({version})")
    return versions_dict[version]
