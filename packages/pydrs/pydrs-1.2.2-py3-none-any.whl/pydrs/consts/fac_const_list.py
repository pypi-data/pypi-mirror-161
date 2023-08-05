"""""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """''
======================================================================
                    Listas de Entidades BSMP
        A posição da entidade na lista corresponde ao seu ID BSMP
======================================================================
""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" ""

# FAC ACDC
list_fac_acdc_soft_interlocks = []

list_fac_acdc_hard_interlocks = [
    "CapBank Overvoltage",
    "Rectifier Overvoltage",
    "Rectifier Undervoltage",
    "Rectifier Overcurrent",
    "Welded Contactor Fault",
    "Opened Contactor Fault",
    "IIB Input Stage Interlock",
    "IIB Command Interlock",
]

list_fac_acdc_iib_is_interlocks = [
    "Rectifier Overvoltage",
    "Input Overcurrent",
    "IGBT Overtemperature",
    "IGBT Overtemperature HW",
    "Driver Overvoltage",
    "Driver Overcurrent",
    "Top Driver Error",
    "Bottom Driver Error",
    "Inductors Overtemperature",
    "Heat-Sink Overtemperature",
    "Board IIB Overtemperature",
    "Module Overhumidity",
]

list_fac_acdc_iib_is_alarms = [
    "Rectifier Overvoltage",
    "Input Overcurrent",
    "IGBT Overtemperature",
    "Driver Overvoltage",
    "Driver Overcurrent",
    "Inductors Overtemperature",
    "Heat-Sink Overtemperature",
    "Board IIB Overtemperature",
    "Module Overhumidity",
]

list_fac_acdc_iib_cmd_interlocks = [
    "Capbank Overvoltage",
    "Output Overvoltage",
    "External Boards Overvoltage",
    "Auxiliary Board Overcurrent",
    "IDB Board Overcurrent",
    "Rectifier Inductor Overtemperature",
    "Rectifier Heat-Sink Overtemperature",
    "AC Mains Overcurrent",
    "Emergency Button",
    "AC Mains Undervoltage",
    "AC Mains Overvoltage",
    "Ground Leakage Overcurrent",
    "Board IIB Overtemperature",
    "Module Overhumidity",
]

list_fac_acdc_iib_cmd_alarms = [
    "Capbank Overvoltage",
    "Output Overvoltage",
    "External Boards Overvoltage",
    "Auxiliary Board Overcurrent",
    "IDB Board Overcurrent",
    "Rectifier Inductor Overtemperature",
    "Rectifier Heat-Sink Overtemperature",
    "Ground Leakage Overcurrent",
    "Board IIB Overtemperature",
    "Module Overhumidity",
]

# FAC DCDC
list_fac_dcdc_soft_interlocks = [
    "DCCT 1 Fault",
    "DCCT 2 Fault",
    "DCCT High Difference",
    "Load Feedback 1 Fault",
    "Load Feedback 2 Fault",
]

list_fac_dcdc_hard_interlocks = [
    "Load Overcurrent",
    "CapBank Overvoltage",
    "CapBank Undervoltage",
    "IIB Interlock",
    "External Interlock",
    "Rack Interlock",
]

list_fac_dcdc_iib_interlocks = [
    "Input Overvoltage",
    "Input Overcurrent",
    "Output Overcurrent",
    "IGBT 1 Overtemperature",
    "IGBT 1 Overtemperature HW",
    "IGBT 2 Overtemperature",
    "IGBT 2 Overtemperature HW",
    "Driver Overvoltage",
    "Driver 1 Overcurrent",
    "Driver 2 Overcurrent",
    "Top Driver 1 Error",
    "Bottom Driver 1 Error",
    "Top Driver 2 Error",
    "Bottom Driver 2 Error",
    "Inductors Overtemperature",
    "Heat-Sink Overtemperature",
    "Ground Leakage Overcurrent",
    "Board IIB Overtemperature",
    "Module Overhumidity",
]

list_fac_dcdc_iib_alarms = [
    "Input Overvoltage",
    "Input Overcurrent",
    "Output Overcurrent",
    "IGBT 1 Overtemperature",
    "IGBT 2 Overtemperature",
    "Driver Overvoltage",
    "Driver 1 Overcurrent",
    "Driver 2 Overcurrent",
    "Inductors Overtemperature",
    "Heat-Sink Overtemperature",
    "Ground Leakage Overcurrent",
    "Board IIB Overtemperature",
    "Module Overhumidity",
]

# FAC-2S AC/DC
list_fac_2s_acdc_soft_interlocks = []
list_fac_2s_acdc_hard_interlocks = [
    "CapBank Overvoltage",
    "Rectifier Overvoltage",
    "Rectifier Undervoltage",
    "Rectifier Overcurrent",
    "Welded Contactor Fault",
    "Opened Contactor Fault",
    "IIB Input Stage Interlock",
    "IIB Command Interlock",
]

list_fac_2s_acdc_iib_is_interlocks = list_fac_acdc_iib_is_interlocks
list_fac_2s_acdc_iib_cmd_interlocks = list_fac_acdc_iib_cmd_interlocks
list_fac_2s_acdc_iib_is_alarms = list_fac_acdc_iib_is_alarms
list_fac_2s_acdc_iib_cmd_alarms = list_fac_acdc_iib_cmd_alarms

# FAC-2S DC/DC
list_fac_2s_dcdc_soft_interlocks = [
    "DCCT 1 Fault",
    "DCCT 2 Fault",
    "DCCT High Difference",
    "Load Feedback 1 Fault",
    "Load Feedback 2 Fault",
]

