'''EMS protocol driver'''

import asyncio
import concurrent.futures
import logging
import sys

import posix_ipc

from ems_bus.ems_defines import EMS_MAX_TELEGRAM_LENGTH
from ems_bus import ems_messages, ems_serio
from ems_bus.ems_devices import \
    EMS_DEVICES, EMS_DEVICE_TYPE_NAMES, EMS_INITIAL_REQUESTS, EMS_DEVICE_FLAG_NO_WRITE

LOGGER = logging.getLogger(__name__)

EMS_MSG_USAGES = ['BROADCAST', 'REQUEST', 'WRITE', 'RESPONSE', 'INVALID']

class EmsProtocol():
    run = False
    _rx_queue = None
    _tx_queue = None

    def __init__(self, serial_path, log_level, client_id, event_handler=None, hass=None):
        self.online_devices = bytes(ems_messages.UbaDevicesMessage.Meta.length)
        self.known_devices = {}
        self._serial_path = serial_path
        self._log_level = log_level
        self.client_id = client_id
        self.event_handler = event_handler
        self.hass = hass
        # Generate list of messages
        self.msg_dict = {obj.Meta.identification: obj for obj in ems_messages.__dict__.values() \
                         if isinstance(obj, type) and issubclass(obj, ems_messages.Message)}

    def create_task(self, task):
        '''Runs a task in background. Uses home assistant if given.'''
        if self.hass:
            created = self.hass.async_create_task(task)
        else:
            created = asyncio.create_task(task)
            #loop = asyncio.get_event_loop()
            #loop.create_task(task)
            #executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            #def run_task():
            #    asyncio.run(task())
            #await loop.run_in_executor(executor, run_task)
        return(created)

    async def start(self):
        '''Start the serial bus driver'''
        ret = ems_serio.loglevel(self._log_level)
        LOGGER.debug('ems_serio log level is %d', ret)
        ret = ems_serio.start(self._serial_path)
        if ret != 0:
            LOGGER.error('ems_serio.start(%s) failed: %d', self._serial_path, ret)
            return(None)
        self.run = True
        return(self.create_task(self.recv()))


    async def recv(self):
        LOGGER.debug('Entering RX loop')
        # Todo: Open in a loop, each 1 s, recover if lost
        self._rx_queue = None
        self._tx_queue = None
        tries = 0

        while self._rx_queue is None or self._tx_queue is None:
            try:
                self._rx_queue = \
                    posix_ipc.MessageQueue('/ems_bus_rx', 0, 0o666, 10, 32, True, False)
                LOGGER.debug('Connected to RX queue')
            except:
                pass
            try:
                self._tx_queue = \
                    posix_ipc.MessageQueue('/ems_bus_tx', 0, 0o666, 10, 32, False, True)
                LOGGER.debug('Connected to TX queue')
            except:
                pass
            if self._rx_queue is None or self._tx_queue is None:
                await asyncio.sleep(1)
            tries += 1

        # If we could connect immediately and the queue was full, assume that the bus driver
        # was running for a long time. Clear the queue and schedule a device query to the boiler.
        if tries == 1 and self._rx_queue.current_messages == self._rx_queue.max_messages:
            LOGGER.debug('Clearing RX queue')
            self._rx_queue.block = False
            while self._rx_queue.current_messages:
                self._rx_queue.receive()
            self._rx_queue.block = True

            LOGGER.debug('Querying device list from boiler')
            self.create_task(self.read_request(0x08, ems_messages.UbaDevicesMessage))
        del(tries)

        while self.run:
            try:
                # Posix message queue is blocking, run in a separate executor.
                if self.hass:
                    message = (await self.hass.async_add_executor_job(self._rx_queue.receive))[0]
                else:
                    loop = asyncio.get_running_loop()
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        message = (await loop.run_in_executor(pool, self._rx_queue.receive))[0]
            except Exception as e:
                LOGGER.error(e)
                continue

            #LOGGER.debug('Got msg: %s', message.hex())
            if len(message) < 6:
                continue
            src = message[0]
            dst = message[1]
            if message[1] == 0:
                usage = 0
            else:
                #if src == self.bus.polled_id:
                #    if dst & 0x80:
                #        usage = 1
                #    else:
                #        usage = 2
                #elif dst == self.bus.polled_id:
                #    usage = 3
                #else:
                #    usage = 4
                usage = 3
            LOGGER.debug(
                '%9s 0x%02x -> 0x%02x t 0x%02x, o %i: %s',
                EMS_MSG_USAGES[usage], src, dst & 0x7f, message[2], message[3], message.hex())

            if usage in (0, 3):
                self.create_task(self.parse_message(message))

    async def parse_message(self, message):
        ''' Parses in incoming message '''
        src = message[0]
        dst = message[1]
        msgtype = message[2]
        offset = message[3]

        #LOGGER.error('Got msg : %s', message.hex())
