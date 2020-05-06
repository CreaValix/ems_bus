'''EMS bus input_number controls'''

import logging

from homeassistant.components.input_number import \
    InputNumber, CONF_INITIAL, CONF_ID, CONF_MIN, CONF_MAX, CONF_NAME, CONF_ICON, CONF_STEP, \
    ATTR_UNIT_OF_MEASUREMENT, CONF_MODE, MODE_SLIDER
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN
from .entity import EmsBusEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config_entry, async_add_entities, discovery_info=None):
    '''Set up EMS bus input number properties'''

    @callback
    def async_add_input_number(input_number):
        '''Add an EMS bus input_number property'''
        async_add_entities([input_number], False)

    async_dispatcher_connect(hass, f'{DOMAIN}_new_input_number', async_add_input_number)


class EmsBusInputNumber(EmsBusEntity, InputNumber):
    '''EMS bus input number devices'''
    def __init__(self, entity_id, device, message, field_name, field):
        EmsBusEntity.__init__(self, entity_id, device, message, field_name, field)
        try:
            between = field.unit.RANGE
        except AttributeError:
            between = (0, 100)

        config = {
            CONF_INITIAL: self._field.value,
            CONF_ID: entity_id,
            CONF_MIN: between[0],
            CONF_MAX: between[1],
            CONF_NAME: field_name,
            CONF_ICON: None,
            CONF_STEP: 1,
            ATTR_UNIT_OF_MEASUREMENT: field.unit(0).sign if field.unit else '',
            CONF_MODE: MODE_SLIDER,
        }
        _LOGGER.debug('config=%s', config)
        InputNumber.__init__(self, config)

    @property
    def state(self):
        """Return the state of the component."""
        return self._field.value

    async def async_set_value(self, value):
        """Set new value."""
        super().async_set_value(value)
        self._message.field_set_send(self._field_name, value)
