import logging

from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN
from ems_bus.ems_fields import BooleanField, BooleanIntegerField

_LOGGER = logging.getLogger(__name__)

class EmsBusEntity:
    def __init__(self, entity_id, device, message, field_name, field):
        '''Initialize the EMS bus entity'''
        self._devinfo = device
        self._message = message
        self._field_name = field_name
        self._field = field
        self._unique_id = f'{DOMAIN}_{self._devinfo.address:02x}_{self._message.Meta.identification:02x}_{self._field_name}'
        # Pre-set the entity ID. It will be modified by async_add_entities.
        self.entity_id = entity_id

    async def async_added_to_hass(self):
        """Connect to update callbacks"""
        await super().async_added_to_hass()
        async def updated():
            self.async_schedule_update_ha_state(False)
        async_dispatcher_connect(self.hass, self._unique_id, updated)
        _LOGGER.debug('Added %s', self.entity_id)

    @property
    def is_on(self):
        '''Return if the entity is on'''
        if isinstance(self._field, (BooleanField, BooleanIntegerField)):
            return(bool(self._field.value))
        return(None)

    @property
    def unique_id(self):
        return(self._unique_id)

    @property
    def device_info(self):
        return({
            'name': self._devinfo.product[2],
            'identifiers': {(DOMAIN, f'{DOMAIN}_{self._devinfo.address:02x}')},
            #'manufacturer': '',
            'model': self._devinfo.product[2],
            #'via_devinfo': (DOMAIN, f'{DOMAIN}_{self._devinfo.address:02x}')
        })

    @property
    def should_poll(self):
        return(False)

    @property
    def name(self):
        return(self._field.name)

    @property
    def assumed_state(self):
        return(False)

    @property
    def available(self):
        return(True)

#    @property
#    def hass(self):
#        return(self._hass)

#    def async_update(self):
#        pass

#    @property
#    def device_id(self):
#        return self.unique_id
