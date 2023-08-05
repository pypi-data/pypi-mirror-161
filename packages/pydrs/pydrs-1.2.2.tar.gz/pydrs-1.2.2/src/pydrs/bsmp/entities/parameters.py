# import typing
import typing as _typing

from siriuspy.bsmp import BSMPType as _BSMPType
from siriuspy.bsmp import Entity as _Entity
from siriuspy.bsmp import Types as _Types
from siriuspy.pwrsupply.bsmp.constants import ConstPSBSMP as _c


class Parameter:
    def __init__(
        self,
        var_type: _BSMPType,
        unit: str,
        init: bool,
        Op: bool,
        count: int,
    ):
        self.var_type: _BSMPType = var_type
        self.unit: str = unit
        self.init: bool = init
        self.Op: bool = Op
        self.count: int = count


class Parameters(_Entity):
    """Power supply parameters."""

    _parameters: _typing.Dict[int, Parameter] = {
        # ----- class PS -----
        _c.P_PS_NAME: Parameter(
            count=64,
            var_type=_Types.T_FLOAT,
            unit="",
            init=False,
            Op=True,
        ),
        _c.P_PS_MODEL: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        _c.P_PS_NR_PSMODELS: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        # ----- class Communication -----
        _c.P_COMM_CMD_INTERFACE: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="",
            init=False,
            Op=True,
        ),
        4: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="bps",
            init=True,
            Op=False,
        ),
        5: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="",
            init=False,
            Op=True,
        ),
        6: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        7: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        8: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        9: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        10: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="%",
            init=True,
            Op=False,
        ),
        # ----- class Control -----
        11: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="Hz",
            init=True,
            Op=False,
        ),
        12: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="Hz",
            init=True,
            Op=False,
        ),
        13: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        14: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="A/V",
            init=False,
            Op=True,
        ),
        15: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="A/V",
            init=False,
            Op=True,
        ),
        16: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="%",
            init=False,
            Op=True,
        ),
        17: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="%",
            init=False,
            Op=True,
        ),
        # ----- class PWM -----
        18: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="Hz",
            init=True,
            Op=False,
        ),
        19: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="ns",
            init=True,
            Op=False,
        ),
        20: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="pu",
            init=False,
            Op=True,
        ),
        21: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="pu",
            init=False,
            Op=True,
        ),
        22: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="pu",
            init=False,
            Op=True,
        ),
        23: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="pu",
            init=False,
            Op=True,
        ),
        24: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="pu",
            init=False,
            Op=True,
        ),
        # ----- class HRADC -----
        25: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        26: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="MHz",
            init=True,
            Op=False,
        ),
        27: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="Hz",
            init=True,
            Op=False,
        ),
        28: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        29: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        30: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        31: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        32: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        # ----- class SigGen -----
        33: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        34: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        35: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="Hz",
            init=False,
            Op=True,
        ),
        36: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="A/V/%",
            init=False,
            Op=True,
        ),
        37: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="A/V/%",
            init=False,
            Op=True,
        ),
        38: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        # ----- class WfmRef -----
        39: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        40: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
        41: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="Hz",
            init=True,
            Op=False,
        ),
        42: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="A/V/%",
            init=False,
            Op=True,
        ),
        43: Parameter(
            count=4,
            var_type=_Types.T_FLOAT,
            unit="A/V/%",
            init=False,
            Op=True,
        ),
        # ----- class Analog Variables -----
        44: Parameter(
            count=64,
            var_type=_Types.T_FLOAT,
            unit="",
            init=False,
            Op=True,
        ),
        45: Parameter(
            count=64,
            var_type=_Types.T_FLOAT,
            unit="",
            init=False,
            Op=True,
        ),
        # ----- class Debounding manager -----
        46: Parameter(
            count=32,
            var_type=_Types.T_FLOAT,
            unit="us",
            init=True,
            Op=False,
        ),
        47: Parameter(
            count=32,
            var_type=_Types.T_FLOAT,
            unit="us",
            init=True,
            Op=False,
        ),
        48: Parameter(
            count=32,
            var_type=_Types.T_FLOAT,
            unit="us",
            init=True,
            Op=False,
        ),
        49: Parameter(
            count=32,
            var_type=_Types.T_FLOAT,
            unit="us",
            init=True,
            Op=False,
        ),
        # ---- Scope -----
        50: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="Hz",
            init=True,
            Op=False,
        ),
        51: Parameter(
            count=1,
            var_type=_Types.T_FLOAT,
            unit="",
            init=True,
            Op=False,
        ),
    }

    def value_to_load(self, eid: int, value):
        """."""
        _parameter = Parameters._parameters[eid]
        size = _parameter.count
        var_types = [_parameter.var_type] * size
        if eid == 0:
            # power supply name
            value = [float(ord(c)) for c in value]
        load = self._conv_value_to_load(var_types, size, value)
        return load

    def load_to_value(self, eid: int, load):
        """."""
        _parameter = Parameters._parameters[eid]
        size = _parameter.count
        var_types = [_parameter.var_type] * size
        value = self._conv_load_to_value(var_types, load)
        if eid == 0:
            # power supply name
            value = [chr(int(v)) for v in value]
        return value

    @property
    def eids(self):
        """Return entities identifications."""
        return tuple(Parameters._parameters.keys())

    def __getitem__(self, key):
        """."""
        return Parameters._parameters[key]
