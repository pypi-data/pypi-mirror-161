from siriuspy.bsmp.serial import IOInterface as _IOInterface
from siriuspy.pwrsupply.bsmp.commands import PSBSMP as _PSBSMP

from .entities import EntitiesPS as _EntitiesPS


class CommonPSBSMP(_PSBSMP):
    """Essa classe espera receber como parâmetro um objeto do tipo siriuspy.bsmp.Entities,
    que possui a relação entre endereço e tipo de entidade bsmp que o dispositivo
    que desejamos controlar possui.
    Caso esse objeto seja nulo, diversas funções deverão ser implementadas novamente.
    ver from siriuspy.pwrsupply.bsmp.entities import EntitiesPS"""

    _timeout_read_variable: float = 100  # [ms]
    _timeout_execute_function: float = 100  # [ms]
    _timeout_remove_vars_groups: float = 100  # [ms]
    _timeout_create_vars_groups: float = 100  # [ms]
    _timeout_read_group_of_variables: float = 100  # [ms]
    _timeout_request_curve_block: float = 100  # [ms]
    _timeout_curve_block: float = 100  # [ms]
    _timeout_query_list_of_group_of_variables: float = 100  # [ms]
    _timeout_query_group_of_variables: float = 100  # [ms]

    _sleep_turn_onoff = 0.050  # [s]
    _sleep_reset_udc = 1.000  # [s]
    _sleep_disable_scope = 0.5  # [s]
    _sleep_select_op_mode = 0.030  # [s]

    def __init__(
        self, iointerface: _IOInterface, slave_address: int, entities: _EntitiesPS
    ):
        super().__init__(iointerface, slave_address, entities)
        self._entities: _EntitiesPS

    @property
    def entities(self) -> _EntitiesPS:
        """Return BSMP entities."""
        return self._entities
