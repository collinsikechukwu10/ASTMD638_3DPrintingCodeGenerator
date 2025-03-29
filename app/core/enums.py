from enum import StrEnum, IntEnum

from app.core.exceptions import ConfigTypeNotFoundError


class PrinterType(StrEnum):
    REPRAP = "REPRAP"
    ULTIMAKER = "ULTIMAKER"


class MicrostructureType(IntEnum):
    SHIFTED = 0
    STRAIGHT = 1


class ConfigType(StrEnum):
    NUMERIC = "number"
    BOOLEAN = "boolean"
    CATEGORICAL = "categorical"

    @staticmethod
    def get_config_type(value):
        try:
            return ConfigType(value)
        except ValueError as e:
            raise ConfigTypeNotFoundError(e)