list_fac_2s_dcdc_hard_interlocks = [
    "Load Overcurrent",
    "Module 1 CapBank Overvoltage",
    "Module 2 CapBank Overvoltage",
    "Module 1 CapBank Undervoltage",
    "Module 2 CapBank Undervoltage",
    "IIB Mod 1 Itlk",
    "IIB Mod 2 Itlk",
    "External Interlock",
    "Rack Interlock",
]

list_fac_2s_dcdc_iib_interlocks = list_fac_dcdc_iib_interlocks
list_fac_2s_dcdc_iib_alarms = list_fac_dcdc_iib_alarms

# FAC-2P4S AC/DC
list_fac_2p4s_acdc_hard_interlocks = [
    "CapBank Overvoltage",
    "Rectifier Overvoltage",
    "Rectifier Undervoltage",
    "Rectifier Overcurrent",
    "Welded Contactor Fault",
    "Opened Contactor Fault",
    "IIB Input Stage Interlock",
    "IIB Command Interlock",
]

list_fac_2p4s_acdc_iib_is_interlocks = list_fac_acdc_iib_is_interlocks
list_fac_2p4s_acdc_iib_cmd_interlocks = list_fac_acdc_iib_cmd_interlocks
list_fac_2p4s_acdc_iib_is_alarms = list_fac_acdc_iib_is_alarms
list_fac_2p4s_acdc_iib_cmd_alarms = list_fac_acdc_iib_cmd_alarms

# FAC-2P4S DC/DC
list_fac_2p4s_dcdc_soft_interlocks = [
    "DCCT 1 Fault",
    "DCCT 2 Fault",
    "DCCT High Difference",
    "Load Feedback 1 Fault",
    "Load Feedback 2 Fault",
    "Arm 1 Overcurrent",
    "Arm 2 Overcurrent",
    "Arms High Difference",
    "Complementary PS Interlock",
]

list_fac_2p4s_dcdc_hard_interlocks = [
    "Load Overcurrent",
    "Module 1 CapBank Overvoltage",
    "Module 2 CapBank Overvoltage",
    "Module 3 CapBank Overvoltage",
    "Module 4 CapBank Overvoltage",
    "Module 5 CapBank Overvoltage",
    "Module 6 CapBank Overvoltage",
    "Module 7 CapBank Overvoltage",
    "Module 8 CapBank Overvoltage",
    "Module 1 CapBank Undervoltage",
    "Module 2 CapBank Undervoltage",
    "Module 3 CapBank Undervoltage",
    "Module 4 CapBank Undervoltage",
    "Module 5 CapBank Undervoltage",
    "Module 6 CapBank Undervoltage",
    "Module 7 CapBank Undervoltage",
    "Module 8 CapBank Undervoltage",
    "IIB 1 Itlk",
    "IIB 2 Itlk",
    "IIB 3 Itlk",
    "IIB 4 Itlk",
    "IIB 5 Itlk",
    "IIB 6 Itlk",
    "IIB 7 Itlk",
    "IIB 8 Itlk",
]

list_fac_2p4s_dcdc_iib_interlocks = list_fac_dcdc_iib_interlocks
list_fac_2p4s_dcdc_iib_alarms = list_fac_dcdc_iib_alarms

# FAC DCDC EMA
list_fac_dcdc_ema_soft_interlocks = ["DCCT Fault", "Load Feedback Fault"]

list_fac_dcdc_ema_hard_interlocks = [
    "Load Overcurrent",
    "DCLink Overvoltage",
    "DCLink Undervoltage",
    "Emergency Button",
    "Load Waterflow",
    "Load Overtemperature",
    "IIB Itlk",
]

list_fac_dcdc_ema_iib_interlocks = [
    "Input Overvoltage",
    "Input Overcurrent",
    "Output Overcurrent",
    "IGBT 1 Overtemperature",
    "IGBT 1 Overtemperature HW",
    "IGBT 2 Overtemperature",
    "IGBT 2 Overtemperature HW",
    "Driver Overvoltage",
    "Driver 1 Overcurrent",
    "Driver 2 Overcurrent",
    "Top Driver 1 Error",
    "Bottom Driver 1 Error",
    "Top Driver 2 Error",
    "Bottom Driver 2 Error",
    "Inductors Overtemperature",
    "Heat-Sink Overtemperature",
    "Ground Leakage Overcurrent",
    "Board IIB Overtemperature",
    "Module Overhumidity",
]

list_fac_dcdc_ema_iib_alarms = [
    "Input Overvoltage",
    "Input Overcurrent",
    "Output Overcurrent",
    "IGBT 1 Overtemperature",
    "IGBT 2 Overtemperature",
    "Driver Overvoltage",
    "Driver 1 Overcurrent",
    "Driver 2 Overcurrent",
    "Inductors Overtemperature",
    "Heat-Sink Overtemperature",
    "Ground Leakage Overcurrent",
    "Board IIB Overtemperature",
    "Module Overhumidity",
]

# FAC-2P ACDC
list_fac_2p_acdc_imas_soft_interlocks = []

list_fac_2p_acdc_imas_hard_interlocks = [
    "CapBank Overvoltage",
    "Rectifier Overcurrent",
    "AC Mains Contactor Fault",
    "Module A Interlock",
    "Module B Interlock",
    "DCDC Interlock",
]

# FAC-2P DCDC
list_fac_2p_dcdc_imas_soft_interlocks = []

list_fac_2p_dcdc_imas_hard_interlocks = [
    "Load Overcurrent",
    "Module 1 CapBank_Overvoltage",
    "Module 2 CapBank_Overvoltage",
    "Module 1 CapBank_Undervoltage",
    "Module 2 CapBank_Undervoltage",
    "Arm 1 Overcurrent",
    "Arm 2 Overcurrent",
    "Arms High_Difference",
    "ACDC Interlock",
]
