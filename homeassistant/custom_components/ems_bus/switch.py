'''EMS bus switches'''

import logging

from homeassistant.components.switch import SwitchDevice
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN
from .entity import EmsBusEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config_entry, async_add_entities, discovery_info=None):
    '''Set up EMS bus switch properties'''

    @callback
    def async_add_switch(switch):
        '''Add an EMS bus switch property'''
        async_add_entities([switch], True)
        #_LOGGER.debug('Added new switch %s / %s', switch.entity_id, switch.unique_id)

    async_dispatcher_connect(hass, f'{DOMAIN}_new_switch', async_add_switch)


class EmsBusSwitch(EmsBusEntity, SwitchDevice):
    '''Representation of a EMS bus switch property'''

    # Todo: make async
    def turn_on(self, **kwargs):
        '''Turn the property on'''
        self._message.field_set_send(self._field_name, True)

    # Todo: make async
    def turn_off(self, **kwargs):
        '''Turn the property off.'''
        self._message.field_set_send(self._field_name, False)
