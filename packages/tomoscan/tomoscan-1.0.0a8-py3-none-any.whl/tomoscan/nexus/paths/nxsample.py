class NEXUS_SAMPLE_PATH:
    NAME = "sample_name"

    ROTATION_ANGLE = "rotation_angle"

    X_TRANSLATION = "x_translation"

    Y_TRANSLATION = "y_translation"

    Z_TRANSLATION = "z_translation"

    ROCKING = "rocking"

    BASE_TILT = "base_tilt"

    N_STEPS_ROCKING = "n_step_rocking"

    N_STEPS_ROTATION = "n_step_rotation"


class NEXUS_SAMPLE_PATH_V_1_0(NEXUS_SAMPLE_PATH):
    pass


class NEXUS_SAMPLE_PATH_V_1_1(NEXUS_SAMPLE_PATH_V_1_0):
    NAME = "name"


class NEXUS_SAMPLE_PATH_V_1_2(NEXUS_SAMPLE_PATH_V_1_1):
    pass
