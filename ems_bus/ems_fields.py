'''
Message field definitions for the EMS bus
'''

from datetime import datetime, date

from ems_bus.ems_units import UnitDate, UnitDateTime


import logging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class Field():
    ''' Field abstract class '''
    MIN_LENGTH = 1
    MAX_LENGTH = 4
    value = None

    def __init__(self, pos, length, name, unit=None):
        if length < self.MIN_LENGTH or length > self.MAX_LENGTH:
            raise(ValueError(f'Invalid length {length} for {__name__}'))
        self.pos = pos
        self.length = length
        self.name = name
        self.unit = unit

    def __str__(self):
        if self.unit is None:
            val = str(self.value)
        else:
            val = str(self.unit(self.value))
        return(f'{self.name:40}: {val}')

    def update(self, value):
        ''' Update the value '''
        self.value = value

    def to_bytes(self, _):
        ''' Returns a bytes object of this field '''
        raise(Exception('Must be overridden'))

    def has_changed(self, update, offset, message):
        if self.value is None:
            return(True)
        # Start and end of the field in the update
        update_start = self.pos - offset
        update_end = update_start + self.length
        #assert 0 <= update_start < update_end <= len(update)
        end = self.pos + self.length
        return(update[update_start:update_end] != message[self.pos:end])


class DateField(Field):
    ''' Date field '''
    MIN_LENGTH = 3
    MAX_LENGTH = 3

    def __init__(self, pos, length, name):
        super().__init__(pos, length, name, UnitDate)

    def parse(self, update):
        data = update[self.pos:self.pos + self.length]
        self.value = date(data[2] + 2000, data[1], data[0])

    def to_bytes(self, _):
        data = bytearray(self.length)
        data[0] = self.value.day
        data[1] = self.value.month
        data[2] = self.value.year - 2000
        return(data)


class DateTimeField(Field):
    ''' Date and time field '''
    MIN_LENGTH = 5
    MAX_LENGTH = 6

    def __init__(self, pos, length, name):
        super().__init__(pos, length, name, UnitDateTime)

    def parse(self, update):
        data = update[self.pos:self.pos + self.length]
        tzinfo = datetime.now().astimezone().tzinfo
        second = data[5] if self.length == 6 else 0
        # Todo: Understand what bit 7 of year means. Source:
        # https://emswiki.thefischer.net/doku.php?id=wiki:ems:telegramme#ubaerrormessages1
        self.value = \
            datetime((data[0] & 0x7F) + 2000, data[1], data[3], data[2], data[4], second, 0, tzinfo)

    def to_bytes(self, _):
        data = bytearray(self.length)
        data[0] = self.value.year - 2000
        data[1] = self.value.month
        data[2] = self.value.hour
        data[3] = self.value.day
        data[4] = self.value.minute
        if self.length == 6:
            data[5] = self.value.second
        return(data)


class IntegerField(Field):
    ''' Integer field '''
    def __init__(self, pos, length, name, unit=None, factor=None, signed=False):
        super().__init__(pos, length, name, unit)
        self.factor = factor
        self.signed = signed

    def parse(self, update):
        self.value = \
            int.from_bytes(update[self.pos:self.pos + self.length], 'big', signed=self.signed)
        if self.factor is not None:
            self.value /= self.factor

    def to_bytes(self, _):
        factor = 1 if self.factor is None else self.factor
        return(int(self.value * factor).to_bytes(self.length, 'big', signed=self.signed))


class BooleanField(Field):
    ''' Boolean field '''
    MAX_LENGTH = 1

    def __init__(self, pos, length, name, unit=None, bit=None):
        super().__init__(pos, length, name, unit)
        if bit is None:
            raise(ValueError('{}: Bit must be specied'.format(__name__)))
        self.bit = bit

    def parse(self, update):
        self.value = bool(update[self.pos] & (1 << self.bit))

    def has_changed(self, update, offset, message):
        if self.value is None:
            return(True)
        mask = 1 << self.bit
        return(update[self.pos - offset] & mask != message[self.pos] & mask)

    def to_bytes(self, msg_obj):
        # We need to set the bits of other booleans on the same byte, not touching undefined bits.
        value = msg_obj[self.pos]
        for field in dir(self):
            f_obj = getattr(self, field)
            if not issubclass(f_obj.__class__, Field) or f_obj.pos != self.pos:
                continue
            # Overlapping fields MUST be boolean
            if not issubclass(f_obj.__class__, BooleanField):
                raise(Exception('Overlapping fields must be boolean'))
            value = f_obj.modify_byte(value)
        return(value.to_bytes(1, 'big', signed=False))

    def modify_byte(self, value):
        ''' Sets the value in the bit of a byte '''
        return((value & ~(1 << self.bit)) | (int(self.value) << self.bit))


class BooleanIntegerField(Field):
    MAX_LENGTH = 1

    def __init__(self, pos, length, name, unit=None, onvalue=0xff, **kw):
        super().__init__(pos, length, name, unit)
        self.onvalue = onvalue

    def parse(self, update):
        self.value = update[self.pos] == self.onvalue

    def to_bytes(self, _):
        value = self.onvalue if self.value else 0x00
        return(value.to_bytes(1, 'big', signed=False))


class StringField(Field):
    '''' String field '''
    MAX_LENGTH = 8
    ENCODING = 'ISO8859-15' # Is assumed

    def parse(self, update):
        self.value = update[self.pos:self.pos + self.length].decode(self.ENCODING)

    def to_bytes(self, _):
        value = self.value.encode(self.ENCODING)
        if len(value) != self.length:
            return(None)
        return(value)
