import typing

"""BSMP PS."""


def create_value_error(parameter: str, input: typing.Any):
    raise ValueError(f"Invalid value for parameter '{parameter}', received '{input}'")


class BasePSAckError(Exception):
    """Exception raised when the ack response is not the expected"""

    def __init__(self, message, *args: object) -> None:
        super().__init__(*args)


class FunctionExecutionPSAckError(BasePSAckError):
    """."""


class InvalidCommandPSAckError(BasePSAckError):
    """."""


class DSPBusyPSAckError(BasePSAckError):
    """."""


class DSPTimeoutPSAckError(BasePSAckError):
    """."""


class ResourceBusyPSAckError(BasePSAckError):
    """."""


class UDCLockedPSAckError(BasePSAckError):
    """."""


class PSInterlockPSAckError(BasePSAckError):
    """."""
