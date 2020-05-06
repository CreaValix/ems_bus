'''Support for EMS bus'''

import logging

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from ems_bus.ems_fields import BooleanField, BooleanIntegerField, Field, IntegerField, StringField
from ems_bus.ems_protocol import EmsProtocol
from ems_bus.ems_units import UnitCelsius
from homeassistant import bootstrap, config_entries
from homeassistant.const import CONF_DEVICE, EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STOP
from homeassistant.helpers import discovery
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.entity_platform import DATA_ENTITY_PLATFORM

#from .binary_sensor import EmsBusBinarySensor
from .climate import EmsBusClimate
from .const import CONF_LOG_LEVEL, CONF_SERIAL_PATH, DATA_DEVICES, DATA_EMSBUS_CONFIG, \
                   DATA_PROTOCOL, DEFAULT_CLIENT_ID, DEFAULT_LOG_LEVEL, DEFAULT_SERIAL_PATH, \
                   DOMAIN, PLATFORMS, SERVICE_STATS
from .input_number import EmsBusInputNumber
from .input_select import EmsBusInputSelect
from .sensor import EmsBusSensor
from .switch import EmsBusSwitch

LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_SERIAL_PATH): vol.Coerce(str),
                vol.Optional(CONF_LOG_LEVEL): vol.Coerce(int),
            }
        )
    },
    extra=vol.ALLOW_EXTRA
)

async def async_setup(hass, config):
    '''Old way of setting up integrations.'''

    # Client ID must match the serial driver client ID which is hardcoded.
    # So disable that option for now.
    conf = config.get(DOMAIN)
    if conf is not None:
        serial_path = conf.get(CONF_SERIAL_PATH, DEFAULT_SERIAL_PATH)
        log_level = conf.get(CONF_LOG_LEVEL, DEFAULT_LOG_LEVEL)
        #client_id = conf.get(CONF_CLIENT_ID, DEFAULT_CLIENT_ID)
    else:
        serial_path = DEFAULT_SERIAL_PATH
        log_level = DEFAULT_LOG_LEVEL
        #client_id = DEFAULT_CLIENT_ID

    async def event_handler(signal, device, message, affected_fields):
        '''Callback function when update events happen on the EMS bus'''
        for field_name, field_obj in message.get_fields():
            platform_name = None
            if getattr(message.Meta, 'write', False):
                if issubclass(field_obj.__class__, BooleanField) or \
                   issubclass(field_obj.__class__, BooleanIntegerField):
                    # Boolean values -> switch
                    platform_name = 'switch'
                    platform_type = EmsBusSwitch
                elif issubclass(field_obj.__class__, IntegerField):
                    if field_obj.unit == UnitCelsius:
                        # Celsius values -> climate
                        platform_name = 'climate'
                        platform_type = EmsBusClimate
                    elif hasattr(field_obj.unit, 'VALUES'):
                        # Multiple choice values -> Input select
                        platform_name = 'input_select'
                        platform_type = EmsBusInputSelect
                    else:
                        # Other integer values (%, bar, ...)
                        platform_name = 'input_number'
                        platform_type = EmsBusInputNumber
            if platform_name is None:
                # Read-only field or no write entity configured
#                if issubclass(field_obj.__class__, BooleanField) or \
#                   issubclass(field_obj.__class__, BooleanIntegerField):
#                    # Boolean types -> Binary sensor
#                    platform_name = 'binary_sensor'
#                    platform_type = EmsBusBinarySensor
#                else:
                # Create a read only sensor
                platform_name = 'sensor'
                platform_type = EmsBusSensor

            unique_id = f'{DOMAIN}_{device.address:02x}_' \
                        f'{message.Meta.identification:02x}_{field_name}'
            if not unique_id in hass.data[DATA_DEVICES]:
                #LOGGER.debug('Adding new entity %s', unique_id)
                #entity_id_format = platform_name + '.{}'
                # It's uncommon to create the entity ID here, but here is the best place
                #entity_id = async_generate_entity_id(entity_id_format, unique_id, hass=hass)
                entity_id = f'{platform_name}.{unique_id}'
                LOGGER.debug('Setting up %s', entity_id)
                platform = platform_type(entity_id, device, message, field_name, field_obj)
                # See comment below
                if platform_name.startswith('input_'):
                    # The Input* component only read from the yaml config.
                    # Also, the setup_platform of input_select is not called.
                    # So run it manually in the component.
                    component = hass.data[DATA_ENTITY_PLATFORM][platform_name][0]
                    await component.async_add_entities([platform])
                else:
                    async_dispatcher_send(hass, f'{DOMAIN}_new_{platform_name}', platform)
                hass.data[DATA_DEVICES][unique_id] = platform
            # Dispatch update event for updated fields
            if field_obj in affected_fields:
                async_dispatcher_send(hass, unique_id)
            #hass.data[DATA_DEVICES][unique_id].async_schedule_update_ha_state()

    hass.data[DATA_DEVICES] = {}
    protocol = hass.data[DATA_PROTOCOL] = EmsProtocol(
        serial_path, log_level, DEFAULT_CLIENT_ID, event_handler, hass)

    async def start_emsbus(_event):
        LOGGER.info('Starting the EMS bus...')
        await protocol.start()

    async def stop_emsbus(_event):
        LOGGER.info('Stopping the EMS bus...')
        await protocol.stop()

    def stats(_):
        '''Log statistics'''
        for key, value in protocol.stats().items():
            LOGGER.info('%20s %s', key, value)
    hass.services.async_register(DOMAIN, SERVICE_STATS, stats)


    # https://developers.home-assistant.io/docs/creating_component_generic_discovery/
    # Load platforms. We're not using config entries right now.
    for plat in PLATFORMS:
        hass.async_create_task(
            discovery.async_load_platform(hass, plat, DOMAIN, {}, config)
        )

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, start_emsbus)
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, stop_emsbus)

    return(True)
