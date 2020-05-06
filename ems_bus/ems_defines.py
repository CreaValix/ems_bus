'''
Definitions for the EMS bus
'''

EMS_MIN_TELEGRAM_LENGTH = 6
EMS_MAX_TELEGRAM_LENGTH = 32

# Bus message types
EMS_TYPE_UBA_MONITOR_FAST = 0x18       # is an automatic monitor broadcast
EMS_TYPE_UBA_MONITOR_SLOW = 0x19       # is an automatic monitor broadcast
EMS_TYPE_UBA_MONITOR_WW = 0x34         # is an automatic monitor broadcast
EMS_TYPE_UBA_MAINTENANCE_STATUS = 0x1C # is an automatic monitor broadcast
EMS_TYPE_UBA_PARAM_WW = 0x33
EMS_TYPE_UBA_TOTAL_UPTIME_MESSAGE = 0x14
EMS_TYPE_UBA_FLAGS = 0x35
EMS_TYPE_UBA_MAINTENANCE_SETTINGS = 0x15
EMS_TYPE_UBA_PARAM = 0x16
EMS_TYPE_UBA_SET_POINT = 0x1A
EMS_TYPE_UBA_FUNCTION_TEST = 0x1D
# RC35 status broadcasts for heat circuits
EMS_TYPE_RC35_STATUS_HC1 = 0x3E # is an automatic thermostat broadcast giving us temps on HC1
EMS_TYPE_RC35_STATUS_HC2 = 0x48 # is an automatic thermostat broadcast giving us temps on HC2
EMS_TYPE_RC35_STATUS_HC3 = 0x52 # is an automatic thermostat broadcast giving us temps on HC3
EMS_TYPE_RC35_STATUS_HC4 = 0x5C # is an automatic thermostat broadcast giving us temps on HC4
# RC35 settings for heat circuits
EMS_TYPE_RC35_SET_HC1 = 0x3D    # for setting values like temp and mode (Working mode HC1)
EMS_TYPE_RC35_SET_HC2 = 0x47    # for setting values like temp and mode (Working mode HC2)
EMS_TYPE_RC35_SET_HC3 = 0x51    # for setting values like temp and mode (Working mode HC3)
EMS_TYPE_RC35_SET_HC4 = 0x5B    # for setting values like temp and mode (Working mode HC4)

# Offsets for EMS_TYPE_UBA_PARAM_WW
EMS_OFFSET_UBA_PARAM_ONE_TIME = 0  # One time loading
EMS_OFFSET_UBA_PARAM_ACTIVATED = 1 # Activated
EMS_OFFSET_UBA_PARAM_WW_TEMP = 2   # Temperature
EMS_OFFSET_UBA_PARAM_COMFORT = 9   # Comfort or eco mode

# RC35 status offsets
EMS_OFFSET_RC35_STATUS_MODE = 0     # for holiday mode
EMS_OFFSET_RC35_STATUS_MODE = 1     # day mode, also summer on RC3's
EMS_OFFSET_RC35_STATUS_SETPOINT = 2 # desired temp
EMS_OFFSET_RC35_STATUS_CURRENT = 3  # current temp

# RC35 set offsets
EMS_OFFSET_RC35_SET_HEATING_MODE = 0        # floor heating = 3 0x47
EMS_OFFSET_RC35_SET_TEMP_NIGHT = 1          # thermostat setpoint temperature for night time
EMS_OFFSET_RC35_SET_TEMP_DAY = 2            # thermostat setpoint temperature for day time
EMS_OFFSET_RC35_SET_TEMP_HOLIDAY = 3        # temp during holiday 0x47
EMS_OFFSET_RC35_SET_TEMP_ROOM_INFLUENCE = 4 # temp during holiday 0x47
EMS_OFFSET_RC35_SET_TEMP_ROOM_OFFSET = 6    # temp during holiday 0x47
EMS_OFFSET_RC35_SET_MODE = 7                # thermostat mode
EMS_OFFSET_RC35_SET_CALC_CIRCUIT_TEMP = 14  # calculated circuit temperature 0x48
EMS_OFFSET_RC35_SET_TEMP_SUMMER = 22        # temp during holiday 0x47

EMS_FMT_DATETIME = 0
