'''Platform for sensor integration.'''

import logging

from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN
from .entity import EmsBusEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config_entry, async_add_entities, discovery_info=None):
    '''Set up EMS bus sensor properties'''

    @callback
    def async_add_sensor(sensor):
        '''Add an EMS bus sensor property'''
        async_add_entities([sensor], True)
        #_LOGGER.debug('Added new sensor %s / %s', sensor.entity_id, sensor.unique_id)

    async_dispatcher_connect(hass, f'{DOMAIN}_new_sensor', async_add_sensor)


class EmsBusSensor(EmsBusEntity, Entity):
    '''Representation of a Sensor.'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._unit = None if self._field.unit is None else self._field.unit(self._field.value)

    @property
    def state(self):
        '''Return the state of the sensor.'''
        if self._unit is None:
            return(self._field.value)
        self._unit.update(self._field.value)
        return(self._unit.value)

    @property
    def unit_of_measurement(self):
        '''Return the unit of measurement the value is expressed in.'''
        return(None if self._unit is None else self._unit.sign)

    @callback
    def update_callback(self):
        """Get new data and update state."""
        #_LOGGER.debug('async_schedule_update_ha_state %s', self.unique_id)
        self.async_schedule_update_ha_state(False)