#        if self.sent == 0:
#            self.sent += 1
#            self.read_request(8, self.msg_dict[0x33])

        data = message[4:-1]
        try:
            message_type = self.msg_dict[msgtype]
        except KeyError:
            LOGGER.error('Unknown message %02x from %02x to %02x', msgtype, src, dst)
            return
        if src in self.known_devices:
            entry = self.known_devices[src]
            if entry.product is None:
                # No definition means that the device is known but the product is unknown.
                return
            try:
                msg_obj = entry.messages[msgtype]
            except KeyError:
                msg_obj = message_type(src, self)
                entry.messages[msgtype] = msg_obj
        else:
            msg_obj = message_type(src, self)
        try:
            updated_fields = msg_obj.parse(data, offset)
        except ValueError as e:
            LOGGER.error(e)
            return
        #msg_obj.dump()

        # We always parse 0x07 and 0x02, even from unknown devices
        if msg_obj.Meta.identification == 0x07 and self.online_devices != data:
            # We got a changed online devices list.
            LOGGER.debug('Device info changed: %s -> %s', self.online_devices.hex(), data.hex())
            for num_byte in range(8):
                for num_bit in range(8):
                    old_state = self.online_devices[num_byte] & (1 << num_bit)
                    new_state = data[num_byte] & (1 << num_bit)
                    if old_state == new_state:
                        continue
                    dev_num = (num_byte + 1) * 8 + num_bit
                    if old_state == 0x00:
                        LOGGER.info('Device %02d came online. Requesting version.', dev_num)
                        if dev_num != self.client_id:
                            self.create_task(self.read_request(dev_num,
                                                               ems_messages.VersionMessage))
                    else:
                        LOGGER.info('Device %02d went offline. Removing.', dev_num)
                        if dev_num in self.known_devices:
                            del(self.known_devices[dev_num])
            self.online_devices = data
        elif msgtype == 0x02 and src not in self.known_devices:
            # Received version info from a device. Update the internal table.
            product_id = msg_obj.product_id.value
            product = next((i for i in EMS_DEVICES if i[0] == product_id), None)
            if product is None:
                LOGGER.error('Found unknown device with product ID %02x', product_id)
                return
            LOGGER.info('Found a %s at 0x%02x: ID %d, a %s v%d.%d',
                        EMS_DEVICE_TYPE_NAMES[product[1]], src, product[1], product[2],
                        msg_obj.ver_major.value, msg_obj.ver_minor.value)

            # Read some initial parameters
            if product[1] in EMS_INITIAL_REQUESTS:
                for request in EMS_INITIAL_REQUESTS[product[1]]:
                    self.create_task(self.read_request(src, request))

            # Add to internal list and call back user event handler
            dev_entry = EmsDevice(src, product, {msgtype: msg_obj})
            self.known_devices[src] = dev_entry
            await self.event_handler(0, dev_entry, msg_obj, updated_fields)
            #await self.event_handler(1, self.known_devices[src], msg_obj)
        elif src in self.known_devices and updated_fields is not None:
            await self.event_handler(1, self.known_devices[src], msg_obj, updated_fields)


    async def read_request(self, dst, msgtype):
        ''' Generates a read request of this message '''
        msg_id = msgtype.Meta.identification
        LOGGER.info('Reading message 0x%02x from 0x%02x', msg_id, dst)
        data = bytearray(6)
        data[0] = self.client_id
        data[1] = dst | 0x80
        data[2] = msg_id
        data[3] = 0x00 # Offset 0
        data[4] = EMS_MAX_TELEGRAM_LENGTH
        if self.hass:
            await self.hass.async_add_executor_job(self._tx_queue.send, data)
        else:
            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                await loop.run_in_executor(executor, self._tx_queue.send, data)

    def device_set_value(self, dev_id, message_type, field, value):
        ''' Updates and sends an updated value of a field of a message of a device '''
        try:
            dev_entry = self.known_devices[dev_id]
        except:
            raise(ValueError(f'Device {dev_id} is not online'))
        product = dev_entry.product
        if product[3] & EMS_DEVICE_FLAG_NO_WRITE:
            raise(ValueError(f'Write not allowed for product {product[1]} - {product[2]}'))
        message = dev_entry.messages[message_type.Meta.identification]
        message.field_set_send(field, value)

    async def stop(self):
        ''' Set a stop condition for the EMS bus'''
        self.run = False
        ems_serio.stop()

    def stats(self):
        return(ems_serio.stats())

class EmsDevice:
    def __init__(self, address, product, messages):
        # Address on the EMS bus
        self.address = address
        # Product definition (an entry of EMS_DEVICES in ems_devices.py)
        self.product = product
        # Known messages for this device
        self.messages = messages
