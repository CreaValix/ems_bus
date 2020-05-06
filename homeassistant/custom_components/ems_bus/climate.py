'''EMS bus climate controls'''

import logging

from homeassistant.components.climate import ClimateDevice, SUPPORT_TARGET_TEMPERATURE, \
                                             TEMP_CELSIUS, HVAC_MODE_OFF
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN
from .entity import EmsBusEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config_entry, async_add_entities, discovery_info=None):
    '''Set up EMS bus climate properties'''

    @callback
    def async_add_climate(climate):
        '''Add an EMS bus climate property'''
        async_add_entities([climate], False)
        #_LOGGER.debug('Added new climate %s / %s', climate.entity_id, climate.unique_id)

    async_dispatcher_connect(hass, f'{DOMAIN}_new_climate', async_add_climate)


class EmsBusClimate(EmsBusEntity, ClimateDevice):
    '''EMS bus climate devices'''

    @property
    def temperature_unit(self):
        return(TEMP_CELSIUS)

    @property
    def current_temperature(self):
        return(self._field.value)

    def set_temperature(self, **kwargs):
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        self._message.field_set_send(self._field_name, temp)

    @property
    def target_temperature(self):
        return(self._field.value)

    @property
    def supported_features(self):
        return(SUPPORT_TARGET_TEMPERATURE)

    @property
    def precision(self):
        return(1 if self._field.factor is None else 1 / self._field.factor)

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        try:
            return(self._field.unit.RANGE[0])
        except (AttributeError, IndexError):
            return(0)

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        try:
            return(self._field.unit.RANGE[1])
        except (AttributeError, IndexError):
            return(80)

    # It seems that we need to overwrite the static methods. If now, we get a TypeError:
    # Can't instantiate abstract class EmsBusClimate with abstract methods hvac_mode, hvac_modes
    @property
    def hvac_mode(self):
        return(HVAC_MODE_OFF)

    @property
    def hvac_modes(self):
        return[(HVAC_MODE_OFF)]
