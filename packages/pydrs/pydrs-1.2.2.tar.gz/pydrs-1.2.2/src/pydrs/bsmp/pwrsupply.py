from siriuspy.bsmp import IOInterface as _IOInterface
from siriuspy.pwrsupply.bsmp.constants import ConstPSBSMP as _ConstPSBSMP

from .command import CommonPSBSMP as _CommonPSBSMP
from .entities import EntitiesPS as _EntitiesPS


class GenericPowerPS:
    def __init__(self, iointerf: _IOInterface, address: int) -> None:
        self._bsmp: _CommonPSBSMP = _CommonPSBSMP(
            iointerface=iointerf, entities=_EntitiesPS(), slave_address=address
        )

    def turn_on(self):
        ack, data = self._bsmp.execute_function(
            func_id=_ConstPSBSMP.F_TURN_ON,
            input_val=(),
        )
        return ack, data
