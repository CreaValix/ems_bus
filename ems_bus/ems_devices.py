''' List of known devices for the EMS bus '''

from ems_bus.ems_messages import \
    UbaSetValuesMessage, UbaDrinkwaterParameterMessage, Hc1ParamMessage, Hc1MonitorMessage, \
    UbaDrinkwaterMonitorMessage, UbaMonitorFast, UbaMonitorSlow, HcDrinkwaterParam

EMS_DEVICE_TYPE_NONE = 0
EMS_DEVICE_TYPE_SERVICEKEY = 1
EMS_DEVICE_TYPE_BOILER = 2
EMS_DEVICE_TYPE_THERMOSTAT = 3
EMS_DEVICE_TYPE_MIXING = 4
EMS_DEVICE_TYPE_SOLAR = 5
EMS_DEVICE_TYPE_HEATPUMP = 6
EMS_DEVICE_TYPE_GATEWAY = 7
EMS_DEVICE_TYPE_OTHER = 8
EMS_DEVICE_TYPE_SWITCH = 9
EMS_DEVICE_TYPE_CONTROLLER = 10
EMS_DEVICE_TYPE_CONNECT = 11
EMS_DEVICE_TYPE_UNKNOWN = 12

EMS_DEVICE_TYPE_NAMES = [
    'none', 'service key', 'boiler', 'thermostat', 'mixer', 'solar panel', 'heat pump', 'gateway',
    'other device', 'switch', 'controller', 'connector', 'unknown device'
]
EMS_INITIAL_REQUESTS = {
    EMS_DEVICE_TYPE_BOILER: (
        UbaMonitorFast, UbaMonitorSlow, UbaSetValuesMessage, UbaDrinkwaterParameterMessage,
        UbaDrinkwaterMonitorMessage),
    EMS_DEVICE_TYPE_THERMOSTAT: (Hc1ParamMessage, Hc1MonitorMessage, HcDrinkwaterParam),
}

EMS_DEVICE_FLAG_NONE = 0
EMS_DEVICE_FLAG_SM10 = 10  # solar module1
EMS_DEVICE_FLAG_SM100 = 11 # solar module2

EMS_DEVICE_FLAG_NO_WRITE = 0x80 # top bit set if write not supported
EMS_DEVICE_FLAG_EASY = 1
EMS_DEVICE_FLAG_RC10 = 2
EMS_DEVICE_FLAG_RC20 = 3
EMS_DEVICE_FLAG_RC30 = 4
EMS_DEVICE_FLAG_RC35 = 5
EMS_DEVICE_FLAG_RC300 = 6
EMS_DEVICE_FLAG_JUNKERS = 7

