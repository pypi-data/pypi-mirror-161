"""Provides exceptions related to 'var_value' Utility"""


class InvalidLocaleException(Exception):
    """Raied by 'var_value' Utility if 'locale' is not defined in runtime config"""

    def __init__(self, *, locale):
        super().__init__(f"Invalid locale '{locale}'")


class InvalidVarException(Exception):
    """Raied by 'var_value' Utility if failed to extract value of 'var'"""

    def __init__(self, *, var):
        super().__init__(f"Invalid var '{var}'")
