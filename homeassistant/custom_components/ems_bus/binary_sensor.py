'''EMS bus binary sensor controls'''
import logging

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.components.binary_sensor import BinarySensorDevice, DEVICE_CLASS_OPENING

#from .ems_units import UnitOnOff, UnitYesNo, UnitOpenClosed
from .entity import EmsBusEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config_entry, async_add_entities, discovery_info=None):
    '''Set up EMS bus binary sensor properties'''

    @callback
    def async_add_binary_sensor(binary_sensor):
        '''Add an EMS bus binary sensor property'''
        async_add_entities([binary_sensor], False)

    async_dispatcher_connect(hass, f'{DOMAIN}_new_binary_sensor', async_add_binary_sensor)


class EmsBusBinarySensor(EmsBusEntity, BinarySensorDevice):
    '''EMS bus binary sensor devices'''

    @property
    def is_on(self):
        return(bool(self._field.value))

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return(DEVICE_CLASS_OPENING)
