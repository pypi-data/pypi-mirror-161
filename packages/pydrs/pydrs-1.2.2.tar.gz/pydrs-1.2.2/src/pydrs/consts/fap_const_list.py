"""""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """''
======================================================================
                    Listas de Entidades BSMP
        A posição da entidade na lista corresponde ao seu ID BSMP
======================================================================
""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" ""

# FAP
list_fap_soft_interlocks = [
    "DCCT 1 Fault",
    "DCCT 2 Fault",
    "DCCT High Difference",
    "Load Feedback 1 Fault",
    "Load Feedback 2 Fault",
    "IGBTs Current High Difference",
]

list_fap_hard_interlocks = [
    "Load Overcurrent",
    "Load Overvoltage",
    "DCLink Overvoltage",
    "DCLink Undervoltage",
    "Welded Contactor Fault",
    "Opened Contactor Fault",
    "IGBT 1 Overcurrent",
    "IGBT 2 Overcurrent",
    "IIB Itlk",
]

list_fap_iib_interlocks = [
    "Input Overvoltage",
    "Output Overvoltage",
    "IGBT 1 Overcurrent",
    "IGBT 2 Overcurrent",
    "IGBT 1 Overtemperature",
    "IGBT 2 Overtemperature",
    "Driver Overvoltage",
    "Driver 1 Overcurrent",
    "Driver 2 Overcurrent",
    "Driver 1 Error",
    "Driver 2 Error",
    "Inductors Overtemperature",
    "Heat-Sink Overtemperature",
    "DCLink Contactor Fault",
    "Contact Sticking of Contactor",
    "External Interlock",
    "Rack Interlock",
    "High Leakage Current",
    "Board IIB Overtemperature",
    "Module Overhumidity",
]

list_fap_iib_alarms = [
    "Input Overvoltage",
    "Output Overvoltage",
    "IGBT 1 Overcurrent",
    "IGBT 2 Overcurrent",
    "IGBT 1 Overtemperature",
    "IGBT 2 Overtemperature",
    "Driver Overvoltage",
    "Driver 1 Overcurrent",
    "Driver 2 Overcurrent",
    "Inductors Overtemperature",
    "Heat-Sink Overtemperature",
    "High Leakage Current",
    "Board IIB Overtemperature",
    "Module Overhumidity",
]

# FAP-4P
list_fap_4p_soft_interlocks = [
    "DCCT 1 Fault",
    "DCCT 2 Fault",
    "DCCT High Difference",
    "Load Feedback 1 Fault",
    "Load Feedback 2 Fault",
    "IGBTs Current High Difference",
]

list_fap_4p_hard_interlocks = [
    "Load Overcurrent",
    "Load Overvoltage",
    "IGBT 1 Mod 1 Overcurrent",
    "IGBT 2 Mod 1 Overcurrent",
    "IGBT 1 Mod 2 Overcurrent",
    "IGBT 2 Mod 2 Overcurrent",
    "IGBT 1 Mod 3 Overcurrent",
    "IGBT 2 Mod 3 Overcurrent",
    "IGBT 1 Mod 4 Overcurrent",
    "IGBT 2 Mod 4 Overcurrent",
    "Welded Contactor Mod 1 Fault",
    "Welded Contactor Mod 2 Fault",
    "Welded Contactor Mod 3 Fault",
    "Welded Contactor Mod 4 Fault",
    "Opened Contactor Mod 1 Fault",
    "Opened Contactor Mod 2 Fault",
    "Opened Contactor Mod 3 Fault",
    "Opened Contactor Mod 4 Fault",
    "DCLink Mod 1 Overvoltage",
    "DCLink Mod 2 Overvoltage",
    "DCLink Mod 3 Overvoltage",
    "DCLink Mod 4 Overvoltage",
    "DCLink Mod 1 Undervoltage",
    "DCLink Mod 2 Undervoltage",
    "DCLink Mod 3 Undervoltage",
    "DCLink Mod 4 Undervoltage",
    "IIB Mod 1 Itlk",
    "IIB Mod 2 Itlk",
    "IIB Mod 3 Itlk",
    "IIB Mod 4 Itlk",
]

list_fap_4p_iib_interlocks = list_fap_iib_interlocks
list_fap_4p_iib_alarms = list_fap_iib_alarms

# FAP-2P2S
list_fap_2p2s_soft_interlocks = [
    "DCCT 1 Fault",
    "DCCT 2 Fault",
    "DCCT High Difference",
    "Load Feedback 1 Fault",
    "Load Feedback 2 Fault",
    "Arms High Difference",
    "IGBTs Current High Difference",
    "Complementary PS Interlock",
]

list_fap_2p2s_hard_interlocks = [
    "Load Overcurrent",
    "IGBT 1 Mod 1 Overcurrent",
    "IGBT 2 Mod 1 Overcurrent",
    "IGBT 1 Mod 2 Overcurrent",
    "IGBT 2 Mod 2 Overcurrent",
    "IGBT 1 Mod 3 Overcurrent",
    "IGBT 2 Mod 3 Overcurrent",
    "IGBT 1 Mod 4 Overcurrent",
    "IGBT 2 Mod 4 Overcurrent",
    "Welded Contactor Mod 1 Fault",
    "Welded Contactor Mod 2 Fault",
    "Welded Contactor Mod 3 Fault",
    "Welded Contactor Mod 4 Fault",
    "Opened Contactor Mod 1 Fault",
    "Opened Contactor Mod 2 Fault",
    "Opened Contactor Mod 3 Fault",
    "Opened Contactor Mod 4 Fault",
    "DCLink Mod 1 Overvoltage",
    "DCLink Mod 2 Overvoltage",
    "DCLink Mod 3 Overvoltage",
    "DCLink Mod 4 Overvoltage",
    "DCLink Mod 1 Undervoltage",
    "DCLink Mod 2 Undervoltage",
    "DCLink Mod 3 Undervoltage",
    "DCLink Mod 4 Undervoltage",
    "IIB Mod 1 Itlk",
    "IIB Mod 2 Itlk",
    "IIB Mod 3 Itlk",
    "IIB Mod 4 Itlk",
    "Arm 1 Overcurrent",
    "Arm 2 Overcurrent",
]

list_fap_2p2s_iib_interlocks = list_fap_iib_interlocks
list_fap_2p2s_iib_alarms = list_fap_iib_alarms

# FAP 225A
list_fap_225A_soft_interlocks = ["IGBTs Current High Difference"]

list_fap_225A_hard_interlocks = [
    "Load Overcurrent",
    "DCLink Contactor Fault",
    "IGBT 1 Overcurrent",
    "IGBT 2 Overcurrent",
]
