from homeassistant.helpers.entity import Entity
from .const import DOMAIN

class EmsBusDevice(Entity):
    '''Representation of a EMS bus device'''
    # Todo: Deactivate device

    def __init__(self, device_id, product, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._product = product
        # todo, update from 0x02
        self._version = ''
        self._unique_id = f'{DOMAIN}.device_{device_id:02x}'

    @property
    def unique_id(self):
        """Return unique ID of EMS bus device."""
        return(self._unique_id)

#    @property
#    def device_info(self):
#        """Return device information."""
#        #identifier, name = node_device_id_and_name(self.node)
#        return({
#            'identifiers': {(DOMAIN, self._unique_id)},
#            'name': self.name,
#            'manufacturer': '',
#            'model': self._product[2],
#            'sw_version': self._version,
#            #'via_device': (DOMAIN, )
#           })

    @property
    def state(self):
        '''Return the state.'''
        return('ready')

    @property
    def should_poll(self):
        """No polling needed."""
        return(False)

    @property
    def name(self):
        """Return the name of the device."""
        return(self._product[2])
