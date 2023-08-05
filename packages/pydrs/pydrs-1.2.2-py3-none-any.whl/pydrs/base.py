#!/usr/bin/env python3
"""The core for pydrs, from which all child classes are based"""
import csv
import math
import os
import struct
import time

from .consts import (
    COM_FUNCTION,
    COM_READ_VAR,
    COM_REQUEST_CURVE,
    COM_SEND_WFM_REF,
    COM_WRITE_VAR,
    DP_MODULE_MAX_COEFF,
    NUM_MAX_COEFFS_DSP,
    UDC_FIRMWARE_VERSION,
    WRITE_DOUBLE_SIZE_PAYLOAD,
    WRITE_FLOAT_SIZE_PAYLOAD,
    dsp_classes_names,
    num_blocks_curves_fax,
    num_blocks_curves_fbp,
    num_coeffs_dsp_modules,
    num_dsp_modules,
    size_curve_block,
    type_format,
    type_size,
)

# common_list
from .consts.common_list import (
    list_common_vars,
    list_curv,
    list_func,
    list_op_mode,
    list_parameters,
    list_ps_models,
    list_sig_gen_types,
)

# fac_const_list
from .consts.fac_const_list import (
    list_fac_2p4s_dcdc_hard_interlocks,
    list_fac_2p4s_dcdc_iib_alarms,
    list_fac_2p4s_dcdc_iib_interlocks,
    list_fac_2p4s_dcdc_soft_interlocks,
    list_fac_2p_acdc_imas_hard_interlocks,
    list_fac_2p_acdc_imas_soft_interlocks,
    list_fac_2p_dcdc_imas_hard_interlocks,
    list_fac_2p_dcdc_imas_soft_interlocks,
    list_fac_2s_acdc_hard_interlocks,
    list_fac_2s_acdc_iib_cmd_alarms,
    list_fac_2s_acdc_iib_cmd_interlocks,
    list_fac_2s_acdc_iib_is_alarms,
    list_fac_2s_acdc_iib_is_interlocks,
    list_fac_2s_acdc_soft_interlocks,
    list_fac_2s_dcdc_hard_interlocks,
    list_fac_2s_dcdc_iib_alarms,
    list_fac_2s_dcdc_iib_interlocks,
    list_fac_2s_dcdc_soft_interlocks,
    list_fac_acdc_hard_interlocks,
    list_fac_acdc_iib_cmd_alarms,
    list_fac_acdc_iib_cmd_interlocks,
    list_fac_acdc_iib_is_alarms,
    list_fac_acdc_iib_is_interlocks,
    list_fac_acdc_soft_interlocks,
    list_fac_dcdc_ema_hard_interlocks,
    list_fac_dcdc_ema_iib_alarms,
    list_fac_dcdc_ema_iib_interlocks,
    list_fac_dcdc_ema_soft_interlocks,
    list_fac_dcdc_hard_interlocks,
    list_fac_dcdc_iib_alarms,
    list_fac_dcdc_iib_interlocks,
    list_fac_dcdc_soft_interlocks,
)

# fap_const_list
from .consts.fap_const_list import (
    list_fap_2p2s_hard_interlocks,
    list_fap_2p2s_soft_interlocks,
    list_fap_4p_hard_interlocks,
    list_fap_4p_iib_alarms,
    list_fap_4p_iib_interlocks,
    list_fap_4p_soft_interlocks,
    list_fap_225A_hard_interlocks,
    list_fap_225A_soft_interlocks,
    list_fap_hard_interlocks,
    list_fap_iib_alarms,
    list_fap_iib_interlocks,
    list_fap_soft_interlocks,
)

# fbp_const_list
from .consts.fbp_const_list import (
    list_fbp_dclink_hard_interlocks,
    list_fbp_hard_interlocks,
    list_fbp_soft_interlocks,
)
from .utils import (
    double_to_hex,
    float_list_to_hex,
    float_to_hex,
    format_list_size,
    get_logger,
    index_to_hex,
    size_to_hex,
    uint32_to_hex,
)
from .validation import SerialErrPckgLen, SerialInvalidCmd

logger = get_logger(name=__file__)