EMS_DEVICES = [

    #
    # UBA Masters - typically with device_id of 0x08
    #
    [72, EMS_DEVICE_TYPE_BOILER, 'MC10 Module', EMS_DEVICE_FLAG_NONE],
    [123, EMS_DEVICE_TYPE_BOILER, 'Buderus GBx72/Nefit Trendline/Junkers Cerapur/Worcester Greenstar Si/27i', EMS_DEVICE_FLAG_NONE],
    [133, EMS_DEVICE_TYPE_BOILER, 'Buderus GB125/Logamatic MC110', EMS_DEVICE_FLAG_NONE],
    [115, EMS_DEVICE_TYPE_BOILER, 'Nefit Topline/Buderus GB162', EMS_DEVICE_FLAG_NONE],
    [203, EMS_DEVICE_TYPE_BOILER, 'Buderus Logamax U122/Junkers Cerapur', EMS_DEVICE_FLAG_NONE],
    [208, EMS_DEVICE_TYPE_BOILER, 'Buderus Logamax plus/GB192/Bosch Condens GC9000', EMS_DEVICE_FLAG_NONE],
    [64, EMS_DEVICE_TYPE_BOILER, 'Sieger BK13,BK15/Nefit Smartline/Buderus GB1x2', EMS_DEVICE_FLAG_NONE],
    [234, EMS_DEVICE_TYPE_BOILER, 'Buderus Logamax Plus GB122', EMS_DEVICE_FLAG_NONE],
    [95, EMS_DEVICE_TYPE_BOILER, 'Bosch Condens 2500/Buderus Logamax GB062/Junkers Cerapur Top/Worcester Greenstar i/Generic HT3', EMS_DEVICE_FLAG_NONE],
    [122, EMS_DEVICE_TYPE_BOILER, 'Nefit Proline', EMS_DEVICE_FLAG_NONE],
    [170, EMS_DEVICE_TYPE_BOILER, 'Buderus Logano GB212', EMS_DEVICE_FLAG_NONE],
    [172, EMS_DEVICE_TYPE_BOILER, 'Nefit Enviline', EMS_DEVICE_FLAG_NONE],

    #
    # Solar Modules - type 0x30
    #
    [73, EMS_DEVICE_TYPE_SOLAR, 'SM10 Solar Module', EMS_DEVICE_FLAG_SM10],
    [163, EMS_DEVICE_TYPE_SOLAR, 'SM100 Solar Module', EMS_DEVICE_FLAG_SM100],
    [101, EMS_DEVICE_TYPE_SOLAR, 'Junkers ISM1 Solar Module', EMS_DEVICE_FLAG_SM100],
    [162, EMS_DEVICE_TYPE_SOLAR, 'SM50 Solar Module', EMS_DEVICE_FLAG_SM100],

    #
    # Mixing Devices - type 0x20 or 0x21
    #
    [160, EMS_DEVICE_TYPE_MIXING, 'MM100 Mixing Module', EMS_DEVICE_FLAG_NONE],
    [161, EMS_DEVICE_TYPE_MIXING, 'MM200 Mixing Module', EMS_DEVICE_FLAG_NONE],
    [69, EMS_DEVICE_TYPE_MIXING, 'MM10 Mixer Module', EMS_DEVICE_FLAG_NONE],
    [159, EMS_DEVICE_TYPE_MIXING, 'MM50 Mixing Module', EMS_DEVICE_FLAG_NONE],
    [79, EMS_DEVICE_TYPE_MIXING, 'MM100 Mixer Module', EMS_DEVICE_FLAG_NONE],
    [80, EMS_DEVICE_TYPE_MIXING, 'MM200 Mixer Module', EMS_DEVICE_FLAG_NONE],
    [78, EMS_DEVICE_TYPE_MIXING, 'MM400 Mixer Module', EMS_DEVICE_FLAG_NONE],

    #
    # HeatPump - type 0x38
    #
    [252, EMS_DEVICE_TYPE_HEATPUMP, 'HeatPump Module', EMS_DEVICE_FLAG_NONE],
    [200, EMS_DEVICE_TYPE_HEATPUMP, 'HeatPump Module', EMS_DEVICE_FLAG_NONE],

    #
    # Other devices, like 0x11 for Switching, 0x09 for controllers, 0x02 for Connect, 0x48 for Gateway
    #
    [71, EMS_DEVICE_TYPE_SWITCH, 'WM10 Switch Module', EMS_DEVICE_FLAG_NONE],                        # 0x11
    [68, EMS_DEVICE_TYPE_CONTROLLER, 'BC10/RFM20 Receiver', EMS_DEVICE_FLAG_NONE],                   # 0x09
    [218, EMS_DEVICE_TYPE_CONTROLLER, 'Junkers M200/Buderus RFM200 Receiver', EMS_DEVICE_FLAG_NONE], # 0x50
    [190, EMS_DEVICE_TYPE_CONTROLLER, 'BC10 Base Controller', EMS_DEVICE_FLAG_NONE],                 # 0x09
    [114, EMS_DEVICE_TYPE_CONTROLLER, 'BC10 Base Controller', EMS_DEVICE_FLAG_NONE],                 # 0x09
    [125, EMS_DEVICE_TYPE_CONTROLLER, 'BC25 Base Controller', EMS_DEVICE_FLAG_NONE],                 # 0x09
    [169, EMS_DEVICE_TYPE_CONTROLLER, 'BC40 Base Controller', EMS_DEVICE_FLAG_NONE],                 # 0x09
    [152, EMS_DEVICE_TYPE_CONTROLLER, 'Controller', EMS_DEVICE_FLAG_NONE],                           # 0x09
    [95, EMS_DEVICE_TYPE_CONTROLLER, 'HT3 Controller', EMS_DEVICE_FLAG_NONE],                        # 0x09
    [230, EMS_DEVICE_TYPE_CONTROLLER, 'BC Base Controller', EMS_DEVICE_FLAG_NONE],                   # 0x09
    [205, EMS_DEVICE_TYPE_CONNECT, 'Nefit Moduline Easy Connect', EMS_DEVICE_FLAG_NONE],             # 0x02
    [206, EMS_DEVICE_TYPE_CONNECT, 'Bosch Easy Connect', EMS_DEVICE_FLAG_NONE],                      # 0x02
    [171, EMS_DEVICE_TYPE_CONNECT, 'EMS-OT OpenTherm converter', EMS_DEVICE_FLAG_NONE],              # 0x02
    [189, EMS_DEVICE_TYPE_GATEWAY, 'Web Gateway KM200', EMS_DEVICE_FLAG_NONE],                       # 0x48

    #
    # Thermostats, typically device id of 0x10, 0x17 and 0x18
    #

    # Easy devices - not currently supporting write operations
    [202, EMS_DEVICE_TYPE_THERMOSTAT, 'Logamatic TC100/Nefit Moduline Easy', EMS_DEVICE_FLAG_EASY | EMS_DEVICE_FLAG_NO_WRITE], # 0x18, cannot write
    [203, EMS_DEVICE_TYPE_THERMOSTAT, 'Bosch EasyControl CT200', EMS_DEVICE_FLAG_EASY | EMS_DEVICE_FLAG_NO_WRITE],             # 0x18, cannot write
    [157, EMS_DEVICE_TYPE_THERMOSTAT, 'Buderus RC200/Bosch CW100/Junkers CW100', EMS_DEVICE_FLAG_NO_WRITE],                    # 0x18, cannot write

    # Buderus/Nefit
    [79, EMS_DEVICE_TYPE_THERMOSTAT, 'RC10/Moduline 100', EMS_DEVICE_FLAG_RC10],                                    # 0x17
    [77, EMS_DEVICE_TYPE_THERMOSTAT, 'RC20/Moduline 300', EMS_DEVICE_FLAG_RC20],                                    # 0x17
    [93, EMS_DEVICE_TYPE_THERMOSTAT, 'RC20RF', EMS_DEVICE_FLAG_RC20],                                               # 0x18
    [67, EMS_DEVICE_TYPE_THERMOSTAT, 'RC30', EMS_DEVICE_FLAG_RC30],                                                 # 0x10
    [78, EMS_DEVICE_TYPE_THERMOSTAT, 'RC30/Moduline 400', EMS_DEVICE_FLAG_RC30],                                    # 0x10
    [86, EMS_DEVICE_TYPE_THERMOSTAT, 'RC35', EMS_DEVICE_FLAG_RC35],                                                 # 0x10
    [158, EMS_DEVICE_TYPE_THERMOSTAT, 'RC300/RC310/Moduline 3000/Bosch CW400/W-B Sense II', EMS_DEVICE_FLAG_RC300], # 0x10
    [165, EMS_DEVICE_TYPE_THERMOSTAT, 'RC100/Moduline 1010', EMS_DEVICE_FLAG_RC300 | EMS_DEVICE_FLAG_NO_WRITE],     # 0x18, cannot write

    # Sieger
    [76, EMS_DEVICE_TYPE_THERMOSTAT, 'Sieger ES73', EMS_DEVICE_FLAG_RC35], # 0x10

    # Junkers
    [105, EMS_DEVICE_TYPE_THERMOSTAT, 'Junkers FW100', EMS_DEVICE_FLAG_JUNKERS | EMS_DEVICE_FLAG_NO_WRITE], # 0x10, cannot write
    [106, EMS_DEVICE_TYPE_THERMOSTAT, 'Junkers FW200', EMS_DEVICE_FLAG_JUNKERS | EMS_DEVICE_FLAG_NO_WRITE], # 0x10, cannot write
    [107, EMS_DEVICE_TYPE_THERMOSTAT, 'Junkers FR100', EMS_DEVICE_FLAG_JUNKERS | EMS_DEVICE_FLAG_NO_WRITE], # 0x10, cannot write
    [108, EMS_DEVICE_TYPE_THERMOSTAT, 'Junkers FR110', EMS_DEVICE_FLAG_JUNKERS | EMS_DEVICE_FLAG_NO_WRITE], # 0x10, cannot write
    [111, EMS_DEVICE_TYPE_THERMOSTAT, 'Junkers FR10', EMS_DEVICE_FLAG_JUNKERS | EMS_DEVICE_FLAG_NO_WRITE],  # 0x10, cannot write
    [191, EMS_DEVICE_TYPE_THERMOSTAT, 'Junkers FR120', EMS_DEVICE_FLAG_JUNKERS | EMS_DEVICE_FLAG_NO_WRITE], # 0x10, cannot write
    [192, EMS_DEVICE_TYPE_THERMOSTAT, 'Junkers FW120', EMS_DEVICE_FLAG_JUNKERS | EMS_DEVICE_FLAG_NO_WRITE], # 0x10, cannot write
    [147, EMS_DEVICE_TYPE_THERMOSTAT, 'Junkers FR50', EMS_DEVICE_FLAG_JUNKERS | EMS_DEVICE_FLAG_NO_WRITE]   # 0x10, cannot write
]
