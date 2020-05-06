'''EMS bus hass component constants'''

DOMAIN = 'ems_bus'

DATA_EMSBUS_CONFIG = 'ems_bus_config'
DATA_PROTOCOL = 'ems_bus_protocol'
DATA_DEVICES = 'ems_bus_devices'

CONF_SERIAL_PATH = 'serial_path'
#CONF_CLIENT_ID = 'client_id'
CONF_LOG_LEVEL = 'log_level'

DEFAULT_SERIAL_PATH = '/dev/ttyAMA0'
DEFAULT_CLIENT_ID = 0x0B
DEFAULT_LOG_LEVEL = 3

SERVICE_STATS = 'stats'

PLATFORMS = ['switch', 'climate', 'sensor', 'binary_sensor', 'input_select', 'input_number']
