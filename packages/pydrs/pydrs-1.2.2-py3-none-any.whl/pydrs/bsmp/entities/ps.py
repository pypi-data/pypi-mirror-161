import typing as _typing

from siriuspy.bsmp import Curve as _C
from siriuspy.bsmp import Entities as _E
from siriuspy.bsmp import Function as _F
from siriuspy.bsmp import Types as _Types
from siriuspy.bsmp import Variable as _V
from siriuspy.pwrsupply.bsmp.constants import ConstPSBSMP as _c

from .parameters import Parameters as _Parameters


class EntitiesPS(_E):
    """PS Entities."""

    _ps_variables: _typing.Tuple = (
        # --- common variables
        # fmt: off
        _V(eid=_c.V_PS_STATUS, waccess=False, count=1, var_type=_Types.T_UINT16),
        _V(eid=_c.V_PS_SETPOINT, waccess=False, count=1, var_type=_Types.T_FLOAT),
        _V(eid=_c.V_PS_REFERENCE, waccess=False, count=1, var_type=_Types.T_FLOAT),
        _V(eid=_c.V_COUNTER_SET_SLOWREF, waccess=False, count=128, var_type=_Types.T_CHAR),
        _V(eid=4, waccess=False, count=1, var_type=_Types.T_UINT32),
        _V(eid=5, waccess=False, count=1, var_type=_Types.T_UINT32),
        _V(eid=6, waccess=False, count=1, var_type=_Types.T_UINT16),
        _V(eid=7, waccess=False, count=1, var_type=_Types.T_UINT16),
        _V(eid=8, waccess=False, count=1, var_type=_Types.T_UINT16),
        _V(eid=9, waccess=False, count=1, var_type=_Types.T_FLOAT),
        _V(eid=10, waccess=False, count=1, var_type=_Types.T_FLOAT),
        _V(eid=11, waccess=False, count=1, var_type=_Types.T_FLOAT),
        _V(eid=12, waccess=False, count=1, var_type=_Types.T_FLOAT),
        _V(eid=13, waccess=False, count=4, var_type=_Types.T_FLOAT),
        _V(eid=14, waccess=False, count=1, var_type=_Types.T_UINT16),
        _V(eid=15, waccess=False, count=1, var_type=_Types.T_UINT16),
        _V(eid=16, waccess=False, count=1, var_type=_Types.T_FLOAT),
        _V(eid=17, waccess=False, count=1, var_type=_Types.T_FLOAT),
        _V(eid=18, waccess=False, count=1, var_type=_Types.T_FLOAT),
        _V(eid=19, waccess=False, count=1, var_type=_Types.T_UINT32),
        _V(eid=20, waccess=False, count=1, var_type=_Types.T_UINT32),
        _V(eid=21, waccess=False, count=1, var_type=_Types.T_UINT32),
        _V(eid=22, waccess=False, count=1, var_type=_Types.T_UINT32),
        _V(eid=23, waccess=False, count=1, var_type=_Types.T_UINT32),
        _V(eid=24, waccess=False, count=1, var_type=_Types.T_UINT32),
        _V(eid=25, waccess=False, count=1, var_type=_Types.T_FLOAT),
        _V(eid=26, waccess=False, count=1, var_type=_Types.T_FLOAT),
        _V(eid=27, waccess=False, count=1, var_type=_Types.T_UINT32),
        # --- undefined variables
        _V(eid=28, waccess=False, count=1, var_type=_Types.T_UINT8),
        _V(eid=29, waccess=False, count=1, var_type=_Types.T_UINT8),
        _V(eid=30, waccess=False, count=1, var_type=_Types.T_UINT8),
    )
    # fmt: on

    _ps_functions: _typing.Tuple = (
        _F(eid=_c.F_TURN_ON, i_type=(), o_type=(_Types.T_UINT8,)),
        _F(eid=_c.F_TURN_OFF, i_type=(), o_type=(_Types.T_UINT8,)),
        _F(eid=_c.F_OPEN_LOOP, i_type=(), o_type=(_Types.T_UINT8,)),
        _F(eid=_c.F_CLOSE_LOOP, i_type=(), o_type=(_Types.T_UINT8,)),
        _F(
            eid=_c.F_SELECT_OP_MODE,
            i_type=(_Types.T_ENUM,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_RESET_INTERLOCKS,
            i_type=(),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_SET_COMMAND_INTERFACE,
            i_type=(_Types.T_ENUM,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_SET_SERIAL_TERMINATION,
            i_type=(_Types.T_UINT16,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_UNLOCK_UDC,
            i_type=(_Types.T_UINT16,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_LOCK_UDC,
            i_type=(_Types.T_UINT16,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_CFG_SOURCE_SCOPE,
            i_type=(_Types.T_UINT32,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_CFG_FREQ_SCOPE,
            i_type=(_Types.T_FLOAT,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_CFG_DURATION_SCOPE,
            i_type=(_Types.T_FLOAT,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(eid=_c.F_ENABLE_SCOPE, i_type=(), o_type=(_Types.T_UINT8,)),
        _F(
            eid=_c.F_DISABLE_SCOPE,
            i_type=(),
            o_type=(_Types.T_UINT8,),
        ),
        _F(eid=_c.F_SYNC_PULSE, i_type=(), o_type=()),
        _F(
            eid=_c.F_SET_SLOWREF,
            i_type=(_Types.T_FLOAT,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_SET_SLOWREF_FBP,
            i_type=(_Types.T_FLOAT, _Types.T_FLOAT, _Types.T_FLOAT, _Types.T_FLOAT),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_SET_SLOWREF_READBACK_MON,
            i_type=(_Types.T_FLOAT,),
            o_type=(
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
            ),
        ),
        _F(
            eid=_c.F_SET_SLOWREF_FBP_READBACK_MON,
            i_type=(
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
            ),
            o_type=(
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
            ),
        ),
        _F(
            eid=_c.F_SET_SLOWREF_READBACK_REF,
            i_type=(_Types.T_FLOAT,),
            o_type=(
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
            ),
        ),
        _F(
            eid=_c.F_SET_SLOWREF_FBP_READBACK_REF,
            i_type=(
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
            ),
            o_type=(
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
            ),
        ),
        _F(
            eid=_c.F_RESET_COUNTERS,
            i_type=(),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_CFG_WFMREF,
            i_type=(
                _Types.T_UINT16,
                _Types.T_UINT16,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
            ),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_SELECT_WFMREF,
            i_type=(_Types.T_UINT16,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_GET_WFMREF_SIZE,
            i_type=(_Types.T_UINT16,),
            o_type=(_Types.T_UINT16,),
        ),
        _F(eid=_c.F_RESET_WFMREF, i_type=(), o_type=(_Types.T_UINT8,)),
        _F(
            eid=_c.F_CFG_SIGGEN,
            i_type=(
                _Types.T_ENUM,
                _Types.T_UINT16,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
            ),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_SET_SIGGEN,
            i_type=(_Types.T_FLOAT, _Types.T_FLOAT, _Types.T_FLOAT),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_ENABLE_SIGGEN,
            i_type=(),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_DISABLE_SIGGEN,
            i_type=(),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_SET_PARAM,
            i_type=(
                _Types.T_PARAM,
                _Types.T_UINT16,
                _Types.T_FLOAT,
            ),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_GET_PARAM,
            i_type=(
                _Types.T_PARAM,
                _Types.T_UINT16,
            ),
            o_type=(_Types.T_FLOAT,),
        ),
        _F(
            eid=_c.F_SAVE_PARAM_EEPROM,
            i_type=(
                _Types.T_PARAM,
                _Types.T_UINT16,
                _Types.T_UINT16,
            ),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_LOAD_PARAM_EEPROM,
            i_type=(
                _Types.T_PARAM,
                _Types.T_UINT16,
                _Types.T_UINT16,
            ),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_SAVE_PARAM_BANK,
            i_type=(_Types.T_UINT16,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_LOAD_PARAM_BANK,
            i_type=(_Types.T_UINT16,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_SET_DSP_COEFFS,
            i_type=(
                _Types.T_DSP_CLASS,
                _Types.T_UINT16,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
                _Types.T_FLOAT,
            ),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_GET_DSP_COEFF,
            i_type=(
                _Types.T_DSP_CLASS,
                _Types.T_UINT16,
                _Types.T_UINT16,
            ),
            o_type=(_Types.T_FLOAT,),
        ),
        _F(
            eid=_c.F_SAVE_DSP_COEFFS_EEPROM,
            i_type=(
                _Types.T_DSP_CLASS,
                _Types.T_UINT16,
                _Types.T_UINT16,
            ),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_LOAD_DSP_COEFFS_EEPROM,
            i_type=(
                _Types.T_DSP_CLASS,
                _Types.T_UINT16,
                _Types.T_UINT16,
            ),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_SAVE_DSP_MODULES_EEPROM,
            i_type=(_Types.T_UINT16,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(
            eid=_c.F_LOAD_DSP_MODULES_EEPROM,
            i_type=(_Types.T_UINT16,),
            o_type=(_Types.T_UINT8,),
        ),
        _F(eid=_c.F_RESET_UDC, i_type=(), o_type=()),
    )

    _ps_curves: _typing.Tuple = (
        _C(
            eid=0,
            waccess=True,
            count=256,
            nblocks=16,
            var_type=_Types.T_FLOAT,
        ),
        _C(
            eid=1,
            waccess=True,
            count=256,
            nblocks=16,
            var_type=_Types.T_FLOAT,
        ),
        _C(
            eid=2,
            waccess=False,
            count=256,
            nblocks=16,
            var_type=_Types.T_FLOAT,
        ),
    )

    _ps_parameters = _Parameters()

    def __init__(self):
        """Call super."""
        super().__init__(self._ps_variables, self._ps_curves, self._ps_functions)

    @property
    def parameters(self):
        """Return pwrsupply parameters."""
        return EntitiesPS._ps_parameters