class BaseDRS(object):
    """Base class, originates all communication child classes"""

    def __init__(self):
        self.slave_addr = 1

        print(
            "\n pyDRS - compatible UDC firmware version: " + UDC_FIRMWARE_VERSION + "\n"
        )

    def __exit__(self):
        self.disconnect()

    def connect(self):
        """Creates communication bus object and connects"""
        pass

    def disconnect(self):
        """Disconnects current communication bus"""
        pass

    def is_open(self) -> bool:
        """Returns whether or not the current communication bus is open (or equivalent terminology)"""
        pass

    def _transfer(self, msg: str, size: int) -> bytes:
        """Sends then receives data from target DRS device"""
        pass

    def _transfer_write(self, msg: str):
        """Transfers data to target DRS device"""
        pass

    def _reset_input_buffer(self):
        """Resets input buffer for the given communication protocol"""
        pass

    @property
    def timeout(self) -> float:
        """Communication bus timeout"""
        pass

    @timeout.setter
    def timeout(self, new_timeout: float):
        pass

    @property
    def slave_addr(self) -> int:
        return struct.unpack("B", self._slave_addr.encode())[0]

    @slave_addr.setter
    def slave_addr(self, address: int):
        self._slave_addr = struct.pack("B", address).decode("ISO-8859-1")

    """
    ======================================================================
                    Funções Internas da Classe
    ======================================================================
    """

    def read_var(self, var_id: str, size: int):
        """Reads a variable with a given ID"""
        self._reset_input_buffer()
        return self._transfer(COM_READ_VAR + var_id, size)

    """
    ======================================================================
                Métodos de Chamada de Entidades Funções BSMP
            O retorno do método são os bytes de retorno da mensagem
    ======================================================================
    """

    def turn_on(self):
        """Turns on power supply"""
        payload_size = size_to_hex(1)  # Payload: ID
        send_packet = (
            COM_FUNCTION + payload_size + index_to_hex(list_func.index("turn_on"))
        )
        return self._transfer(send_packet, 6)

    def turn_off(self):
        """Turns off power supply"""
        payload_size = size_to_hex(1)  # Payload: ID
        send_packet = (
            COM_FUNCTION + payload_size + index_to_hex(list_func.index("turn_off"))
        )
        return self._transfer(send_packet, 6)

    def open_loop(self):
        payload_size = size_to_hex(1)  # Payload: ID
        send_packet = (
            COM_FUNCTION + payload_size + index_to_hex(list_func.index("open_loop"))
        )
        return self._transfer(send_packet, 6)

    def closed_loop(self):
        payload_size = size_to_hex(1)  # Payload: ID
        send_packet = (
            COM_FUNCTION + payload_size + index_to_hex(list_func.index("closed_loop"))
        )
        return self._transfer(send_packet, 6)

    def reset_interlocks(self):
        """Resets interlocks on connected DRS device"""
        payload_size = size_to_hex(1)  # Payload: ID
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("reset_interlocks"))
        )
        return self._transfer(send_packet, 6)

    def read_ps_status(self) -> dict:
        """Gets power supply status"""
        reply_msg = self.read_var(index_to_hex(list_common_vars.index("ps_status")), 7)
        val = struct.unpack("BBHHB", reply_msg)
        return {
            "state": list_op_mode[(val[3] & 0b0000000000001111)],
            "open_loop": (val[3] & 0b0000000000010000) >> 4,
            "interface": (val[3] & 0b0000000001100000) >> 5,
            "active": (val[3] & 0b0000000010000000) >> 7,
            "model": list_ps_models[(val[3] & 0b0001111100000000) >> 8],
            "unlocked": (val[3] & 0b0010000000000000) >> 13,
        }

    def set_ps_name(self, ps_name: str):
        # TODO: Turn into property?
        """Sets power supply name"""
        for n in range(len(ps_name)):
            self.set_param("PS_Name", n, float(ord(ps_name[n])))
        for i in range(n + 1, 64):
            self.set_param("PS_Name", i, float(ord(" ")))

    def get_ps_name(self) -> str:
        # TODO: Turn into property?
        """Gets power supply name"""
        ps_name = ""
        for n in range(64):
            ps_name = ps_name + chr(int(self.get_param("PS_Name", n)))
            if ps_name[-3:] == "   ":
                ps_name = ps_name[: n - 2]
                break
        return ps_name

    def set_slowref(self, setpoint: float) -> bytes:
        """Sets new slowref reference value"""
        payload_size = size_to_hex(1 + 4)  # Payload: ID + iSlowRef
        hex_setpoint = float_to_hex(setpoint)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("set_slowref"))
            + hex_setpoint
        )
        return self._transfer(send_packet, 6)

    def set_slowref_fbp(
        self, iRef1: int = 0, iRef2: int = 0, iRef3: int = 0, iRef4: int = 0
    ) -> bytes:
        """Sets slowref reference value for FBP power supplies"""
        # TODO: Take int list instead?
        payload_size = size_to_hex(1 + 4 * 4)  # Payload: ID + 4*iRef
        hex_iRef1 = float_to_hex(iRef1)
        hex_iRef2 = float_to_hex(iRef2)
        hex_iRef3 = float_to_hex(iRef3)
        hex_iRef4 = float_to_hex(iRef4)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("set_slowref_fbp"))
            + hex_iRef1
            + hex_iRef2
            + hex_iRef3
            + hex_iRef4
        )
        return self._transfer(send_packet, 6)

    def set_slowref_readback_mon(self, setpoint: float) -> bytes:
        """Sets slowref reference value and returns current readback"""
        payload_size = size_to_hex(1 + 4)  # Payload: ID + iSlowRef
        hex_setpoint = float_to_hex(setpoint)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("set_slowref_readback_mon"))
            + hex_setpoint
        )
        reply_msg = self._transfer(send_packet, 9)
        val = struct.unpack("BBHfB", reply_msg)
        return val[3]

    def set_slowref_fbp_readback_mon(
        self, iRef1: int = 0, iRef2: int = 0, iRef3: int = 0, iRef4: int = 0
    ):
        """Sets slowref reference value for FBP power supplies and returns current readback"""
        # TODO: Take int list instead?
        payload_size = size_to_hex(1 + 4 * 4)  # Payload: ID + 4*iRef
        hex_iRef1 = float_to_hex(iRef1)
        hex_iRef2 = float_to_hex(iRef2)
        hex_iRef3 = float_to_hex(iRef3)
        hex_iRef4 = float_to_hex(iRef4)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("set_slowref_fbp_readback_mon"))
            + hex_iRef1
            + hex_iRef2
            + hex_iRef3
            + hex_iRef4
        )
        try:
            reply_msg = self._transfer(send_packet, 21)
            val = struct.unpack("BBHffffB", reply_msg)
            return [val[3], val[4], val[5], val[6]]
        except (SerialErrPckgLen, SerialInvalidCmd):
            return reply_msg

    def set_slowref_readback_ref(self, setpoint: float) -> float:
        """Sets slowref reference value and returns reference current"""
        payload_size = size_to_hex(1 + 4)  # Payload: ID + iSlowRef
        hex_setpoint = float_to_hex(setpoint)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("set_slowref_readback_ref"))
            + hex_setpoint
        )
        reply_msg = self._transfer(send_packet, 9)
        val = struct.unpack("BBHfB", reply_msg)
        return val[3]

    def set_slowref_fbp_readback_ref(
        self, iRef1: int = 0, iRef2: int = 0, iRef3: int = 0, iRef4: int = 0
    ):
        """Sets slowref reference value for FBP power supplies and returns reference current"""
        # TODO: Take int list instead?
        payload_size = size_to_hex(1 + 4 * 4)  # Payload: ID + 4*iRef
        hex_iRef1 = float_to_hex(iRef1)
        hex_iRef2 = float_to_hex(iRef2)
        hex_iRef3 = float_to_hex(iRef3)
        hex_iRef4 = float_to_hex(iRef4)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("set_slowref_fbp_readback_ref"))
            + hex_iRef1
            + hex_iRef2
            + hex_iRef3
            + hex_iRef4
        )
        try:
            reply_msg = self._transfer(send_packet, 21)
            val = struct.unpack("BBHffffB", reply_msg)
            return [val[3], val[4], val[5], val[6]]
        except (SerialErrPckgLen, SerialInvalidCmd):
            return reply_msg

    def set_param(self, param_id: int, n: int, value: float) -> bytes:
        """Set parameter"""
        # TODO: Turn into property?
        payload_size = size_to_hex(
            1 + 2 + 2 + 4
        )  # Payload: ID + param id + [n] + value
        if type(param_id) == str:
            hex_id = double_to_hex(list_parameters.index(param_id))
        if type(param_id) == int:
            hex_id = double_to_hex(param_id)
        hex_n = double_to_hex(n)
        hex_value = float_to_hex(value)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("set_param"))
            + hex_id
            + hex_n
            + hex_value
        )

        reply_msg = self._transfer(send_packet, 6)
        return reply_msg

    def get_param(self, param_id, n=0):
        """Get parameter"""
        # Payload: ID + param id + [n]
        payload_size = size_to_hex(1 + 2 + 2)
        if type(param_id) == str:
            hex_id = double_to_hex(list_parameters.index(param_id))
        if type(param_id) == int:
            hex_id = double_to_hex(param_id)
        hex_n = double_to_hex(n)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("get_param"))
            + hex_id
            + hex_n
        )
        self._reset_input_buffer()
        try:
            reply_msg = self._transfer(send_packet, 9)
            val = struct.unpack("BBHfB", reply_msg)
            return val[3]
        except SerialInvalidCmd:
            return float("nan")

    def save_param_eeprom(
        self, param_id: int, n: int = 0, type_memory: int = 2
    ) -> bytes:
        """Save parameter to EEPROM"""
        # TODO: Raise exception instead of printing?
        payload_size = size_to_hex(
            1 + 2 + 2 + 2
        )  # Payload: ID + param id + [n] + memory type
        if type(param_id) == str:
            hex_id = double_to_hex(list_parameters.index(param_id))
        if type(param_id) == int:
            hex_id = double_to_hex(param_id)
        hex_n = double_to_hex(n)
        hex_type = double_to_hex(type_memory)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("save_param_eeprom"))
            + hex_id
            + hex_n
            + hex_type
        )
        return self._transfer(send_packet, 6)

    def load_param_eeprom(
        self, param_id: int, n: int = 0, type_memory: int = 2
    ) -> bytes:
        """Load parameter from EEPROM"""
        payload_size = size_to_hex(
            1 + 2 + 2 + 2
        )  # Payload: ID + param id + [n] + memory type
        if type(param_id) == str:
            hex_id = double_to_hex(list_parameters.index(param_id))
        if type(param_id) == int:
            hex_id = double_to_hex(param_id)
        hex_n = double_to_hex(n)
        hex_type = double_to_hex(type_memory)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("load_param_eeprom"))
            + hex_id
            + hex_n
            + hex_type
        )
        reply_msg = self._transfer(send_packet, 6)
        return reply_msg

    def save_param_bank(self, type_memory: int = 2) -> bytes:
        """Configures all paremeters according to values loaded into param_data"""
        payload_size = size_to_hex(1 + 2)  # Payload: ID + memory type
        hex_type = double_to_hex(type_memory)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("save_param_bank"))
            + hex_type
        )

        # User defined timeout is temporarily changed to a "safe" value to prevent lockups
        old_timeout = self.timeout
        self.timeout = 10
        ret = self._transfer(send_packet, 6)
        self.timeout = old_timeout
        return ret

    def load_param_bank(self, type_memory: int = 2) -> bytes:
        """Loads all parameter values into param_data"""
        payload_size = size_to_hex(1 + 2)  # Payload: ID + memory type
        hex_type = double_to_hex(type_memory)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("load_param_bank"))
            + hex_type
        )
        return self._transfer(send_packet, 6)

    def set_param_bank(self, param_file: str):
        fbp_param_list = []
        with open(param_file, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                fbp_param_list.append(row)

        for param in fbp_param_list:
            if str(param[0]) == "PS_Name":
                print(str(param[0]) + "[0]: " + str(param[1]))
                print(self.set_ps_name(str(param[1])))
            else:
                for n in range(64):
                    try:
                        print(str(param[0]) + "[" + str(n) + "]: " + str(param[n + 1]))
                        print(self.set_param(str(param[0]), n, float(param[n + 1])))
                    except:
                        break
        # self.save_param_bank()

    def get_param_bank(
        self,
        list_param: list = list_parameters,
        timeout: float = 0.5,
        print_modules: bool = True,
    ) -> list:
        timeout_old = self.timeout
        param_bank = []

        for param_name in list_param:

            param_row = [param_name]

            for n in range(64):
                if param_name == "PS_Name":

                    p = self.get_ps_name()
                    param_row.append(p)
                    # if(print_modules):
                    # print('PS_Name: ' + p)
                    self.timeout = timeout
                    break

                else:
                    p = self.get_param(param_name, n)
                    if math.isnan(p):
                        break
                    param_row.append(p)
                    # if(print_modules):
                    # print(param_name + "[" + str(n) + "]: " + str(p))

            if print_modules:
                print(param_row)

            param_bank.append(param_row)

        self.timeout = timeout_old

        return param_bank

    def store_param_bank_csv(self, bank: list):
        """Saves parameter bank to CSV file"""
        filename = input("Digite o nome do arquivo: ")
        with open(filename + ".csv", "w", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            for param_row in bank:
                writer.writerow(param_row)

    def enable_onboard_eeprom(self):
        """Enables onboard EEPROM"""
        self.set_param("Enable_Onboard_EEPROM", 0, 0)
        self.save_param_eeprom("Enable_Onboard_EEPROM", 0, 2)

    def disable_onboard_eeprom(self):
        """Disables onboard EEPROM"""
        self.set_param("Enable_Onboard_EEPROM", 0, 1)
        self.save_param_eeprom("Enable_Onboard_EEPROM", 0, 2)

    def set_dsp_coeffs(
        self,
        dsp_class: int,
        dsp_id: int,
        coeffs_list: list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ) -> bytes:
        coeffs_list_full = format_list_size(coeffs_list, NUM_MAX_COEFFS_DSP)
        payload_size = size_to_hex(1 + 2 + 2 + 4 * NUM_MAX_COEFFS_DSP)
        hex_dsp_class = double_to_hex(dsp_class)
        hex_dsp_id = double_to_hex(dsp_id)
        hex_coeffs = float_list_to_hex(coeffs_list_full)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("set_dsp_coeffs"))
            + hex_dsp_class
            + hex_dsp_id
            + hex_coeffs
        )
        return self._transfer(send_packet, 6)

    def get_dsp_coeff(self, dsp_class: int, dsp_id: int, coeff: int):
        payload_size = size_to_hex(1 + 2 + 2 + 2)
        hex_dsp_class = double_to_hex(dsp_class)
        hex_dsp_id = double_to_hex(dsp_id)
        hex_coeff = double_to_hex(coeff)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("get_dsp_coeff"))
            + hex_dsp_class
            + hex_dsp_id
            + hex_coeff
        )
        self._reset_input_buffer()
        reply_msg = self._transfer(send_packet, 9)
        # print(reply_msg)
        val = struct.unpack("BBHfB", reply_msg)
        return val[3]

    def save_dsp_coeffs_eeprom(
        self, dsp_class: int, dsp_id: int, type_memory: int = 2
    ) -> bytes:
        payload_size = size_to_hex(1 + 2 + 2 + 2)
        hex_dsp_class = double_to_hex(dsp_class)
        hex_dsp_id = double_to_hex(dsp_id)
        hex_type = double_to_hex(type_memory)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("save_dsp_coeffs_eeprom"))
            + hex_dsp_class
            + hex_dsp_id
            + hex_type
        )
        return self._transfer(send_packet, 6)

    def load_dsp_coeffs_eeprom(
        self, dsp_class: int, dsp_id: int, type_memory: int = 2
    ) -> bytes:
        payload_size = size_to_hex(1 + 2 + 2 + 2)
        hex_dsp_class = double_to_hex(dsp_class)
        hex_dsp_id = double_to_hex(dsp_id)
        hex_type = double_to_hex(type_memory)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("load_dsp_coeffs_eeprom"))
            + hex_dsp_class
            + hex_dsp_id
            + hex_type
        )
        return self._transfer(send_packet, 6)

    def save_dsp_modules_eeprom(self, type_memory: int = 2) -> bytes:
        payload_size = size_to_hex(1 + 2)  # Payload: ID + memory type
        hex_type = double_to_hex(type_memory)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("save_dsp_modules_eeprom"))
            + hex_type
        )
        return self._transfer(send_packet, 6)

    def load_dsp_modules_eeprom(self, type_memory: int = 2) -> bytes:
        payload_size = size_to_hex(1 + 2)  # Payload: ID + memory type
        hex_type = double_to_hex(type_memory)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("load_dsp_modules_eeprom"))
            + hex_type
        )
        return self._transfer(send_packet, 6)

    def reset_udc(self):
        """Resets UDC firmware"""
        reply = input(
            "\nEste comando realiza o reset do firmware da placa UDC, e por isso, so e executado caso a fonte esteja desligada. \nCaso deseje apenas resetar interlocks, utilize o comando reset_interlocks(). \n\nTem certeza que deseja prosseguir? [Y/N]: "
        )
        if reply == "Y" or reply == "y":
            payload_size = size_to_hex(1)  # Payload: ID
            send_packet = (
                COM_FUNCTION + payload_size + index_to_hex(list_func.index("reset_udc"))
            )
            self._transfer_write(send_packet)

    def run_bsmp_func(self, id_func: int) -> bytes:
        payload_size = size_to_hex(1)  # Payload: ID
        send_packet = COM_FUNCTION + payload_size + index_to_hex(id_func)
        return self._transfer(send_packet, 6)

    def run_bsmp_func_all_ps(
        self,
        p_func,
        add_list: list,
        arg=None,
        delay: float = 0.5,
        print_reply: bool = True,
    ):
        old_add = self.slave_addr
        for add in add_list:
            self.slave_addr = add
            if arg is None:
                r = p_func()
            else:
                r = p_func(arg)
            if print_reply:
                print("\n Add " + str(add))
                print(r)
            time.sleep(delay)
        self.slave_addr = old_add

    def cfg_source_scope(self, p_source: int) -> bytes:
        payload_size = size_to_hex(1 + 4)  # Payload: ID + p_source
        hex_op_mode = uint32_to_hex(p_source)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("cfg_source_scope"))
            + hex_op_mode
        )
        return self._transfer(send_packet, 6)

    def cfg_freq_scope(self, freq: float) -> bytes:
        payload_size = size_to_hex(1 + 4)  # Payload: ID + freq
        hex_op_mode = float_to_hex(freq)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("cfg_freq_scope"))
            + hex_op_mode
        )
        return self._transfer(send_packet, 6)

    def cfg_duration_scope(self, duration: float) -> bytes:
        payload_size = size_to_hex(1 + 4)  # Payload: ID + duration
        hex_op_mode = float_to_hex(duration)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("cfg_duration_scope"))
            + hex_op_mode
        )
        return self._transfer(send_packet, 6)

    def enable_scope(self) -> bytes:
        """Enables scope"""
        payload_size = size_to_hex(1)  # Payload: ID
        send_packet = (
            COM_FUNCTION + payload_size + index_to_hex(list_func.index("enable_scope"))
        )
        return self._transfer(send_packet, 6)

    def disable_scope(self) -> bytes:
        """Disables scope"""
        payload_size = size_to_hex(1)  # Payload: ID
        send_packet = (
            COM_FUNCTION + payload_size + index_to_hex(list_func.index("disable_scope"))
        )
        return self._transfer(send_packet, 6)

    def get_scope_vars(self) -> dict:
        return {
            "frequency": self.read_bsmp_variable(25, "float"),
            "duration": self.read_bsmp_variable(26, "float"),
            "source_data": self.read_bsmp_variable(27, "uint32_t"),
        }

    def sync_pulse(self) -> bytes:
        payload_size = size_to_hex(1)  # Payload: ID
        send_packet = (
            COM_FUNCTION + payload_size + index_to_hex(list_func.index("sync_pulse"))
        )
        return self._transfer(send_packet, 6)

    def select_op_mode(self, op_mode: int) -> bytes:
        payload_size = size_to_hex(1 + 2)  # Payload: ID + enable
        hex_op_mode = double_to_hex(list_op_mode.index(op_mode))
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("select_op_mode"))
            + hex_op_mode
        )
        return self._transfer(send_packet, 6)

    def set_serial_termination(self, term_enable: int) -> bytes:
        payload_size = size_to_hex(1 + 2)  # Payload: ID + enable
        hex_enable = double_to_hex(term_enable)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("set_serial_termination"))
            + hex_enable
        )
        return self._transfer(send_packet, 6)

    def set_command_interface(self, interface: int) -> bytes:
        payload_size = size_to_hex(1 + 2)  # Payload: ID + enable
        hex_interface = double_to_hex(interface)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("set_command_interface"))
            + hex_interface
        )
        return self._transfer(send_packet, 6)

    def unlock_udc(self, password: int) -> bytes:
        """Unlocks UDC, enables password protected commands to be ran"""
        payload_size = size_to_hex(1 + 2)  # Payload: ID + password
        hex_password = double_to_hex(password)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("unlock_udc"))
            + hex_password
        )
        return self._transfer(send_packet, 6)

    def lock_udc(self, password: int) -> bytes:
        """Locks UDC, disables password protected commands"""
        payload_size = size_to_hex(1 + 2)  # Payload: ID + password
        hex_password = double_to_hex(password)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("lock_udc"))
            + hex_password
        )
        return self._transfer(send_packet, 6)

    def reset_counters(self) -> bytes:
        payload_size = size_to_hex(1)  # Payload: ID
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("reset_counters"))
        )
        return self._transfer(send_packet, 6)

    def cfg_siggen(
        self,
        sig_type: int,
        num_cycles: int,
        freq: float,
        amplitude: float,
        offset: float,
        aux0: float,
        aux1: float,
        aux2: float,
        aux3: float,
    ) -> bytes:
        # TODO: take aux as list?
        payload_size = size_to_hex(1 + 2 + 2 + 4 + 4 + 4 + 4 * 4)
        hex_sig_type = double_to_hex(list_sig_gen_types.index(sig_type))
        hex_num_cycles = double_to_hex(num_cycles)
        hex_freq = float_to_hex(freq)
        hex_amplitude = float_to_hex(amplitude)
        hex_offset = float_to_hex(offset)
        hex_aux0 = float_to_hex(aux0)
        hex_aux1 = float_to_hex(aux1)
        hex_aux2 = float_to_hex(aux2)
        hex_aux3 = float_to_hex(aux3)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("cfg_siggen"))
            + hex_sig_type
            + hex_num_cycles
            + hex_freq
            + hex_amplitude
            + hex_offset
            + hex_aux0
            + hex_aux1
            + hex_aux2
            + hex_aux3
        )
        return self._transfer(send_packet, 6)

    def set_siggen(self, freq: float, amplitude: float, offset: float) -> bytes:
        """Updates signal generator parameters in continuous operation.
        Amplitude and offset are updated instantaneously, frequency is
        updated on the next 1 second update cycle. *This function cannot be
        applied in trapezoidal mode."""
        payload_size = size_to_hex(1 + 4 + 4 + 4)
        hex_freq = float_to_hex(freq)
        hex_amplitude = float_to_hex(amplitude)
        hex_offset = float_to_hex(offset)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("set_siggen"))
            + hex_freq
            + hex_amplitude
            + hex_offset
        )
        return self._transfer(send_packet, 6)

    def enable_siggen(self) -> bytes:
        """Enables signal generator"""
        payload_size = size_to_hex(1)  # Payload: ID
        send_packet = (
            COM_FUNCTION + payload_size + index_to_hex(list_func.index("enable_siggen"))
        )
        return self._transfer(send_packet, 6)

    def disable_siggen(self) -> bytes:
        """Disables signal generator"""
        payload_size = size_to_hex(1)  # Payload: ID
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("disable_siggen"))
        )
        return self._transfer(send_packet, 6)

    def cfg_wfmref(
        self,
        idx: int,
        sync_mode: int,
        frequency: float,
        gain: float = 1.0,
        offset: int = 0,
    ) -> bytes:
        payload_size = size_to_hex(
            1 + 2 + 2 + 4 + 4 + 4
        )  # Payload: ID + idx + sync_mode + frequency + gain + offset
        hex_idx = double_to_hex(idx)
        hex_mode = double_to_hex(sync_mode)
        hex_freq = float_to_hex(frequency)
        hex_gain = float_to_hex(gain)
        hex_offset = float_to_hex(offset)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("cfg_wfmref"))
            + hex_idx
            + hex_mode
            + hex_freq
            + hex_gain
            + hex_offset
        )
        return self._transfer(send_packet, 6)

    def select_wfmref(self, idx: int) -> bytes:
        """Selects index in current waveform, loads waveform into
        wfmref_data."""
        payload_size = size_to_hex(1 + 2)  # Payload: ID + idx
        hex_idx = double_to_hex(idx)
        send_packet = (
            COM_FUNCTION
            + payload_size
            + index_to_hex(list_func.index("select_wfmref"))
            + hex_idx
        )
        return self._transfer(send_packet, 6)

    def reset_wfmref(self) -> bytes:
        """Resets WfmRef, next sync pulse takes index back to the
        waveform's start."""
        payload_size = size_to_hex(1)  # Payload: ID
        send_packet = (
            COM_FUNCTION + payload_size + index_to_hex(list_func.index("reset_wfmref"))
        )
        return self._transfer(send_packet, 6)

    def get_wfmref_vars(self, curve_id: int):
        return {
            "curve_id": curve_id,
            "length": (
                self.read_bsmp_variable(20 + curve_id * 3, "uint32_t")
                - self.read_bsmp_variable(19 + curve_id * 3, "uint32_t")
            )
            / 2
            + 1,
            "index": (
                self.read_bsmp_variable(21 + curve_id * 3, "uint32_t")
                - self.read_bsmp_variable(19 + curve_id * 3, "uint32_t")
            )
            / 2
            + 1,
            "wfmref_selected": self.read_bsmp_variable(14, "uint16_t"),
            "sync_mode": self.read_bsmp_variable(15, "uint16_t"),
            "frequency": self.read_bsmp_variable(16, "float"),
            "gain": self.read_bsmp_variable(17, "float"),
            "offset": self.read_bsmp_variable(18, "float"),
        }

    def read_csv_file(self, filename: str, type: str = "float") -> list:
        csv_list = []
        with open(filename, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if type == "float":
                    row_converted = float(row[0])
                elif type == "string" or type == "str":
                    row_converted = str(row[0])
                csv_list.append(row_converted)
        print("Length of list: " + str(len(csv_list)) + "\n")
        return csv_list

    """
    ======================================================================
                Métodos de Leitura de Valores das Variáveis BSMP
    O retorno do método são os valores double/float da respectiva variavel
    ======================================================================
    """

    def read_bsmp_variable(self, id_var: int, type_var: int, print_msg: bool = False):
        reply_msg = self.read_var(index_to_hex(id_var), type_size[type_var])
        # TODO: Remove print_msg?
        if print_msg:
            print(reply_msg)
        val = struct.unpack(type_format[type_var], reply_msg)
        return val[3]

    def read_bsmp_variable_gen(self, id_var: int, size_bytes: int) -> bytes:
        return self.read_var(index_to_hex(id_var), size_bytes + 5)

    def read_udc_arm_version(self) -> str:
        reply_msg = self.read_var(index_to_hex(3), 133)
        val = struct.unpack("16s", reply_msg[4:20])
        return val[0].decode("utf-8")

    def read_udc_c28_version(self) -> str:
        reply_msg = self.read_var(index_to_hex(3), 133)
        val = struct.unpack("16s", reply_msg[20:36])
        return val[0].decode("utf-8")

    def read_udc_version(self) -> dict:
        return {"arm": self.read_udc_arm_version(), "c28": self.read_udc_c28_version()}

    """
    ======================================================================
                Métodos de Escrita de Valores das Variáveis BSMP
            O retorno do método são os bytes de retorno da mensagem
    ======================================================================
    """

    def Write_sigGen_Freq(self, float_value):
        # TODO: Fix method name
        hex_float = float_to_hex(float_value)
        send_packet = (
            COM_WRITE_VAR
            + WRITE_FLOAT_SIZE_PAYLOAD
            + index_to_hex(list_common_vars.index("sigGen_Freq"))
            + hex_float
        )
        return self._transfer(send_packet, 5)

    def Write_sigGen_Amplitude(self, float_value):
        # TODO: Fix method name
        hex_float = float_to_hex(float_value)
        send_packet = (
            COM_WRITE_VAR
            + WRITE_FLOAT_SIZE_PAYLOAD
            + index_to_hex(list_common_vars.index("sigGen_Amplitude"))
            + hex_float
        )
        return self._transfer(send_packet, 5)

    def Write_sigGen_Offset(self, float_value):
        # TODO: Fix method name
        hex_float = float_to_hex(float_value)
        send_packet = (
            COM_WRITE_VAR
            + WRITE_FLOAT_SIZE_PAYLOAD
            + index_to_hex(list_common_vars.index("sigGen_Offset"))
            + hex_float
        )
        return self._transfer(send_packet, 5)

    def Write_sigGen_Aux(self, float_value):
        # TODO: Fix method name
        hex_float = float_to_hex(float_value)
        send_packet = (
            COM_WRITE_VAR
            + WRITE_FLOAT_SIZE_PAYLOAD
            + index_to_hex(list_common_vars.index("sigGen_Aux"))
            + hex_float
        )
        return self._transfer(send_packet, 5)

    def Write_dp_ID(self, double_value):
        # TODO: Fix method name
        hex_double = double_to_hex(double_value)
        send_packet = (
            COM_WRITE_VAR
            + WRITE_DOUBLE_SIZE_PAYLOAD
            + index_to_hex(list_common_vars.index("dp_ID"))
            + hex_double
        )
        return self._transfer(send_packet, 5)

    def Write_dp_Class(self, double_value):
        # TODO: Fix method name
        hex_double = double_to_hex(double_value)
        send_packet = (
            COM_WRITE_VAR
            + WRITE_DOUBLE_SIZE_PAYLOAD
            + index_to_hex(list_common_vars.index("dp_Class"))
            + hex_double
        )
        return self._transfer(send_packet, 5)

    def Write_dp_Coeffs(self, list_float):
        # TODO: Fix method name
        hex_float_list = []
        # list_full = list_float[:]

        # while(len(list_full) < self.dp_module_max_coeff):
        #    list_full.append(0)

        list_full = [0 for i in range(DP_MODULE_MAX_COEFF)]
        list_full[: len(list_float)] = list_float[:]

        for float_value in list_full:
            hex_float = float_to_hex(float(float_value))
            hex_float_list.append(hex_float)
        str_float_list = "".join(hex_float_list)
        payload_size = size_to_hex(
            1 + 4 * DP_MODULE_MAX_COEFF
        )  # Payload: ID + 16floats
        send_packet = (
            COM_WRITE_VAR
            + payload_size
            + index_to_hex(list_common_vars.index("dp_Coeffs"))
            + str_float_list
        )
        return self._transfer(send_packet, 5)

    """
    ======================================================================
                     Métodos de Escrita de Curvas BSMP
            O retorno do método são os bytes de retorno da mensagem
    ======================================================================
    """

    def send_wfmref_curve(self, block_idx: int, data) -> bytes:
        # TODO: Could use list comprehension in val
        block_hex = size_to_hex(block_idx)
        val = []
        for k in range(0, len(data)):
            val.append(float_to_hex(float(data[k])))
        payload_size = size_to_hex((len(val) * 4) + 3)
        curve_hex = "".join(val)
        send_packet = (
            COM_SEND_WFM_REF
            + payload_size
            + index_to_hex(list_curv.index("wfmRef_Curve"))
            + block_hex
            + curve_hex
        )
        return self._transfer(send_packet, 5)

    def recv_wfmref_curve(self, block_idx: int) -> list:
        # TODO: Will always fail, wfmRef_Curve is not in list
        block_hex = size_to_hex(block_idx)
        payload_size = size_to_hex(1 + 2)  # Payload: ID+Block_index
        send_packet = (
            COM_REQUEST_CURVE
            + payload_size
            + index_to_hex(list_curv.index("wfmRef_Curve"))
            + block_hex
        )
        # Address+Command+Size+ID+Block_idx+data+checksum
        recv_msg = self._transfer(send_packet, 1 + 1 + 2 + 1 + 2 + 8192 + 1)
        val = []
        for k in range(7, len(recv_msg) - 1, 4):
            val.append(struct.unpack("f", recv_msg[k : k + 4]))
        return val

    def recv_samples_buffer(self) -> list:
        # TODO: Will always fail, samplesBuffer is not in list
        block_hex = size_to_hex(0)
        payload_size = size_to_hex(1 + 2)  # Payload: ID+Block_index
        send_packet = (
            COM_REQUEST_CURVE
            + payload_size
            + index_to_hex(list_curv.index("samplesBuffer"))
            + block_hex
        )
        # Address+Command+Size+ID+Block_idx+data+checksum
        recv_msg = self._transfer(send_packet, 1 + 1 + 2 + 1 + 2 + 16384 + 1)
        val = []
        try:
            for k in range(7, len(recv_msg) - 1, 4):
                val.extend(struct.unpack("f", recv_msg[k : k + 4]))
        except:
            pass
        return val

    def send_full_wfmref_curve(self, block_idx: int, data) -> bytes:
        # TODO: Will always fail, fullwfmRef_Curve is not in list
        block_hex = size_to_hex(block_idx)
        val = []
        for k in range(0, len(data)):
            val.append(float_to_hex(float(data[k])))
        payload_size = size_to_hex(len(val) * 4 + 3)
        curve_hex = "".join(val)
        send_packet = (
            COM_SEND_WFM_REF
            + payload_size
            + index_to_hex(list_curv.index("fullwfmRef_Curve"))
            + block_hex
            + curve_hex
        )
        return self._transfer(send_packet, 5)

    def recv_full_wfmref_curve(self, block_idx: int) -> list:
        # TODO: Will always fail, fullwfmRef_Curve is not in list
        block_hex = size_to_hex(block_idx)
        payload_size = size_to_hex(1 + 2)  # Payload: ID+Block_index
        send_packet = (
            COM_REQUEST_CURVE
            + payload_size
            + index_to_hex(list_curv.index("fullwfmRef_Curve"))
            + block_hex
        )
        recv_msg = self._transfer(send_packet, 1 + 1 + 2 + 1 + 2 + 16384 + 1)
        val = []
        for k in range(7, len(recv_msg) - 1, 4):
            val.append(struct.unpack("f", recv_msg[k : k + 4]))
        return val

    def recv_samples_buffer_blocks(self, block_idx: int) -> list:
        # TODO: Will always fail, samplesBuffer_blocks is not in list
        block_hex = size_to_hex(block_idx)
        payload_size = size_to_hex(1 + 2)  # Payload: ID+Block_index
        send_packet = (
            COM_REQUEST_CURVE
            + payload_size
            + index_to_hex(list_curv.index("samplesBuffer_blocks"))
            + block_hex
        )
        # t0 = time.time()
        # Address+Command+Size+ID+Block_idx+data+checksum
        recv_msg = self._transfer(send_packet, 1 + 1 + 2 + 1 + 2 + 1024 + 1)
        # print(time.time()-t0)
        # print(recv_msg)
        val = []
        for k in range(7, len(recv_msg) - 1, 4):
            val.extend(struct.unpack("f", recv_msg[k : k + 4]))
        return val

    def recv_samples_buffer_allblocks(self) -> list:
        # TODO: Will fail
        buff = []
        # self.DisableSamplesBuffer()
        for i in range(0, 16):
            # t0 = time.time()
            buff.extend(self.recv_samples_buffer_blocks(i))
            # print(time.time()-t0)
        # self.EnableSamplesBuffer()
        return buff

    def read_curve_block(self, curve_id: int, block_id: int) -> list:
        block_hex = size_to_hex(block_id)
        payload_size = size_to_hex(1 + 2)  # Payload: curve_id + block_id
        send_packet = (
            COM_REQUEST_CURVE + payload_size + index_to_hex(curve_id) + block_hex
        )
        # t0 = time.time()
        self._reset_input_buffer()
        # Address+Command+Size+ID+Block_idx+data+checksum
        recv_msg = self._transfer(
            send_packet, 1 + 1 + 2 + 1 + 2 + size_curve_block[curve_id] + 1
        )
        # print(time.time()-t0)
        # print(recv_msg)
        val = []
        for k in range(7, len(recv_msg) - 1, 4):
            val.extend(struct.unpack("f", recv_msg[k : k + 4]))
        return val

    def write_curve_block(self, curve_id: int, block_id: int, data) -> bytes:
        block_hex = size_to_hex(block_id)
        val = []
        for k in range(0, len(data)):
            val.append(float_to_hex(float(data[k])))
        payload_size = size_to_hex(len(val) * 4 + 3)
        curve_hex = "".join(val)
        send_packet = (
            COM_SEND_WFM_REF
            + payload_size
            + index_to_hex(curve_id)
            + block_hex
            + curve_hex
        )
        return self._transfer(send_packet, 5)

    def write_wfmref(self, curve: int, data) -> list:
        # curve = list_curv.index('wfmref')
        block_size = int(size_curve_block[curve] / 4)
        # print(block_size)

        blocks = [data[x : x + block_size] for x in range(0, len(data), block_size)]

        ps_status = self.read_ps_status()

        wfmref_selected = self.read_bsmp_variable(14, "uint16_t")

        if (wfmref_selected == curve) and (
            ps_status["state"] == "RmpWfm" or ps_status["state"] == "MigWfm"
        ):
            raise RuntimeError(
                "The specified curve ID is currently selected and PS is on {} state. Choose a different curve ID.".format(
                    ps_status["state"]
                )
            )

        else:
            for block_id in range(len(blocks)):
                self.write_curve_block(curve, block_id, blocks[block_id])

        return blocks

    def read_buf_samples_ctom(self) -> list:
        buf = []
        curve_id = list_curv.index("buf_samples_ctom")

        ps_status = self.read_ps_status()
        if ps_status["model"] == "FBP":
            for i in range(num_blocks_curves_fbp[curve_id]):
                buf.extend(self.read_curve_block(curve_id, i))
        else:
            for i in range(num_blocks_curves_fax[curve_id]):
                buf.extend(self.read_curve_block(curve_id, i))

        return buf

    """
    ======================================================================
                      Funções auxiliares
    ======================================================================
    """

    def read_vars_common(self, all=False):

        loop_state = ["Closed Loop", "Open Loop"]

        ps_status = self.read_ps_status()
        if ps_status["open_loop"] == 0:
            if (
                (ps_status["model"] == "FAC_ACDC")
                or (ps_status["model"] == "FAC_2S_ACDC")
                or (ps_status["model"] == "FAC_2P4S_ACDC")
            ):
                setpoint_unit = " V"
            else:
                setpoint_unit = " A"
        else:
            setpoint_unit = " %"

        resp = {
            "ps_model": ps_status["model"],
            "state": ps_status["state"],
            "loop_state": loop_state[ps_status["open_loop"]],
            "setpoint": str(round(self.read_bsmp_variable(1, "float"), 3))
            + setpoint_unit,
            "reference": str(round(self.read_bsmp_variable(2, "float"), 3))
            + setpoint_unit,
        }

        if not all:
            return resp

        resp_add = {
            "status": self.read_ps_status(),
            "counter_set_slowref": self.read_bsmp_variable(4, "uint32_t"),
            "counter_sync_pulse": self.read_bsmp_variable(5, "uint32_t"),
            "wfm_ref_0": self.get_wfmref_vars(0),
            "wfm_ref_1": self.get_wfmref_vars(1),
            "scope": self.get_scope_vars(),
            "sig_gen": self.get_siggen_vars(),
        }

        return {**resp, **resp_add}

    def _interlock_unknown_assignment(self, active_interlocks, index):
        active_interlocks.append("bit {}: Reserved".format(index))

    def _interlock_name_assigned(self, active_interlocks, index, list_interlocks):
        active_interlocks.append("bit {}: {}".format(index, list_interlocks[index]))

    def _include_interlocks(self, vars: dict):
        soft_itlks = self.read_bsmp_variable(31, "uint32_t")
        if soft_itlks != 0:
            vars["soft_interlocks"] = self.decode_interlocks(
                soft_itlks, list_fbp_soft_interlocks
            )

        hard_itlks = self.read_bsmp_variable(32, "uint32_t")
        if hard_itlks != 0:
            vars["hard_interlocks"] = self.decode_interlocks(
                hard_itlks, list_fbp_hard_interlocks
            )

        return vars

    def decode_interlocks(self, reg_interlocks, list_interlocks: list) -> list:
        active_interlocks = []
        for index in range(32):
            if reg_interlocks & (1 << index):
                if index < len(list_interlocks):
                    self._interlock_name_assigned(
                        active_interlocks, index, list_interlocks
                    )
                else:
                    self._interlock_unknown_assignment(active_interlocks, index)

        return active_interlocks

    def read_vars_fbp(self, n: int = 1, dt: float = 0.5):
        vars_list = []
        for _ in range(n):
            self.read_vars_common()

            vars = {
                "load_current": str(round(self.read_bsmp_variable(33, "float"), 3))
                + " A",
                "load_voltage": str(round(self.read_bsmp_variable(34, "float"), 3))
                + " V",
                "load_resistance": str(
                    abs(
                        round(
                            self.read_bsmp_variable(34, "float")
                            / self.read_bsmp_variable(33, "float"),
                            3,
                        )
                    )
                )
                + " Ohm",
                "load_power": str(
                    abs(
                        round(
                            self.read_bsmp_variable(34, "float")
                            * self.read_bsmp_variable(33, "float"),
                            3,
                        )
                    )
                )
                + " W",
                "dc_link_voltage": str(round(self.read_bsmp_variable(35, "float"), 3))
                + " V",
                "heatsink_temp": str(round(self.read_bsmp_variable(36, "float"), 3))
                + " °C",
                "duty_cycle": str(round(self.read_bsmp_variable(37, "float"), 3))
                + " %",
            }

            vars_list.append(self._include_interlocks(vars))

            time.sleep(dt)
        return vars_list

    def read_vars_fbp_dclink(self, n: int = 1, dt: float = 0.5) -> list:
        vars_list = []
        try:
            for i in range(n):
                self.read_vars_common()

                vars = {
                    "measurement_number": i + 1,
                    "modules_status": self.read_bsmp_variable(33, "uint32_t"),
                    "dc-link_voltage": str(
                        round(self.read_bsmp_variable(34, "float"), 3)
                    )
                    + " V",
                    "ps1_voltage": str(round(self.read_bsmp_variable(35, "float"), 3))
                    + " V",
                    "ps2_voltage": str(round(self.read_bsmp_variable(36, "float"), 3))
                    + " V",
                    "ps3_voltage": str(round(self.read_bsmp_variable(37, "float"), 3))
                    + " V",
                    "dig_pot_tap": self.read_bsmp_variable(38, "uint8_t"),
                }

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                if hard_itlks:
                    vars["hard_interlocks"] = self.decode_interlocks(
                        hard_itlks, list_fbp_dclink_hard_interlocks
                    )

                vars_list.append(vars)
                time.sleep(dt)

        except Exception:
            pass

    def read_vars_fac_acdc(self, n=1, dt: float = 0.5, iib: bool = True):
        for i in range(n):

            print(
                "\n--- Measurement #"
                + str(i + 1)
                + " ------------------------------------------\n"
            )
            self.read_vars_common()

            soft_itlks = self.read_bsmp_variable(31, "uint32_t")
            print("\nSoft Interlocks: " + str(soft_itlks))
            if soft_itlks:
                self.decode_interlocks(soft_itlks, list_fac_acdc_soft_interlocks)
                print("")

            hard_itlks = self.read_bsmp_variable(32, "uint32_t")
            print("Hard Interlocks: " + str(hard_itlks))
            if hard_itlks:
                self.decode_interlocks(hard_itlks, list_fac_acdc_hard_interlocks)

            iib_is_itlks = self.read_bsmp_variable(45, "uint32_t")
            print("\nIIB IS Interlocks: " + str(iib_is_itlks))
            if iib_is_itlks:
                self.decode_interlocks(iib_is_itlks, list_fac_acdc_iib_is_interlocks)

            iib_is_alarms = self.read_bsmp_variable(46, "uint32_t")
            print("IIB IS Alarms: " + str(iib_is_alarms))
            if iib_is_alarms:
                self.decode_interlocks(iib_is_alarms, list_fac_acdc_iib_is_alarms)

            iib_cmd_itlks = self.read_bsmp_variable(57, "uint32_t")
            print("\nIIB Cmd Interlocks: " + str(iib_cmd_itlks))
            if iib_cmd_itlks:
                self.decode_interlocks(iib_cmd_itlks, list_fac_acdc_iib_cmd_interlocks)

            iib_cmd_alarms = self.read_bsmp_variable(58, "uint32_t")
            print("IIB Cmd Alarms: " + str(iib_cmd_alarms))
            if iib_cmd_alarms:
                self.decode_interlocks(iib_cmd_alarms, list_fac_acdc_iib_cmd_alarms)

            print(
                "\nCapBank Voltage: "
                + str(round(self.read_bsmp_variable(33, "float"), 3))
                + " V"
            )
            print(
                "Rectifier Current: "
                + str(round(self.read_bsmp_variable(34, "float"), 3))
                + " A"
            )

            print(
                "Duty-Cycle: "
                + str(round(self.read_bsmp_variable(35, "float"), 3))
                + " %"
            )

            if iib:
                print(
                    "\nIIB IS Input Current: "
                    + str(round(self.read_bsmp_variable(36, "float"), 3))
                    + " A"
                )
                print(
                    "IIB IS Input Voltage: "
                    + str(round(self.read_bsmp_variable(37, "float"), 3))
                    + " V"
                )
                print(
                    "IIB IS IGBT Temp: "
                    + str(round(self.read_bsmp_variable(38, "float"), 3))
                    + " °C"
                )
                print(
                    "IIB IS Driver Voltage: "
                    + str(round(self.read_bsmp_variable(39, "float"), 3))
                    + " V"
                )
                print(
                    "IIB IS Driver Current: "
                    + str(round(self.read_bsmp_variable(40, "float"), 3))
                    + " A"
                )
                print(
                    "IIB IS Inductor Temp: "
                    + str(round(self.read_bsmp_variable(41, "float"), 3))
                    + " °C"
                )
                print(
                    "IIB IS Heat-Sink Temp: "
                    + str(round(self.read_bsmp_variable(42, "float"), 3))
                    + " °C"
                )
                print(
                    "IIB IS Board Temp: "
                    + str(round(self.read_bsmp_variable(43, "float"), 3))
                    + " °C"
                )
                print(
                    "IIB IS Board RH: "
                    + str(round(self.read_bsmp_variable(44, "float"), 3))
                    + " %"
                )
                print(
                    "IIB IS Interlocks: "
                    + str(round(self.read_bsmp_variable(45, "uint32_t"), 3))
                )
                print(
                    "IIB IS Alarms: "
                    + str(round(self.read_bsmp_variable(46, "uint32_t"), 3))
                )

                print(
                    "\nIIB Cmd Load Voltage: "
                    + str(round(self.read_bsmp_variable(47, "float"), 3))
                    + " V"
                )
                print(
                    "IIB Cmd CapBank Voltage: "
                    + str(round(self.read_bsmp_variable(48, "float"), 3))
                    + " V"
                )
                print(
                    "IIB Cmd Rectifier Inductor Temp: "
                    + str(round(self.read_bsmp_variable(49, "float"), 3))
                    + " °C"
                )
                print(
                    "IIB Cmd Rectifier Heat-Sink Temp: "
                    + str(round(self.read_bsmp_variable(50, "float"), 3))
                    + " °C"
                )
                print(
                    "IIB Cmd External Boards Voltage: "
                    + str(round(self.read_bsmp_variable(51, "float"), 3))
                    + " V"
                )
                print(
                    "IIB Cmd Auxiliary Board Current: "
                    + str(round(self.read_bsmp_variable(52, "float"), 3))
                    + " A"
                )
                print(
                    "IIB Cmd IDB Board Current: "
                    + str(round(self.read_bsmp_variable(53, "float"), 3))
                    + " A"
                )
                print(
                    "IIB Cmd Ground Leakage Current: "
                    + str(round(self.read_bsmp_variable(54, "float"), 3))
                    + " A"
                )
                print(
                    "IIB Cmd Board Temp: "
                    + str(round(self.read_bsmp_variable(55, "float"), 3))
                    + " °C"
                )
                print(
                    "IIB Cmd Board RH: "
                    + str(round(self.read_bsmp_variable(56, "float"), 3))
                    + " %"
                )
                print(
                    "IIB Cmd Interlocks: "
                    + str(round(self.read_bsmp_variable(57, "uint32_t"), 3))
                )
                print(
                    "IIB Cmd Alarms: "
                    + str(round(self.read_bsmp_variable(58, "uint32_t"), 3))
                )

            time.sleep(dt)

        # except:
        #    pass

    def read_vars_fac_dcdc(self, n=1, dt=0.5, iib=1):

        try:
            for i in range(n):

                print(
                    "\n--- Measurement #"
                    + str(i + 1)
                    + " ------------------------------------------\n"
                )
                self.read_vars_common()

                print(
                    "\nSync Pulse Counter: "
                    + str(round(self.read_bsmp_variable(5, "uint32_t"), 3))
                )
                print(
                    "WfmRef Index: "
                    + str(
                        (
                            round(self.read_bsmp_variable(20, "uint32_t"), 3)
                            - round(self.read_bsmp_variable(18, "uint32_t"), 3)
                        )
                        / 2
                        + 1
                    )
                )

                soft_itlks = self.read_bsmp_variable(31, "uint32_t")
                print("\nSoft Interlocks: " + str(soft_itlks))
                if soft_itlks:
                    self.decode_interlocks(soft_itlks, list_fac_dcdc_soft_interlocks)
                    print("")

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                print("Hard Interlocks: " + str(hard_itlks))
                if hard_itlks:
                    self.decode_interlocks(hard_itlks, list_fac_dcdc_hard_interlocks)

                iib_itlks = self.read_bsmp_variable(51, "uint32_t")
                print("\nIIB Interlocks: " + str(iib_itlks))
                if iib_itlks:
                    self.decode_interlocks(iib_itlks, list_fac_dcdc_iib_interlocks)

                iib_alarms = self.read_bsmp_variable(52, "uint32_t")
                print("IIB Alarms: " + str(iib_alarms))
                if iib_alarms:
                    self.decode_interlocks(iib_alarms, list_fac_dcdc_iib_alarms)

                print(
                    "\nLoad Current: "
                    + str(round(self.read_bsmp_variable(33, "float"), 3))
                    + " A"
                )
                print(
                    "Load Current DCCT 1: "
                    + str(round(self.read_bsmp_variable(34, "float"), 3))
                    + " A"
                )
                print(
                    "Load Current DCCT 2: "
                    + str(round(self.read_bsmp_variable(35, "float"), 3))
                    + " A"
                )

                print(
                    "\nCapBank Voltage: "
                    + str(round(self.read_bsmp_variable(36, "float"), 3))
                    + " V"
                )

                print(
                    "\nDuty-Cycle: "
                    + str(round(self.read_bsmp_variable(37, "float"), 3))
                    + " %"
                )

                if iib:
                    print(
                        "\nIIB CapBank Voltage: "
                        + str(round(self.read_bsmp_variable(38, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Input Current: "
                        + str(round(self.read_bsmp_variable(39, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Output Current: "
                        + str(round(self.read_bsmp_variable(40, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB IGBT Leg 1 Temp: "
                        + str(round(self.read_bsmp_variable(41, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB IGBT Leg 2 Temp: "
                        + str(round(self.read_bsmp_variable(42, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Inductor Temp: "
                        + str(round(self.read_bsmp_variable(43, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Heat-Sink Temp: "
                        + str(round(self.read_bsmp_variable(44, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Driver Voltage: "
                        + str(round(self.read_bsmp_variable(45, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Driver Current 1: "
                        + str(round(self.read_bsmp_variable(46, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Driver Current 2: "
                        + str(round(self.read_bsmp_variable(47, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Ground Leakage Current: "
                        + str(round(self.read_bsmp_variable(48, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Board Temp: "
                        + str(round(self.read_bsmp_variable(49, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Board RH: "
                        + str(round(self.read_bsmp_variable(50, "float"), 3))
                        + " %"
                    )
                    print(
                        "IIB Interlocks: "
                        + str(round(self.read_bsmp_variable(51, "uint32_t"), 3))
                    )
                    print(
                        "IIB Alarms: "
                        + str(round(self.read_bsmp_variable(52, "uint32_t"), 3))
                    )

                time.sleep(dt)

        except:
            pass

    def read_vars_fac_dcdc_ema(self, n=1, dt=0.5, iib=0):

        try:
            for i in range(n):

                print(
                    "\n--- Measurement #"
                    + str(i + 1)
                    + " ------------------------------------------\n"
                )
                self.read_vars_common()

                soft_itlks = self.read_bsmp_variable(31, "uint32_t")
                print("\nSoft Interlocks: " + str(soft_itlks))
                if soft_itlks:
                    self.decode_interlocks(
                        soft_itlks, list_fac_dcdc_ema_soft_interlocks
                    )
                    print("")

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                print("Hard Interlocks: " + str(hard_itlks))
                if hard_itlks:
                    self.decode_interlocks(
                        hard_itlks, list_fac_dcdc_ema_hard_interlocks
                    )

                iib_itlks = self.read_bsmp_variable(49, "uint32_t")
                print("IIB Interlocks: " + str(iib_itlks))
                if iib_itlks:
                    self.decode_interlocks(iib_itlks, list_fac_dcdc_ema_iib_interlocks)

                iib_alarms = self.read_bsmp_variable(50, "uint32_t")
                print("IIB Alarms: " + str(iib_alarms))
                if iib_alarms:
                    self.decode_interlocks(iib_alarms, list_fac_dcdc_ema_iib_alarms)

                print(
                    "\nLoad Current: "
                    + str(round(self.read_bsmp_variable(33, "float"), 3))
                )
                print(
                    "DC-Link Voltage: "
                    + str(round(self.read_bsmp_variable(34, "float"), 3))
                )
                print(
                    "\nDuty-Cycle: "
                    + str(round(self.read_bsmp_variable(35, "float"), 3))
                )

                if iib:
                    print(
                        "\nIIB Input Voltage: "
                        + str(round(self.read_bsmp_variable(36, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Input Current: "
                        + str(round(self.read_bsmp_variable(37, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Output Current: "
                        + str(round(self.read_bsmp_variable(38, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB IGBT 1 Temp: "
                        + str(round(self.read_bsmp_variable(39, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB IGBT 2 Temp: "
                        + str(round(self.read_bsmp_variable(40, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Inductor Temp: "
                        + str(round(self.read_bsmp_variable(41, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Heat-Sink Temp: "
                        + str(round(self.read_bsmp_variable(42, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Driver Voltage: "
                        + str(round(self.read_bsmp_variable(43, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Driver Current 1: "
                        + str(round(self.read_bsmp_variable(44, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Driver Current 2: "
                        + str(round(self.read_bsmp_variable(45, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Ground Leakage Current: "
                        + str(round(self.read_bsmp_variable(46, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Board Temp: "
                        + str(round(self.read_bsmp_variable(47, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Board RH: "
                        + str(round(self.read_bsmp_variable(48, "float"), 3))
                        + " %"
                    )
                    print(
                        "IIB Interlocks: "
                        + str(round(self.read_bsmp_variable(49, "uint32_t"), 3))
                    )
                    print(
                        "IIB Alarms: "
                        + str(round(self.read_bsmp_variable(50, "uint32_t"), 3))
                    )

                time.sleep(dt)

        except:
            pass

    def read_vars_fac_2s_acdc(self, n=1, add_mod_a=2, dt=0.5, iib=0):

        old_add = self.slave_add

        try:
            for i in range(n):

                self.slave_add = add_mod_a

                print(
                    "\n--- Measurement #"
                    + str(i + 1)
                    + " ------------------------------------------\n"
                )
                self.read_vars_common()

                print("\n *** MODULE A ***")

                soft_itlks = self.read_bsmp_variable(31, "uint32_t")
                print("\nSoft Interlocks: " + str(soft_itlks))
                if soft_itlks:
                    self.decode_interlocks(soft_itlks, list_fac_2s_acdc_soft_interlocks)
                    print("")

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                print("Hard Interlocks: " + str(hard_itlks))
                if hard_itlks:
                    self.decode_interlocks(hard_itlks, list_fac_2s_acdc_hard_interlocks)

                iib_is_itlks = self.read_bsmp_variable(45, "uint32_t")
                print("\nIIB IS Interlocks: " + str(iib_is_itlks))
                if iib_is_itlks:
                    self.decode_interlocks(
                        iib_is_itlks, list_fac_2s_acdc_iib_is_interlocks
                    )

                iib_is_alarms = self.read_bsmp_variable(46, "uint32_t")
                print("IIB IS Alarms: " + str(iib_is_alarms))
                if iib_is_alarms:
                    self.decode_interlocks(
                        iib_is_alarms, list_fac_2s_acdc_iib_is_alarms
                    )

                iib_cmd_itlks = self.read_bsmp_variable(57, "uint32_t")
                print("\nIIB Cmd Interlocks: " + str(iib_cmd_itlks))
                if iib_cmd_itlks:
                    self.decode_interlocks(
                        iib_cmd_itlks, list_fac_2s_acdc_iib_cmd_interlocks
                    )

                iib_cmd_alarms = self.read_bsmp_variable(58, "uint32_t")
                print("IIB Cmd Alarms: " + str(iib_cmd_alarms))
                if iib_cmd_alarms:
                    self.decode_interlocks(
                        iib_cmd_alarms, list_fac_2s_acdc_iib_cmd_alarms
                    )

                print(
                    "\nCapBank Voltage: "
                    + str(round(self.read_bsmp_variable(33, "float"), 3))
                    + " V"
                )
                print(
                    "Rectifier Current: "
                    + str(round(self.read_bsmp_variable(34, "float"), 3))
                    + " A"
                )
                print(
                    "Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(35, "float"), 3))
                    + " %"
                )

                if iib:
                    print(
                        "\nIIB IS Input Current: "
                        + str(round(self.read_bsmp_variable(36, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB IS Input Voltage: "
                        + str(round(self.read_bsmp_variable(37, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB IS IGBT Temp: "
                        + str(round(self.read_bsmp_variable(38, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB IS Driver Voltage: "
                        + str(round(self.read_bsmp_variable(39, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB IS Driver Current: "
                        + str(round(self.read_bsmp_variable(40, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB IS Inductor Temp: "
                        + str(round(self.read_bsmp_variable(41, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB IS Heat-Sink Temp: "
                        + str(round(self.read_bsmp_variable(42, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB IS Board Temp: "
                        + str(round(self.read_bsmp_variable(43, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB IS Board RH: "
                        + str(round(self.read_bsmp_variable(44, "float"), 3))
                        + " %"
                    )
                    print(
                        "IIB IS Interlocks: "
                        + str(round(self.read_bsmp_variable(45, "uint32_t"), 3))
                    )
                    print(
                        "IIB IS Alarms: "
                        + str(round(self.read_bsmp_variable(46, "uint32_t"), 3))
                    )

                    print(
                        "\nIIB Cmd Load Voltage: "
                        + str(round(self.read_bsmp_variable(47, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Cmd CapBank Voltage: "
                        + str(round(self.read_bsmp_variable(48, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Cmd Rectifier Inductor Temp: "
                        + str(round(self.read_bsmp_variable(49, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Cmd Rectifier Heat-Sink Temp: "
                        + str(round(self.read_bsmp_variable(50, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Cmd External Boards Voltage: "
                        + str(round(self.read_bsmp_variable(51, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Cmd Auxiliary Board Current: "
                        + str(round(self.read_bsmp_variable(52, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Cmd IDB Board Current: "
                        + str(round(self.read_bsmp_variable(53, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Cmd Ground Leakage Current: "
                        + str(round(self.read_bsmp_variable(54, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Cmd Board Temp: "
                        + str(round(self.read_bsmp_variable(55, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Cmd Board RH: "
                        + str(round(self.read_bsmp_variable(56, "float"), 3))
                        + " %"
                    )
                    print(
                        "IIB Cmd Interlocks: "
                        + str(round(self.read_bsmp_variable(57, "uint32_t"), 3))
                    )
                    print(
                        "IIB Cmd Alarms: "
                        + str(round(self.read_bsmp_variable(58, "uint32_t"), 3))
                    )

                self.slave_add = add_mod_a + 1

                print("\n *** MODULE B ***")

                soft_itlks = self.read_bsmp_variable(31, "uint32_t")
                print("\nSoft Interlocks: " + str(soft_itlks))
                if soft_itlks:
                    self.decode_interlocks(soft_itlks, list_fac_2s_acdc_soft_interlocks)
                    print("")

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                print("Hard Interlocks: " + str(hard_itlks))
                if hard_itlks:
                    self.decode_interlocks(hard_itlks, list_fac_2s_acdc_hard_interlocks)

                iib_is_itlks = self.read_bsmp_variable(45, "uint32_t")
                print("\nIIB IS Interlocks: " + str(iib_is_itlks))
                if iib_is_itlks:
                    self.decode_interlocks(
                        iib_is_itlks, list_fac_2s_acdc_iib_is_interlocks
                    )

                iib_is_alarms = self.read_bsmp_variable(46, "uint32_t")
                print("IIB IS Alarms: " + str(iib_is_alarms))
                if iib_is_alarms:
                    self.decode_interlocks(
                        iib_is_alarms, list_fac_2s_acdc_iib_is_alarms
                    )

                iib_cmd_itlks = self.read_bsmp_variable(57, "uint32_t")
                print("\nIIB Cmd Interlocks: " + str(iib_cmd_itlks))
                if iib_cmd_itlks:
                    self.decode_interlocks(
                        iib_cmd_itlks, list_fac_2s_acdc_iib_cmd_interlocks
                    )

                iib_cmd_alarms = self.read_bsmp_variable(58, "uint32_t")
                print("IIB Cmd Alarms: " + str(iib_cmd_alarms))
                if iib_cmd_alarms:
                    self.decode_interlocks(
                        iib_cmd_alarms, list_fac_2s_acdc_iib_cmd_alarms
                    )

                print(
                    "\nCapBank Voltage: "
                    + str(round(self.read_bsmp_variable(33, "float"), 3))
                    + " V"
                )
                print(
                    "Rectifier Current: "
                    + str(round(self.read_bsmp_variable(34, "float"), 3))
                    + " A"
                )
                print(
                    "Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(35, "float"), 3))
                    + " %"
                )

                if iib:
                    print(
                        "\nIIB IS Input Current: "
                        + str(round(self.read_bsmp_variable(36, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB IS Input Voltage: "
                        + str(round(self.read_bsmp_variable(37, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB IS IGBT Temp: "
                        + str(round(self.read_bsmp_variable(38, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB IS Driver Voltage: "
                        + str(round(self.read_bsmp_variable(39, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB IS Driver Current: "
                        + str(round(self.read_bsmp_variable(40, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB IS Inductor Temp: "
                        + str(round(self.read_bsmp_variable(41, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB IS Heat-Sink Temp: "
                        + str(round(self.read_bsmp_variable(42, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB IS Board Temp: "
                        + str(round(self.read_bsmp_variable(43, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB IS Board RH: "
                        + str(round(self.read_bsmp_variable(44, "float"), 3))
                        + " %"
                    )
                    print(
                        "IIB IS Interlocks: "
                        + str(round(self.read_bsmp_variable(45, "uint32_t"), 3))
                    )
                    print(
                        "IIB IS Alarms: "
                        + str(round(self.read_bsmp_variable(46, "uint32_t"), 3))
                    )

                    print(
                        "\nIIB Cmd Load Voltage: "
                        + str(round(self.read_bsmp_variable(47, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Cmd CapBank Voltage: "
                        + str(round(self.read_bsmp_variable(48, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Cmd Rectifier Inductor Temp: "
                        + str(round(self.read_bsmp_variable(49, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Cmd Rectifier Heat-Sink Temp: "
                        + str(round(self.read_bsmp_variable(50, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Cmd External Boards Voltage: "
                        + str(round(self.read_bsmp_variable(51, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Cmd Auxiliary Board Current: "
                        + str(round(self.read_bsmp_variable(52, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Cmd IDB Board Current: "
                        + str(round(self.read_bsmp_variable(53, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Cmd Ground Leakage Current: "
                        + str(round(self.read_bsmp_variable(54, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Cmd Board Temp: "
                        + str(round(self.read_bsmp_variable(55, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Cmd Board RH: "
                        + str(round(self.read_bsmp_variable(56, "float"), 3))
                        + " %"
                    )
                    print(
                        "IIB Cmd Interlocks: "
                        + str(round(self.read_bsmp_variable(57, "uint32_t"), 3))
                    )
                    print(
                        "IIB Cmd Alarms: "
                        + str(round(self.read_bsmp_variable(58, "uint32_t"), 3))
                    )

                time.sleep(dt)

            self.slave_add = old_add
        except:
            self.slave_addr = old_add

    def read_vars_fac_2s_dcdc(self, n=1, com_add=1, dt=0.5, iib=0):

        old_add = self.slave_addr
        iib_offset = 14 * (iib - 1)

        try:
            for i in range(n):

                self.slave_addr = com_add

                print(
                    "\n--- Measurement #"
                    + str(i + 1)
                    + " ------------------------------------------\n"
                )

                self.read_vars_common()

                print(
                    "\nSync Pulse Counter: "
                    + str(round(self.read_bsmp_variable(5, "uint32_t"), 3))
                )

                soft_itlks = self.read_bsmp_variable(31, "uint32_t")
                print("\nSoft Interlocks: " + str(soft_itlks))
                if soft_itlks:
                    self.decode_interlocks(soft_itlks, list_fac_2s_dcdc_soft_interlocks)
                    print("")

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                print("Hard Interlocks: " + str(hard_itlks))
                if hard_itlks:
                    self.decode_interlocks(hard_itlks, list_fac_2s_dcdc_hard_interlocks)

                _load_current = round(self.read_bsmp_variable(33, "float"), 3)
                print("\nLoad Current: {} A".format(_load_current))

                _load_current_dcct1 = round(self.read_bsmp_variable(34, "float"), 3)
                print("Load Current DCCT 1: {} A".format(_load_current_dcct1))

                _load_current_dcct2 = round(self.read_bsmp_variable(35, "float"), 3)
                print("Load Current DCCT 2: {} A".format(_load_current_dcct2))

                print(
                    "\nCapBank Voltage 1: "
                    + str(round(self.read_bsmp_variable(36, "float"), 3))
                    + " V"
                )
                print(
                    "CapBank Voltage 2: "
                    + str(round(self.read_bsmp_variable(37, "float"), 3))
                    + " V"
                )

                print(
                    "\nDuty-Cycle 1: "
                    + str(round(self.read_bsmp_variable(38, "float"), 3))
                    + " %"
                )
                print(
                    "Duty-Cycle 2: "
                    + str(round(self.read_bsmp_variable(39, "float"), 3))
                    + " %"
                )

                if iib:
                    print(
                        "\nIIB CapBank Voltage: "
                        + str(
                            round(self.read_bsmp_variable(40 + iib_offset, "float"), 3)
                        )
                        + " V"
                    )
                    print(
                        "IIB Input Current: "
                        + str(
                            round(self.read_bsmp_variable(41 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB Output Current: "
                        + str(
                            round(self.read_bsmp_variable(42 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB IGBT Leg 1 Temp: "
                        + str(
                            round(self.read_bsmp_variable(43 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB IGBT Leg 2 Temp: "
                        + str(
                            round(self.read_bsmp_variable(44 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB Inductor Temp: "
                        + str(
                            round(self.read_bsmp_variable(45 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB Heat-Sink Temp: "
                        + str(
                            round(self.read_bsmp_variable(46 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB Driver Voltage: "
                        + str(
                            round(self.read_bsmp_variable(47 + iib_offset, "float"), 3)
                        )
                        + " V"
                    )
                    print(
                        "IIB Driver Current 1: "
                        + str(
                            round(self.read_bsmp_variable(48 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB Driver Current 2: "
                        + str(
                            round(self.read_bsmp_variable(49 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB Board Temp: "
                        + str(
                            round(self.read_bsmp_variable(50 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB Board RH: "
                        + str(
                            round(self.read_bsmp_variable(51 + iib_offset, "float"), 3)
                        )
                        + " %"
                    )

                    iib_itlks = self.read_bsmp_variable(52 + iib_offset, "uint32_t")
                    print("\nIIB Interlocks: " + str(iib_itlks))
                    if iib_itlks:
                        self.decode_interlocks(
                            iib_itlks, list_fac_2s_dcdc_iib_interlocks
                        )

                    iib_alarms = self.read_bsmp_variable(53 + iib_offset, "uint32_t")
                    print("IIB Alarms: " + str(iib_alarms))
                    if iib_alarms:
                        self.decode_interlocks(iib_alarms, list_fac_2s_dcdc_iib_alarms)

                time.sleep(dt)

            self.slave_addr = old_add
        except:
            self.slave_addr = old_add

    def read_vars_fac_2p4s_acdc(self, n=1, add_mod_a=1, dt=0.5, iib=0):
        self.read_vars_fac_2s_acdc(n, add_mod_a, dt, iib)

    def read_vars_fac_2p4s_dcdc(self, n=1, com_add=1, dt=0.5, iib=0):

        old_add = self.slave_addr

        try:
            for i in range(n):

                self.slave_addr = com_add

                print(
                    "\n--- Measurement #"
                    + str(i + 1)
                    + " ------------------------------------------\n"
                )

                self.read_vars_common()

                print(
                    "\nSync Pulse Counter: "
                    + str(round(self.read_bsmp_variable(5, "uint32_t"), 3))
                )

                soft_itlks = self.read_bsmp_variable(31, "uint32_t")
                print("\nSoft Interlocks: " + str(soft_itlks))
                if soft_itlks:
                    self.decode_interlocks(
                        soft_itlks, list_fac_2p4s_dcdc_soft_interlocks
                    )
                    print("")

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                print("Hard Interlocks: " + str(hard_itlks))
                if hard_itlks:
                    self.decode_interlocks(
                        hard_itlks, list_fac_2p4s_dcdc_hard_interlocks
                    )

                print(
                    "\nLoad Current: "
                    + str(round(self.read_bsmp_variable(33, "float"), 3))
                )
                print(
                    "Load Current DCCT 1: "
                    + str(round(self.read_bsmp_variable(34, "float"), 3))
                )
                print(
                    "Load Current DCCT 2: "
                    + str(round(self.read_bsmp_variable(35, "float"), 3))
                )

                print(
                    "\nArm Current 1: "
                    + str(round(self.read_bsmp_variable(36, "float"), 3))
                )
                print(
                    "Arm Current 2: "
                    + str(round(self.read_bsmp_variable(37, "float"), 3))
                )

                print(
                    "\nCapBank Voltage 1: "
                    + str(round(self.read_bsmp_variable(38, "float"), 3))
                )
                print(
                    "CapBank Voltage 2: "
                    + str(round(self.read_bsmp_variable(39, "float"), 3))
                )
                print(
                    "CapBank Voltage 3: "
                    + str(round(self.read_bsmp_variable(40, "float"), 3))
                )
                print(
                    "CapBank Voltage 4: "
                    + str(round(self.read_bsmp_variable(41, "float"), 3))
                )
                print(
                    "CapBank Voltage 5: "
                    + str(round(self.read_bsmp_variable(42, "float"), 3))
                )
                print(
                    "CapBank Voltage 6: "
                    + str(round(self.read_bsmp_variable(43, "float"), 3))
                )
                print(
                    "CapBank Voltage 7: "
                    + str(round(self.read_bsmp_variable(44, "float"), 3))
                )
                print(
                    "CapBank Voltage 8: "
                    + str(round(self.read_bsmp_variable(45, "float"), 3))
                )

                print(
                    "\nDuty-Cycle 1: "
                    + str(round(self.read_bsmp_variable(46, "float"), 3))
                )
                print(
                    "Duty-Cycle 2: "
                    + str(round(self.read_bsmp_variable(47, "float"), 3))
                )
                print(
                    "Duty-Cycle 3: "
                    + str(round(self.read_bsmp_variable(48, "float"), 3))
                )
                print(
                    "Duty-Cycle 4: "
                    + str(round(self.read_bsmp_variable(49, "float"), 3))
                )
                print(
                    "Duty-Cycle 5: "
                    + str(round(self.read_bsmp_variable(50, "float"), 3))
                )
                print(
                    "Duty-Cycle 6: "
                    + str(round(self.read_bsmp_variable(51, "float"), 3))
                )
                print(
                    "Duty-Cycle 7: "
                    + str(round(self.read_bsmp_variable(52, "float"), 3))
                )
                print(
                    "Duty-Cycle 8: "
                    + str(round(self.read_bsmp_variable(53, "float"), 3))
                )

                if iib:

                    print(
                        "\nIIB CapBank Voltage: "
                        + str(round(self.read_bsmp_variable(54, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Input Current: "
                        + str(round(self.read_bsmp_variable(55, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Output Current: "
                        + str(round(self.read_bsmp_variable(56, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB IGBT Leg 1 Temp: "
                        + str(round(self.read_bsmp_variable(57, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB IGBT Leg 2 Temp: "
                        + str(round(self.read_bsmp_variable(58, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Inductor Temp: "
                        + str(round(self.read_bsmp_variable(59, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Heat-Sink Temp: "
                        + str(round(self.read_bsmp_variable(60, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Driver Voltage: "
                        + str(round(self.read_bsmp_variable(61, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Driver Current 1: "
                        + str(round(self.read_bsmp_variable(62, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Driver Current 2: "
                        + str(round(self.read_bsmp_variable(63, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Board Temp: "
                        + str(round(self.read_bsmp_variable(64, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Board RH: "
                        + str(round(self.read_bsmp_variable(65, "float"), 3))
                        + " %"
                    )

                    iib_itlks = self.read_bsmp_variable(66, "uint32_t")
                    print("\nIIB Interlocks: " + str(iib_itlks))
                    if iib_itlks:
                        self.decode_interlocks(
                            iib_itlks, list_fac_2p4s_dcdc_iib_interlocks
                        )

                    iib_alarms = self.read_bsmp_variable(67, "uint32_t")
                    print("IIB Alarms: " + str(iib_alarms))
                    if iib_alarms:
                        self.decode_interlocks(
                            iib_alarms, list_fac_2p4s_dcdc_iib_alarms
                        )

                    print(
                        "\nIIB CapBank Voltage: "
                        + str(round(self.read_bsmp_variable(68, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Input Current: "
                        + str(round(self.read_bsmp_variable(69, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Output Current: "
                        + str(round(self.read_bsmp_variable(70, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB IGBT Leg 1 Temp: "
                        + str(round(self.read_bsmp_variable(71, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB IGBT Leg 2 Temp: "
                        + str(round(self.read_bsmp_variable(72, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Inductor Temp: "
                        + str(round(self.read_bsmp_variable(73, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Heat-Sink Temp: "
                        + str(round(self.read_bsmp_variable(74, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Driver Voltage: "
                        + str(round(self.read_bsmp_variable(75, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Driver Current 1: "
                        + str(round(self.read_bsmp_variable(76, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Driver Current 2: "
                        + str(round(self.read_bsmp_variable(77, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Board Temp: "
                        + str(round(self.read_bsmp_variable(78, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Board RH: "
                        + str(round(self.read_bsmp_variable(79, "float"), 3))
                        + " %"
                    )

                    iib_itlks = self.read_bsmp_variable(80, "uint32_t")
                    print("\nIIB Interlocks: " + str(iib_itlks))
                    if iib_itlks:
                        self.decode_interlocks(
                            iib_itlks, list_fac_2p4s_dcdc_iib_interlocks
                        )

                    iib_alarms = self.read_bsmp_variable(81, "uint32_t")
                    print("IIB Alarms: " + str(iib_alarms))
                    if iib_alarms:
                        self.decode_interlocks(
                            iib_alarms, list_fac_2p4s_dcdc_iib_alarms
                        )

                time.sleep(dt)

            self.slave_addr = old_add
        except:
            self.slave_addr = old_add

    def read_vars_fap(self, n=1, com_add=1, dt=0.5, iib=1):

        old_add = self.slave_addr

        try:
            for i in range(n):

                self.slave_addr = com_add

                print(
                    "\n--- Measurement #"
                    + str(i + 1)
                    + " ------------------------------------------\n"
                )
                self.read_vars_common()

                soft_itlks = self.read_bsmp_variable(31, "uint32_t")
                print("\nSoft Interlocks: " + str(soft_itlks))
                if soft_itlks:
                    self.decode_interlocks(soft_itlks, list_fap_soft_interlocks)
                    print("")

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                print("Hard Interlocks: " + str(hard_itlks))
                if hard_itlks:
                    self.decode_interlocks(hard_itlks, list_fap_hard_interlocks)

                iib_itlks = self.read_bsmp_variable(56, "uint32_t")
                print("\nIIB Interlocks: " + str(iib_itlks))
                if iib_itlks:
                    self.decode_interlocks(iib_itlks, list_fap_iib_interlocks)

                iib_alarms = self.read_bsmp_variable(57, "uint32_t")
                print("\nIIB Alarms: " + str(iib_alarms))
                if iib_alarms:
                    self.decode_interlocks(iib_alarms, list_fap_iib_alarms)

                iload = self.read_bsmp_variable(33, "float")

                print("\nLoad Current: " + str(round(iload, 3)) + " A")
                print(
                    "Load Current DCCT 1: "
                    + str(round(self.read_bsmp_variable(34, "float"), 3))
                    + " A"
                )
                print(
                    "Load Current DCCT 2: "
                    + str(round(self.read_bsmp_variable(35, "float"), 3))
                    + " A"
                )

                if not iload == 0:
                    print(
                        "\nLoad Resistance: "
                        + str(
                            abs(round(self.read_bsmp_variable(43, "float") / iload, 3))
                        )
                        + " Ohm"
                    )
                else:
                    print("\nLoad Resistance: 0 Ohm")
                print(
                    "Load Power: "
                    + str(
                        abs(
                            round(
                                self.read_bsmp_variable(43, "float")
                                * self.read_bsmp_variable(33, "float"),
                                3,
                            )
                        )
                    )
                    + " W"
                )

                print(
                    "\nDC-Link Voltage: "
                    + str(round(self.read_bsmp_variable(36, "float"), 3))
                    + " V"
                )
                print(
                    "\nIGBT 1 Current: "
                    + str(round(self.read_bsmp_variable(37, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 2 Current: "
                    + str(round(self.read_bsmp_variable(38, "float"), 3))
                    + " A"
                )
                print(
                    "\nIGBT 1 Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(39, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 2 Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(40, "float"), 3))
                    + " %"
                )
                print(
                    "Differential Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(41, "float"), 3))
                    + " %"
                )

                if iib:
                    print(
                        "\nIIB Input Voltage: "
                        + str(round(self.read_bsmp_variable(42, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Output Voltage: "
                        + str(round(self.read_bsmp_variable(43, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB IGBT 1 Current: "
                        + str(round(self.read_bsmp_variable(44, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB IGBT 2 Current: "
                        + str(round(self.read_bsmp_variable(45, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB IGBT 1 Temp: "
                        + str(round(self.read_bsmp_variable(46, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB IGBT 2 Temp: "
                        + str(round(self.read_bsmp_variable(47, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Driver Voltage: "
                        + str(round(self.read_bsmp_variable(48, "float"), 3))
                        + " V"
                    )
                    print(
                        "IIB Driver Current 1: "
                        + str(round(self.read_bsmp_variable(49, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Driver Current 2: "
                        + str(round(self.read_bsmp_variable(50, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Inductor Temp: "
                        + str(round(self.read_bsmp_variable(51, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Heat-Sink Temp: "
                        + str(round(self.read_bsmp_variable(52, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Ground Leakage Current: "
                        + str(round(self.read_bsmp_variable(53, "float"), 3))
                        + " A"
                    )
                    print(
                        "IIB Board Temp: "
                        + str(round(self.read_bsmp_variable(54, "float"), 3))
                        + " °C"
                    )
                    print(
                        "IIB Board RH: "
                        + str(round(self.read_bsmp_variable(55, "float"), 3))
                        + " %"
                    )
                    print(
                        "IIB Interlocks: "
                        + str(round(self.read_bsmp_variable(56, "uint32_t"), 3))
                    )
                    print(
                        "IIB Alarms: "
                        + str(round(self.read_bsmp_variable(57, "uint32_t"), 3))
                    )
                time.sleep(dt)

            self.slave_addr = old_add
        except:
            self.slave_addr = old_add

    def read_vars_fap_4p(self, n=1, com_add=1, dt=0.5, iib=0):

        old_add = self.slave_addr
        iib_offset = 16 * (iib - 1)

        try:
            for i in range(n):

                self.slave_addr = com_add

                print(
                    "\n--- Measurement #"
                    + str(i + 1)
                    + " ------------------------------------------\n"
                )
                self.read_vars_common()

                soft_itlks = self.read_bsmp_variable(31, "uint32_t")
                print("\nSoft Interlocks: " + str(soft_itlks))
                if soft_itlks:
                    self.decode_interlocks(soft_itlks, list_fap_4p_soft_interlocks)
                    print("")

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                print("Hard Interlocks: " + str(hard_itlks))
                if hard_itlks:
                    self.decode_interlocks(hard_itlks, list_fap_4p_hard_interlocks)

                for j in range(4):
                    iib_itlks = self.read_bsmp_variable(72 + j * 16, "uint32_t")
                    print("\nIIB " + str(j + 1) + " Interlocks: " + str(iib_itlks))
                    if iib_itlks:
                        self.decode_interlocks(iib_itlks, list_fap_4p_iib_interlocks)

                    iib_alarms = self.read_bsmp_variable(73 + j * 16, "uint32_t")
                    print("IIB " + str(j + 1) + " Alarms: " + str(iib_alarms))
                    if iib_alarms:
                        self.decode_interlocks(iib_alarms, list_fap_4p_iib_alarms)

                print(
                    "\n Mean Load Current: "
                    + str(round(self.read_bsmp_variable(33, "float"), 3))
                    + " A"
                )
                print(
                    "Load Current 1: "
                    + str(round(self.read_bsmp_variable(34, "float"), 3))
                    + " A"
                )
                print(
                    "Load Current 2: "
                    + str(round(self.read_bsmp_variable(35, "float"), 3))
                    + " A"
                )

                print(
                    "Load Voltage: "
                    + str(round(self.read_bsmp_variable(36, "float"), 3))
                    + " V"
                )

                print(
                    "\nIGBT 1 Current Mod 1: "
                    + str(round(self.read_bsmp_variable(37, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 2 Current Mod 1: "
                    + str(round(self.read_bsmp_variable(38, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 1 Current Mod 2: "
                    + str(round(self.read_bsmp_variable(39, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 2 Current Mod 2: "
                    + str(round(self.read_bsmp_variable(40, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 1 Current Mod 3: "
                    + str(round(self.read_bsmp_variable(41, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 2 Current Mod 3: "
                    + str(round(self.read_bsmp_variable(42, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 1 Current Mod 4: "
                    + str(round(self.read_bsmp_variable(43, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 2 Current Mod 4: "
                    + str(round(self.read_bsmp_variable(44, "float"), 3))
                    + " A"
                )

                print(
                    "\nDC-Link Voltage Mod 1: "
                    + str(round(self.read_bsmp_variable(45, "float"), 3))
                    + " V"
                )
                print(
                    "DC-Link Voltage Mod 2: "
                    + str(round(self.read_bsmp_variable(46, "float"), 3))
                    + " V"
                )
                print(
                    "DC-Link Voltage Mod 3: "
                    + str(round(self.read_bsmp_variable(47, "float"), 3))
                    + " V"
                )
                print(
                    "DC-Link Voltage Mod 4: "
                    + str(round(self.read_bsmp_variable(48, "float"), 3))
                    + " V"
                )

                print(
                    "\nMean Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(49, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 1 Duty-Cycle Mod 1: "
                    + str(round(self.read_bsmp_variable(50, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 2 Duty-Cycle Mod 1: "
                    + str(round(self.read_bsmp_variable(51, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 1 Duty-Cycle Mod 2: "
                    + str(round(self.read_bsmp_variable(52, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 2 Duty-Cycle Mod 2: "
                    + str(round(self.read_bsmp_variable(53, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 1 Duty-Cycle Mod 3: "
                    + str(round(self.read_bsmp_variable(54, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 2 Duty-Cycle Mod 3: "
                    + str(round(self.read_bsmp_variable(55, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 1 Duty-Cycle Mod 4: "
                    + str(round(self.read_bsmp_variable(56, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 2 Duty-Cycle Mod 4: "
                    + str(round(self.read_bsmp_variable(57, "float"), 3))
                    + " %"
                )

                if not iib == 0:
                    print(
                        "\nIIB "
                        + str(iib)
                        + " Input Voltage: "
                        + str(
                            round(self.read_bsmp_variable(58 + iib_offset, "float"), 3)
                        )
                        + " V"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Output Voltage: "
                        + str(
                            round(self.read_bsmp_variable(59 + iib_offset, "float"), 3)
                        )
                        + " V"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " IGBT 1 Current: "
                        + str(
                            round(self.read_bsmp_variable(60 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " IGBT 2 Current: "
                        + str(
                            round(self.read_bsmp_variable(61 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " IGBT 1 Temp: "
                        + str(
                            round(self.read_bsmp_variable(62 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " IGBT 2 Temp: "
                        + str(
                            round(self.read_bsmp_variable(63 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Driver Voltage: "
                        + str(
                            round(self.read_bsmp_variable(64 + iib_offset, "float"), 3)
                        )
                        + " V"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Driver Current 1: "
                        + str(
                            round(self.read_bsmp_variable(65 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Driver Current 2: "
                        + str(
                            round(self.read_bsmp_variable(66 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Inductor Temp: "
                        + str(
                            round(self.read_bsmp_variable(67 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Heat-Sink Temp: "
                        + str(
                            round(self.read_bsmp_variable(68 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Ground Leakage Current: "
                        + str(
                            round(self.read_bsmp_variable(69 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Board Temp: "
                        + str(
                            round(self.read_bsmp_variable(70 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Board RH: "
                        + str(
                            round(self.read_bsmp_variable(71 + iib_offset, "float"), 3)
                        )
                        + " %"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Interlocks: "
                        + str(
                            round(
                                self.read_bsmp_variable(72 + iib_offset, "uint32_t"), 3
                            )
                        )
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Alarms: "
                        + str(
                            round(
                                self.read_bsmp_variable(73 + iib_offset, "uint32_t"), 3
                            )
                        )
                    )

                time.sleep(dt)

            self.slave_addr = old_add

        except Exception as e:
            self.slave_addr = old_add

    def read_vars_fap_2p2s(self, n=1, com_add=1, dt=0.5, iib=0):

        old_add = self.slave_addr
        iib_offset = 16 * (iib - 1)

        try:
            for i in range(n):

                self.slave_addr = com_add

                print(
                    "\n--- Measurement #"
                    + str(i + 1)
                    + " ------------------------------------------\n"
                )
                self.read_vars_common()

                soft_itlks = self.read_bsmp_variable(31, "uint32_t")
                print("\nSoft Interlocks: " + str(soft_itlks))
                if soft_itlks:
                    self.decode_interlocks(soft_itlks, list_fap_2p2s_soft_interlocks)
                    print("")

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                print("Hard Interlocks: " + str(hard_itlks))
                if hard_itlks:
                    self.decode_interlocks(hard_itlks, list_fap_2p2s_hard_interlocks)

                for j in range(4):
                    iib_itlks = self.read_bsmp_variable(78 + j * 16, "uint32_t")
                    print("\nIIB " + str(j + 1) + " Interlocks: " + str(iib_itlks))
                    if iib_itlks:
                        self.decode_interlocks(iib_itlks, list_fap_4p_iib_interlocks)

                    iib_alarms = self.read_bsmp_variable(79 + j * 16, "uint32_t")
                    print("IIB " + str(j + 1) + " Alarms: " + str(iib_alarms))
                    if iib_alarms:
                        self.decode_interlocks(iib_alarms, list_fap_4p_iib_alarms)

                print(
                    "\nMean Load Current: "
                    + str(round(self.read_bsmp_variable(33, "float"), 3))
                    + " A"
                )
                print(
                    "Load Current 1: "
                    + str(round(self.read_bsmp_variable(34, "float"), 3))
                    + " A"
                )
                print(
                    "Load Current 2: "
                    + str(round(self.read_bsmp_variable(35, "float"), 3))
                    + " A"
                )

                print(
                    "\nArm Current 1: "
                    + str(round(self.read_bsmp_variable(36, "float"), 3))
                    + " A"
                )
                print(
                    "Arm Current 2: "
                    + str(round(self.read_bsmp_variable(37, "float"), 3))
                    + " A"
                )

                print(
                    "\nIGBT 1 Current Mod 1: "
                    + str(round(self.read_bsmp_variable(38, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 2 Current Mod 1: "
                    + str(round(self.read_bsmp_variable(39, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 1 Current Mod 2: "
                    + str(round(self.read_bsmp_variable(40, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 2 Current Mod 2: "
                    + str(round(self.read_bsmp_variable(41, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 1 Current Mod 3: "
                    + str(round(self.read_bsmp_variable(42, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 2 Current Mod 3: "
                    + str(round(self.read_bsmp_variable(43, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 1 Current Mod 4: "
                    + str(round(self.read_bsmp_variable(44, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 2 Current Mod 4: "
                    + str(round(self.read_bsmp_variable(45, "float"), 3))
                    + " A"
                )

                print(
                    "\nDC-Link Voltage Mod 1: "
                    + str(round(self.read_bsmp_variable(50, "float"), 3))
                    + " V"
                )
                print(
                    "DC-Link Voltage Mod 2: "
                    + str(round(self.read_bsmp_variable(51, "float"), 3))
                    + " V"
                )
                print(
                    "DC-Link Voltage Mod 3: "
                    + str(round(self.read_bsmp_variable(52, "float"), 3))
                    + " V"
                )
                print(
                    "DC-Link Voltage Mod 4: "
                    + str(round(self.read_bsmp_variable(53, "float"), 3))
                    + " V"
                )

                print(
                    "\nMean Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(54, "float"), 3))
                    + " %"
                )
                print(
                    "Differential Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(55, "float"), 3))
                    + " %"
                )
                print(
                    "\nIGBT 1 Duty-Cycle Mod 1: "
                    + str(round(self.read_bsmp_variable(56, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 2 Duty-Cycle Mod 1: "
                    + str(round(self.read_bsmp_variable(57, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 1 Duty-Cycle Mod 2: "
                    + str(round(self.read_bsmp_variable(58, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 2 Duty-Cycle Mod 2: "
                    + str(round(self.read_bsmp_variable(59, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 1 Duty-Cycle Mod 3: "
                    + str(round(self.read_bsmp_variable(60, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 2 Duty-Cycle Mod 3: "
                    + str(round(self.read_bsmp_variable(61, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 1 Duty-Cycle Mod 4: "
                    + str(round(self.read_bsmp_variable(62, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 2 Duty-Cycle Mod 4: "
                    + str(round(self.read_bsmp_variable(63, "float"), 3))
                    + " %"
                )

                if not iib == 0:
                    print(
                        "\nIIB "
                        + str(iib)
                        + " Input Voltage: "
                        + str(
                            round(self.read_bsmp_variable(64 + iib_offset, "float"), 3)
                        )
                        + " V"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Output Voltage: "
                        + str(
                            round(self.read_bsmp_variable(65 + iib_offset, "float"), 3)
                        )
                        + " V"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " IGBT 1 Current: "
                        + str(
                            round(self.read_bsmp_variable(66 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " IGBT 2 Current: "
                        + str(
                            round(self.read_bsmp_variable(67 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " IGBT 1 Temp: "
                        + str(
                            round(self.read_bsmp_variable(68 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " IGBT 2 Temp: "
                        + str(
                            round(self.read_bsmp_variable(69 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Driver Voltage: "
                        + str(
                            round(self.read_bsmp_variable(70 + iib_offset, "float"), 3)
                        )
                        + " V"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Driver Current 1: "
                        + str(
                            round(self.read_bsmp_variable(71 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Driver Current 2: "
                        + str(
                            round(self.read_bsmp_variable(72 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Inductor Temp: "
                        + str(
                            round(self.read_bsmp_variable(73 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Heat-Sink Temp: "
                        + str(
                            round(self.read_bsmp_variable(74 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Ground Leakage Current: "
                        + str(
                            round(self.read_bsmp_variable(75 + iib_offset, "float"), 3)
                        )
                        + " A"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Board Temp: "
                        + str(
                            round(self.read_bsmp_variable(76 + iib_offset, "float"), 3)
                        )
                        + " °C"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Board RH: "
                        + str(
                            round(self.read_bsmp_variable(77 + iib_offset, "float"), 3)
                        )
                        + " %"
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Interlocks: "
                        + str(
                            round(
                                self.read_bsmp_variable(78 + iib_offset, "uint32_t"), 3
                            )
                        )
                    )
                    print(
                        "IIB "
                        + str(iib)
                        + " Alarms: "
                        + str(
                            round(
                                self.read_bsmp_variable(79 + iib_offset, "uint32_t"), 3
                            )
                        )
                    )

                time.sleep(dt)

            self.slave_addr = old_add

        except Exception as e:
            self.slave_addr = old_add

    def read_vars_fap_225A(self, n=1, com_add=1, dt=0.5):

        old_add = self.slave_addr

        try:
            for i in range(n):

                self.slave_addr = com_add

                print(
                    "\n--- Measurement #"
                    + str(i + 1)
                    + " ------------------------------------------\n"
                )
                self.read_vars_common()

                soft_itlks = self.read_bsmp_variable(31, "uint32_t")
                print("\nSoft Interlocks: " + str(soft_itlks))
                if soft_itlks:
                    self.decode_interlocks(soft_itlks, list_fap_225A_soft_interlocks)
                    print("")

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                print("Hard Interlocks: " + str(hard_itlks))
                if hard_itlks:
                    self.decode_interlocks(hard_itlks, list_fap_225A_hard_interlocks)

                print(
                    "\nLoad Current: "
                    + str(round(self.read_bsmp_variable(33, "float"), 3))
                    + " A"
                )
                print(
                    "\nIGBT 1 Current: "
                    + str(round(self.read_bsmp_variable(34, "float"), 3))
                    + " A"
                )
                print(
                    "IGBT 2 Current: "
                    + str(round(self.read_bsmp_variable(35, "float"), 3))
                    + " A"
                )
                print(
                    "\nIGBT 1 Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(36, "float"), 3))
                    + " %"
                )
                print(
                    "IGBT 2 Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(37, "float"), 3))
                    + " %"
                )
                print(
                    "Differential Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(38, "float"), 3))
                    + " %"
                )

                time.sleep(dt)

            self.slave_addr = old_add
        except:
            self.slave_addr = old_add

    def read_vars_fac_2p_acdc_imas(self, n=1, add_mod_a=2, dt=0.5, iib=0):

        old_add = self.slave_addr

        try:
            for i in range(n):

                self.slave_addr = add_mod_a

                print(
                    "\n--- Measurement #"
                    + str(i + 1)
                    + " ------------------------------------------\n"
                )
                self.read_vars_common()

                print("\n *** MODULE A ***")

                soft_itlks = self.read_bsmp_variable(31, "uint32_t")
                print("\nSoft Interlocks: " + str(soft_itlks))
                if soft_itlks:
                    self.decode_interlocks(
                        soft_itlks, list_fac_2p_acdc_imas_soft_interlocks
                    )
                    print("")

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                print("Hard Interlocks: " + str(hard_itlks))
                if hard_itlks:
                    self.decode_interlocks(
                        hard_itlks, list_fac_2p_acdc_imas_hard_interlocks
                    )

                print(
                    "\nCapBank Voltage: "
                    + str(round(self.read_bsmp_variable(33, "float"), 3))
                    + " V"
                )
                print(
                    "Rectifier Current: "
                    + str(round(self.read_bsmp_variable(34, "float"), 3))
                    + " A"
                )
                print(
                    "Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(35, "float"), 3))
                    + " %"
                )

                self.slave_addr = add_mod_a + 1

                print("\n *** MODULE B ***")

                soft_itlks = self.read_bsmp_variable(31, "uint32_t")
                print("\nSoft Interlocks: " + str(soft_itlks))
                if soft_itlks:
                    self.decode_interlocks(
                        soft_itlks, list_fac_2p_acdc_imas_soft_interlocks
                    )
                    print("")

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                print("Hard Interlocks: " + str(hard_itlks))
                if hard_itlks:
                    self.decode_interlocks(
                        hard_itlks, list_fac_2p_acdc_imas_hard_interlocks
                    )

                print(
                    "\nCapBank Voltage: "
                    + str(round(self.read_bsmp_variable(33, "float"), 3))
                    + " V"
                )
                print(
                    "Rectifier Current: "
                    + str(round(self.read_bsmp_variable(34, "float"), 3))
                    + " A"
                )
                print(
                    "Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(35, "float"), 3))
                    + " %"
                )

                time.sleep(dt)

            self.slave_addr = old_add
        except:
            self.slave_addr = old_add
            # TODO: Raise proper exception

    def read_vars_fac_2p_dcdc_imas(self, n=1, com_add=1, dt=0.5, iib=0):

        old_add = self.slave_addr

        try:
            for i in range(n):

                self.slave_addr = com_add

                print(
                    "\n--- Measurement #"
                    + str(i + 1)
                    + " ------------------------------------------\n"
                )

                self.read_vars_common()

                print(
                    "\nSync Pulse Counter: "
                    + str(round(self.read_bsmp_variable(5, "uint32_t"), 3))
                )

                soft_itlks = self.read_bsmp_variable(31, "uint32_t")
                print("\nSoft Interlocks: " + str(soft_itlks))
                if soft_itlks:
                    self.decode_interlocks(
                        soft_itlks, list_fac_2p_dcdc_imas_soft_interlocks
                    )
                    print("")

                hard_itlks = self.read_bsmp_variable(32, "uint32_t")
                print("Hard Interlocks: " + str(hard_itlks))
                if hard_itlks:
                    self.decode_interlocks(
                        hard_itlks, list_fac_2p_dcdc_imas_hard_interlocks
                    )

                print(
                    "\nLoad Current: "
                    + str(round(self.read_bsmp_variable(33, "float"), 3))
                    + " A"
                )
                print(
                    "Load Current Error: "
                    + str(round(self.read_bsmp_variable(34, "float"), 3))
                    + " A"
                )

                print(
                    "\nArm 1 Current: "
                    + str(round(self.read_bsmp_variable(35, "float"), 3))
                    + " A"
                )
                print(
                    "Arm 2 Current: "
                    + str(round(self.read_bsmp_variable(36, "float"), 3))
                    + " A"
                )
                print(
                    "Arms Current Diff: "
                    + str(round(self.read_bsmp_variable(37, "float"), 3))
                    + " A"
                )

                print(
                    "\nCapBank Voltage 1: "
                    + str(round(self.read_bsmp_variable(38, "float"), 3))
                    + " V"
                )
                print(
                    "CapBank Voltage 2: "
                    + str(round(self.read_bsmp_variable(39, "float"), 3))
                    + " V"
                )

                print(
                    "\nDuty-Cycle 1: "
                    + str(round(self.read_bsmp_variable(40, "float"), 3))
                    + " %"
                )
                print(
                    "Duty-Cycle 2: "
                    + str(round(self.read_bsmp_variable(41, "float"), 3))
                    + " %"
                )
                print(
                    "Differential Duty-Cycle: "
                    + str(round(self.read_bsmp_variable(42, "float"), 3))
                    + " %"
                )

                time.sleep(dt)

            self.slave_addr = old_add
        except:
            self.slave_addr = old_add
            raise  # TODO: Raise proper exception

    def check_param_bank(self, param_file):
        fbp_param_list = []

        # max_sampling_freq = 600000
        # c28_sysclk = 150e6

        with open(param_file, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                fbp_param_list.append(row)

        for param in fbp_param_list:
            if str(param[0]) == "Num_PS_Modules" and param[1] > 4:
                print(
                    "Invalid " + str(param[0]) + ": " + str(param[1]) + ". Maximum is 4"
                )

            elif str(param[0]) == "Freq_ISR_Controller" and param[1] > 6000000:
                print(
                    "Invalid " + str(param[0]) + ": " + str(param[1]) + ". Maximum is 4"
                )

            else:
                for n in range(64):
                    try:
                        print(str(param[0]) + "[" + str(n) + "]: " + str(param[n + 1]))
                        print(self.set_param(str(param[0]), n, float(param[n + 1])))
                    except:
                        break

    def get_default_ramp_waveform(
        self, interval=500, nrpts=4000, ti=None, fi=None, forms=None
    ):
        from siriuspy.magnet.util import get_default_ramp_waveform

        return get_default_ramp_waveform(interval, nrpts, ti, fi, forms)

    def save_ramp_waveform(self, ramp):
        filename = input("Digite o nome do arquivo: ")
        with open(filename + ".csv", "w", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(ramp)

    def save_ramp_waveform_col(self, ramp):
        filename = input("Digite o nome do arquivo: ")
        with open(filename + ".csv", "w", newline="") as f:
            writer = csv.writer(f)
            for val in ramp:
                writer.writerow([val])

    def read_vars_fac_n(self, n=1, dt=0.5):
        old_add = self.slave_addr
        try:
            for i in range(n):
                print(
                    "\n--- Measurement #"
                    + str(i + 1)
                    + " ------------------------------------------\n"
                )
                self.slave_addr = 1
                self.read_vars_fac_dcdc()
                print("\n-----------------------\n")
                self.slave_addr = 2
                self.read_vars_fac_acdc()
                time.sleep(dt)
            self.slave_addr = old_add
        except:
            self.slave_addr = old_add

    def set_buf_samples_freq(self, fs):
        self.set_param("Freq_TimeSlicer", 1, fs)
        self.save_param_eeprom("Freq_TimeSlicer", 1)
        self.reset_udc()

    def calc_pi(self, r_load, l_load, f_bw, v_dclink, send_drs=0, dsp_id=0):
        kp = 2 * 3.1415 * f_bw * l_load / v_dclink
        ki = kp * r_load / l_load
        print("\n  Kp = " + str(kp))
        print("  Ki = " + str(ki) + "\n")
        if send_drs:
            self.set_dsp_coeffs(3, dsp_id, [kp, ki, 0.95, -0.95])
        return [kp, ki]

    def config_dsp_modules_drs_fap_tests(self):
        kp_load = 0
        ki_load = 20.95
        kp_share = 0.000032117
        ki_share = 0.0012

        self.set_dsp_coeffs(3, 0, [kp_load, ki_load, 0.6, 0])
        self.set_dsp_coeffs(3, 1, [kp_share, ki_share, 0.0015, -0.0015])
        self.save_dsp_modules_eeprom()

    def set_prbs_sampling_freq(self, freq, type_memory):
        self.set_param("Freq_TimeSlicer", 0, freq)
        self.set_param("Freq_TimeSlicer", 1, freq)
        self.save_param_bank(type_memory)

    def get_dsp_modules_bank(
        self, list_dsp_classes=[1, 2, 3, 4, 5, 6], print_modules=1
    ):
        dsp_modules_bank = []
        for dsp_class in list_dsp_classes:
            for dsp_id in range(num_dsp_modules[dsp_class]):
                dsp_module = [dsp_classes_names[dsp_class], dsp_class, dsp_id]
                for dsp_coeff in range(num_coeffs_dsp_modules[dsp_class]):
                    try:
                        coeff = self.get_dsp_coeff(dsp_class, dsp_id, dsp_coeff)
                        if dsp_class == 3 and dsp_coeff == 1:
                            coeff *= self.get_param("Freq_ISR_Controller", 0)
                            dsp_module.append(coeff)
                    except SerialInvalidCmd:
                        dsp_module.append("nan")
                dsp_modules_bank.append(dsp_module)
                if print_modules:
                    print(dsp_module)

        return dsp_modules_bank

    def store_dsp_modules_bank_csv(self, bank):
        filename = input("Digite o nome do arquivo: ")
        with open(filename + ".csv", "w", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            for dsp_module in bank:
                writer.writerow(dsp_module)

    def set_dsp_modules_bank(self, dsp_modules_file, save_eeprom=0):
        # dsp_modules_row = []
        with open(dsp_modules_file, newline="") as f:
            reader = csv.reader(f)

            for dsp_module in reader:
                if not dsp_module == []:
                    if not dsp_module[0][0] == "#":
                        list_coeffs = []

                        for coeff in dsp_module[
                            3 : 3 + num_coeffs_dsp_modules[int(dsp_module[1])]
                        ]:
                            list_coeffs.append(float(coeff))

                        print(
                            str(int(dsp_module[1]))
                            + " "
                            + str(int(dsp_module[2]))
                            + " "
                            + str(list_coeffs)
                        )
                        self.set_dsp_coeffs(
                            int(dsp_module[1]), int(dsp_module[2]), list_coeffs
                        )

        if save_eeprom:
            self.save_dsp_modules_eeprom()
        else:
            print(
                "\n *** Aviso: Os coeficientes configurados não foram salvos na memória EEPROM. Caso deseje salvar, utilize o argumento save_eeprom = 1"
            )

    def select_param_bank(self, cfg_dsp_modules=0):  # noqa: C901

        add = int(
            input(
                "\n Digite o endereco serial atual do controlador a ser configurado: "
            )
        )

        old_add = self.slave_addr
        self.slave_addr = add

        # areas = ["IA", "LA", "PA"]

        ps_models = ["fbp", "fbp_dclink", "fap", "fap_4p", "fap_2p4s", "fac", "fac_2s"]

        # ps_folders = [
        #   "fbp",
        #   "fbp_dclink",
        #   "fap",
        #   "fap",
        # ]

        # la_fap = [
        #   "TB-Fam:PS-B",
        #   "TS-01:PS-QF1A",
        #   "TS-01:PS-QF1B",
        #   "TS-02:PS-QD2",
        #   "TS-02:PS-QF2",
        #   "TS-03:PS-QF3",
        #   "TS-04:PS-QD4A",
        #   "TS-04:PS-QD4B",
        #   "TS-04:PS-QF4",
        # ]

        print("\n Selecione area: \n")
        print("   0: Sala de racks")
        print("   1: Linhas de transporte")
        print("   2: Sala de fontes\n")
        area = int(input(" Digite o numero correspondente: "))

        if area == 0:
            sector = input("\n Digite o setor da sala de racks [1 a 20]: ")

            if int(sector) < 10:
                sector = "0" + sector

            rack = input("\n Escolha o rack em que a fonte se encontra [1/2/3]: ")

            # if (rack != '1') and (rack != '2'):
            if not ((rack == "1") or (rack == "2") or (sector == "09" and rack == "3")):
                print(" \n *** RACK INEXISTENTE ***\n")
                return

            print("\n Escolha o tipo de fonte: \n")
            print("   0: FBP")
            print("   1: FBP-DCLink\n")
            ps_model = int(input(" Digite o numero correspondente: "))

            if ps_model == 0:
                crate = "_crate_" + input(
                    "\n Digite a posicao do bastidor, de cima para baixo. Leve em conta os bastidores que ainda nao foram instalados : "
                )

            elif ps_model == 1:
                crate = ""

            else:
                print(" \n *** TIPO DE FONTE INEXISTENTE ***\n")
                return

            file_dir = "../ps_parameters/IA-" + sector + "/" + ps_models[ps_model] + "/"

            file_name = (
                "parameters_"
                + ps_models[ps_model]
                + "_IA-"
                + sector
                + "RaPS0"
                + rack
                + crate
                + ".csv"
            )

            file_path = file_dir + file_name

            print("\n Banco de parametros a ser utilizado: " + file_path)

        elif area == 1:

            print("\n Escolha o tipo de fonte: \n")
            print("   0: FBP")
            print("   1: FBP-DCLink")
            print("   2: FAP\n")

            ps_model = int(input(" Digite o numero correspondente: "))

            if ps_model == 0 or ps_model == 1:

                crate = input(
                    "\n Digite a posicao do bastidor, de cima para baixo. Leve em conta os bastidores que ainda nao foram instalados : "
                )
                ps_name = "_LA-RaPS06_crate_" + crate

                file_dir = "../ps_parameters/LA/" + ps_models[ps_model] + "/"
                file_name = "parameters_" + ps_models[ps_model] + ps_name + ".csv"
                file_path = file_dir + file_name

            elif ps_model == 2:

                ps_list = []

                file_dir = "../ps_parameters/LA/fap/"
                for entry in os.listdir(file_dir):
                    if os.path.isfile(os.path.join(file_dir, entry)):
                        ps_list.append(entry)

                print("\n ### Lista de fontes FAP da linha de transporte ### \n")

                for idx, ps in enumerate(ps_list):
                    print("   " + str(idx) + ": " + ps)

                ps_idx = int(input("\n Escolha o índice da fonte correspondente: "))

                file_path = file_dir + ps_list[ps_idx]

            else:
                print(" \n *** TIPO DE FONTE INEXISTENTE ***\n")
                return

            print("\n Banco de parametros a ser utilizado: " + file_path)

        elif area == 2:
            print("\n Escolha o tipo de fonte: \n")
            print("   0: FAC")
            print("   1: FAP\n")

            ps_model = int(input(" Digite o numero correspondente: "))

            if ps_model == 0:

                ps_list = []

                file_dir = "../ps_parameters/PA/fac/"
                for entry in os.listdir(file_dir):
                    if os.path.isfile(os.path.join(file_dir, entry)):
                        ps_list.append(entry)

                print(
                    "\n ### Lista de bastidores de controle FAC da sala de fontes ### \n"
                )

                for idx, ps in enumerate(ps_list):
                    print(" ", idx, ": ", ps)

                ps_idx = int(input("\n Escolha o índice da fonte correspondente: "))

                file_path = file_dir + ps_list[ps_idx]

            elif ps_model == 1:

                ps_list = []

                file_dir = "../ps_parameters/PA/fap/"
                for entry in os.listdir(file_dir):
                    if os.path.isfile(os.path.join(file_dir, entry)):
                        ps_list.append(entry)

                print(
                    "\n ### Lista de bastidores de controle FAP da sala de fontes ### \n"
                )

                for idx, ps in enumerate(ps_list):
                    print(" ", idx, ": ", ps)

                ps_idx = int(input("\n Escolha o índice da fonte correspondente: "))

                file_path = file_dir + ps_list[ps_idx]

            else:
                print(" \n *** TIPO DE FONTE INEXISTENTE ***\n")
                return

            print("\n Banco de parametros a ser utilizado: " + file_path)

        else:
            print(" \n *** SALA INEXISTENTE ***\n")
            return

        r = input("\n Tem certeza que deseja prosseguir? [Y/N]: ")

        if (r != "Y") and (r != "y"):
            print(" \n *** OPERAÇÃO CANCELADA ***\n")
            return
        self.slave_addr = add

        if ps_model == 0 and cfg_dsp_modules == 1:
            print("\n Enviando parametros de controle para controlador ...")

            dsp_file_dir = (
                "../dsp_parameters/IA-" + sector + "/" + ps_models[ps_model] + "/"
            )

            dsp_file_name = (
                "dsp_parameters_"
                + ps_models[ps_model]
                + "_IA-"
                + sector
                + "RaPS0"
                + rack
                + crate
                + ".csv"
            )

            dsp_file_path = dsp_file_dir + dsp_file_name

            self.set_dsp_modules_bank(dsp_file_path)

            print("\n Gravando parametros de controle na memoria ...")
            time.sleep(1)
            self.save_dsp_modules_eeprom()

        print("\n Enviando parametros de operacao para controlador ...\n")
        time.sleep(1)
        self.set_param_bank(file_path)
        print("\n Gravando parametros de operacao na memoria EEPROM onboard ...")
        self.save_param_bank(2)
        time.sleep(5)

        print("\n Resetando UDC ...")
        self.reset_udc()
        time.sleep(2)

        print(
            "\n Pronto! Não se esqueça de utilizar o novo endereço serial para se comunicar com esta fonte! :)\n"
        )

        self.slave_addr = old_add

    def get_siggen_vars(self) -> dict:
        reply_msg = self.read_var(index_to_hex(13), 21)
        val = struct.unpack("BBHffffB", reply_msg)

        return {
            "enable": self.read_bsmp_variable(6, "uint16_t"),
            "type": list_sig_gen_types[int(self.read_bsmp_variable(7, "uint16_t"))],
            "num_cycles": self.read_bsmp_variable(8, "uint16_t"),
            "index": self.read_bsmp_variable(9, "float"),
            "frequency": self.read_bsmp_variable(10, "float"),
            "amplitude": self.read_bsmp_variable(11, "float"),
            "offset": self.read_bsmp_variable(12, "float"),
            "aux_params": val[3:7],
        }

    def firmware_initialization(self):
        print("\n ### Inicialização de firmware ### \n")

        print("\n Lendo status...")
        print(self.read_ps_status())

        print("\n Lendo versão de firmware...")
        self.read_udc_version()

        print("\n Desbloqueando UDC...")
        print(self.unlock_udc(0xFFFF))

        print("\n Habilitando EEPROM onboard...")
        self.enable_onboard_eeprom()

        print("\n Alterando senha...")
        print(self.set_param("Password", 0, 0xCAFE))
        print(self.save_param_eeprom("Password", 0, 2))

        print("\n Configurando banco de parâmetros...")
        self.select_param_bank()

        print("\n ### Fim da inicialização de firmware ### \n")

    def cfg_hensys_ps_model(self):

        list_files = [
            "fbp_dclink/parameters_fbp_dclink_hensys.csv",
            "fac/parameters_fac_acdc_hensys.csv",
            "fac/parameters_fac_dcdc_hensys.csv",
            "fac/parameters_fac_2s_acdc_hensys.csv",
            "fac/parameters_fac_2s_dcdc_hensys.csv",
            "fac/parameters_fac_2p4s_acdc_hensys.csv",
            "fac/parameters_fac_2p4s_dcdc_hensys.csv",
            "fap/parameters_fap_hensys.csv",
            "fap/parameters_fap_2p2s_hensys.csv",
            "fap/parameters_fap_4p_hensys.csv",
        ]

        print("\n Desbloqueando UDC ...")
        print(self.unlock_udc(0xCAFE))

        print("\n *** Escolha o modelo de fonte a ser configurado ***\n")
        print(" 0: FBP-DClink")
        print(" 1: FAC-ACDC")
        print(" 2: FAC-DCDC")
        print(" 3: FAC-2S-ACDC")
        print(" 4: FAC-2S-DCDC")
        print(" 5: FAC-2P4S-ACDC")
        print(" 6: FAC-2P4S-DCDC")
        print(" 7: FAP")
        print(" 8: FAP-2P2S")
        print(" 9: FAP-4P")

        model_idx = int(input("\n Digite o índice correspondente: "))
        file_path = "../ps_parameters/development/" + list_files[model_idx]

        print("\n Banco de parametros a ser utilizado: " + file_path)

        r = input("\n Tem certeza que deseja prosseguir? [Y/N]: ")

        if (r != "Y") and (r != "y"):
            print(" \n *** OPERAÇÃO CANCELADA ***\n")
            return

        print("\n Enviando parametros de operacao para controlador ...\n")
        time.sleep(1)
        self.set_param_bank(file_path)

        print("\n Gravando parametros de operacao na memoria EEPROM onboard ...")
        self.save_param_bank(2)
        time.sleep(5)

        print("\n Resetando UDC ...")
        self.reset_udc()
        time.sleep(2)

        print(
            "\n Pronto! Nao se esqueca de utilizar o novo endereco serial para se comunicar com esta fonte! :)\n"
        )

    def test_bid_board(self, password):

        input(
            "\n Antes de iniciar, certifique-se que o bastidor foi energizado sem a placa BID.\n Para prosseguir, conecte a placa BID a ser testada e pressione qualquer tecla... "
        )

        print("\n Desbloqueando UDC ...")
        print(self.unlock_udc(password))

        print("\n Carregando banco de parametros da memoria onboard ...")
        print(self.load_param_bank(type_memory=2))

        print("\n Banco de parametros da memoria onboard:\n")

        max_param = list_parameters.index("Scope_Source")
        param_bank_onboard = []

        for param in list_parameters[0:max_param]:
            val = self.get_param(param, 0)
            print(param + ":", val)
            param_bank_onboard.append(val)

        print("\n Salvando banco de parametros na memoria offboard ...")
        print(self.save_param_bank(type_memory=1))

        time.sleep(5)

        print("\n Resetando UDC ...")
        self.reset_udc()

        time.sleep(3)

        self.read_ps_status()

        print("\n Desbloqueando UDC ...")
        print(self.unlock_udc(password))

        print("\n Carregando banco de parametros da memoria offboard ...")
        print(self.load_param_bank(type_memory=1))

        self.read_ps_status()

        print("\n Verificando banco de parametros offboard apos reset ... \n")
        try:
            param_bank_offboard = []

            for param in list_parameters[0:max_param]:
                val = self.get_param(param, 0)
                print(param, val)
                param_bank_offboard.append(val)

            if param_bank_onboard == param_bank_offboard:
                print("\n Placa BID aprovada!\n")
            else:
                print("\n Placa BID reprovada!\n")

        except:
            print(" Placa BID reprovada!\n")

    def upload_parameters_bid(self, password):
        print("\n Desbloqueando UDC ...")
        print(self.unlock_udc(password))

        print("\n Carregando banco de parametros da memoria offboard ...")
        print(self.load_param_bank(type_memory=1))
        time.sleep(1)

        print("\n Salvando banco de parametros na memoria onboard ...")
        print(self.save_param_bank(type_memory=2))
        time.sleep(5)

        print("\n Carregando coeficientes de controle da memoria offboard ...")
        print(self.load_dsp_modules_eeprom(type_memory=1))
        time.sleep(1)

        print("\n Salvando coeficientes de controle na memoria onboard ...\n")
        print(self.save_dsp_modules_eeprom(type_memory=2))

    def download_parameters_bid(self, password):
        print("\n Desbloqueando UDC ...")
        print(self.unlock_udc(password))

        print("\n Carregando banco de parametros da memoria onboard ...")
        print(self.load_param_bank(type_memory=2))
        time.sleep(1)

        print("\n Salvando banco de parametros na memoria offboard ...")
        print(self.save_param_bank(type_memory=1))
        time.sleep(5)

        print("\n Carregando coeficientes de controle da memoria onboard ...")
        print(self.load_dsp_modules_eeprom(type_memory=2))
        time.sleep(1)

        print("\n Salvando coeficientes de controle na memoria offboard ...")
        print(self.save_dsp_modules_eeprom(type_memory=1))
