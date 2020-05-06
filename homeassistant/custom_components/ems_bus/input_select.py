'''EMS bus input_select controls'''

import logging

from homeassistant.components.input_select import InputSelect, CONF_INITIAL, CONF_OPTIONS, CONF_ID
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN
from .entity import EmsBusEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config_entry, async_add_entities, discovery_info=None):
    '''Set up EMS bus input select properties'''

    @callback
    def async_add_input_select(input_select):
        '''Add an EMS bus input_select property'''
        async_add_entities([input_select], False)

    async_dispatcher_connect(hass, f'{DOMAIN}_new_input_select', async_add_input_select)


class EmsBusInputSelect(EmsBusEntity, InputSelect):
    '''EMS bus input select devices'''
    def __init__(self, entity_id, device, message, field_name, field):
        EmsBusEntity.__init__(self, entity_id, device, message, field_name, field)
        # Get the config options from the field
        try:
            options = self._field.unit.VALUES
        except AttributeError:
            options = ()

        config = {
            CONF_INITIAL: options[self._field.value],
            CONF_OPTIONS: options,
            CONF_ID: entity_id
        }
        InputSelect.__init__(self, config)

    @callback
    def async_select_option(self, option, from_bus=False):
        '''Select a new option.
        Overwrite the internal method because it can be called from the frontend or the bus'''
        super().async_select_option(option)
        if not from_bus:
            # Update the bus value
            value = self._options.index(option)
            _LOGGER.debug('value=%s', value)
            self._message.field_set_send(self._field_name, value)

    @property
    def state(self):
        """Return the state of the component."""
        return self._options[self._field.value]
