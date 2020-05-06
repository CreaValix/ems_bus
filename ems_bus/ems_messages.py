'''
Message definitions for the EMS bus
'''

import logging

from ems_bus.ems_units import \
    UnitMinute, UnitYesNo, UnitOpenClosed, UnitOnOff, UnitCelsius, UnitPercent, UnitMicroAmpere, \
    UnitBar, UnitLiterPerMin, UnitDwLoading, UnitDwMode, UnitDwType, UnitDevice, \
    UnitHcInstallation, UnitHcWorkMode, UnitHcRemote, UnitHcOperation, UnitUbaMsTimestamp, \
    UnitHour, UnitWeekDay, UnitUbaMmNeed, UnitUbaFtValve, UnitHwDcProgram, UnitOffOnAuto
from ems_bus.ems_fields import Field, DateTimeField, IntegerField, BooleanField, StringField, \
                        BooleanIntegerField, DateField

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class Message:
    message = None

    def __init__(self, dev_id, proto):
        self.device_id = dev_id
        self.proto = proto
        self.message = bytearray(self.Meta.length)

    class Meta:
        identification = 0x00
        length = 0

    def get_fields(self):
        for field_name in dir(self):
            field_obj = getattr(self, field_name)
            if issubclass(field_obj.__class__, Field):
                yield (field_name, field_obj)

    def parse(self, update, offset):
        if offset < 0:
            LOGGER.error('Offset %d must be positive', offset)
            return
        if len(update) + offset > self.Meta.length:
            LOGGER.error('Offset %d + length %d is greater than message length %d',
                         offset, len(update), self.Meta.length)
            return

        # Check what fields have changed, merge data and mark updated fields.
        changed_fields = []
        update_end = offset + len(update)
        for field_name, field in self.get_fields():
            if field.pos < offset or field.pos >= update_end:
                continue
            # Check field in range
            field_end = field.pos + field.length
            if field_end > update_end:
                LOGGER.error('Update message 0x%02d range [%d-%d] not covering whole field %s',
                             self.Meta.identification, offset, update_end, field_name)
                continue
            if field.has_changed(update, offset, self.message) and field not in changed_fields:
                changed_fields.append(field)

        # Merge data
        self.message[offset:update_end] = update

        # Update marked fields after data was merged.
        for field in changed_fields:
            field.parse(self.message)

        return(changed_fields)


    def field_set_send(self, field, value):
        ''' Update a field and send the update to the device '''
        field_obj = getattr(self, field)
        field_obj.update(value)
        update_data = field_obj.to_bytes(self)
        data = bytearray(5 + len(update_data)) # 1 byte per src, dst, type, offset, crc
        data[0] = self.proto.client_id
        data[1] = self.device_id
        data[2] = self.Meta.identification
        data[3] = field_obj.pos
        data[4:4 + field_obj.length] = update_data
        #self.proto.bus.send(data)
        self.proto._tx_queue.send(data)

    def dump(self):
        ''' Print the values of the message to the logger '''
        for field in dir(self):
            field_obj = getattr(self, field)
            if issubclass(field_obj.__class__, Field):
                LOGGER.debug(str(field_obj))



class VersionMessage(Message):
    class Meta:
        identification = 0x02
        length = 3

    product_id = IntegerField(0, 1, 'Product ID')
    ver_major = IntegerField(1, 1, 'Version Major')
    ver_minor = IntegerField(2, 1, 'Version Minor')

class RCTimeMessage(Message):
    class Meta:
        identification = 0x06
        length = 8

    time = DateTimeField(0, 6, 'Time')
    dow = IntegerField(6, 1, 'Day of week')
    dst = BooleanField(7, 1, 'Daylight saving', None, 0)
    radio = BooleanField(7, 1, 'Radio clock', None, 1)
    bad_time = BooleanField(7, 1, 'Time incorrect', None, 2)
    bad_date = BooleanField(7, 1, 'Date incorrect', None, 3)
    enabled = BooleanField(7, 1, 'Clock enabled', None, 4)

class UbaDevicesMessage(Message):
    class Meta:
        identification = 0x07
        length = 13
    def __init__(self, dev_id, proto, *args, **kwargs):
        super().__init__(dev_id, proto, *args, **kwargs)
        for num_byte in range(8):
            for num_bit in range(8):
                num_str = '{:02d}'.format((num_byte + 1) * 8 + num_bit)
                setattr(self, 'device_' + num_str,
                        BooleanField(num_byte, 1, 'Device ' + num_str, UnitDevice, num_bit))


class ErrorMessage(Message):
    display = StringField(0, 2, 'Display code')
    code = IntegerField(2, 2, 'Error code')
    timestamp = DateTimeField(4, 5, 'Time stamp')
    duration = IntegerField(9, 2, 'Duration', UnitMinute)
    source = IntegerField(11, 1, 'Source bus address')
class UbaError1Message(ErrorMessage):
    class Meta:
        identification = 0x10
        length = 96
class UbaError2Message(ErrorMessage):
    class Meta:
        identification = 0x11
        length = 96
class RcErrorMessages(ErrorMessage):
    class Meta:
        identification = 0x12
        length = 96
class RcResetErrorMessages(ErrorMessage):
    class Meta:
        identification = 0x13
        length = 96


class UbaOperationTime(Message):
    class Meta:
        identification = 0x14
        length = 3

    duration = IntegerField(0, 3, 'Operation duration', UnitMinute)

# Todo
class UbaMaintenanceSettings(Message):
    class Meta:
        identification = 0x15
        length = 5

    timstamp_unit = IntegerField(0, 1, 'Maintenance log timestamp unit', UnitUbaMsTimestamp)
    remaining_time = IntegerField(1, 1, 'Remaining time to next maintenance', UnitHour, 0.01)
    next_maintenance = DateField(2, 3, 'Date of next maintenance')


class UbaSettings(Message):
    class Meta:
        identification = 0x16
        length = 11

    boiler_heating = BooleanIntegerField(0, 1, 'Boiler heating activated', UnitOnOff, 0xff)
    boiler_temp = IntegerField(1, 1, 'Boiler heating temperature', UnitCelsius, None, True)
    boiler_max = IntegerField(2, 1, 'Maximum boiler power', UnitPercent)
    boiler_min = IntegerField(3, 1, 'Minimum boiler power', UnitPercent)
    stop_hysteresis = IntegerField(4, 1, 'Stop hysteresis', UnitCelsius, None, True)
    start_hysteresis = IntegerField(5, 1, 'Start hysteresis', UnitCelsius, None, True)
    anti_swing_time = IntegerField(6, 1, 'Anti-swinging time', UnitMinute)
    follow_up_time = IntegerField(8, 1, 'Boiler stop follow up time', UnitMinute)
    pump_max = IntegerField(9, 1, 'Heat circuit pump maximum power', UnitPercent)
    pump_min = IntegerField(10, 1, 'Heat circuit pump minimum power', UnitPercent)


class UbaMonitorFast(Message):
    class Meta:
        identification = 0x18
        length = 25

    forward_temp_set = IntegerField(0, 1, 'Set forward flow temperature', UnitCelsius, None, True)
    forward_temp = IntegerField(1, 2, 'Current forward flow temperature', UnitCelsius, 10, True)
    burner_power_max = IntegerField(3, 1, 'Maximum burner power', UnitPercent)
    burner_power = IntegerField(4, 1, 'Current burner power', UnitPercent)
    # 2 bytes missing
    valve1 = BooleanField(7, 1, 'Gas valve 1', UnitOpenClosed, 0)
    valve2 = BooleanField(7, 1, 'Gas valve 2', UnitOpenClosed, 1)
    fan = BooleanField(7, 1, 'Fan', UnitOnOff, 2)
    ignition = BooleanField(7, 1, 'Ignition', UnitOnOff, 3)
    boiler_pump = BooleanField(7, 1, 'Boiler pump', UnitOnOff, 4)
    drinkwater_valve = BooleanField(7, 1, 'Drink water valve', UnitOpenClosed, 5)
    drinkwater_pump = BooleanField(7, 1, 'Drink water circulation pump', UnitOnOff, 6)
    # 1 byte missing
    boiler_temp = IntegerField(9, 2, 'Boiler temperature', UnitCelsius, 10, True)
    drinkwater_temp = IntegerField(11, 2, 'Drink water temperature', UnitCelsius, 10, True)
    return_current = IntegerField(13, 2, 'Current return flow temperature', UnitCelsius, 10, True)
    flame_power = IntegerField(15, 2, 'Flame current', UnitMicroAmpere, 10)
    pressure = IntegerField(17, 1, 'System pressure', UnitBar, 10)
    service_code = StringField(18, 2, 'Service code')
    error_code = IntegerField(20, 2, 'Error code')
    intake_temp = IntegerField(23, 2, 'Intake temperature', UnitCelsius, 10, True)
    # 1 byte missing


class UbaMonitorSlow(Message):
    class Meta:
        identification = 0x19
        length = 25

    outside_temp = IntegerField(0, 2, 'Outside temperature', UnitCelsius, 10, True)
    boiler_temp = IntegerField(2, 2, 'Boiler temperature', UnitCelsius, 10, True)
    exhaust_temp = IntegerField(4, 2, 'Exhaust temperature', UnitCelsius, 10, True)
    # 3 bytes missing
    pump_power = IntegerField(9, 1, 'Pump power', UnitPercent)
    burner_starts = IntegerField(10, 3, 'Burner starts')
    burner_total = IntegerField(13, 3, 'Burner total operation time', UnitMinute)
    burner_stage2 = IntegerField(16, 3, 'Burner time in stage 2', UnitMinute)
    burner_heat = IntegerField(19, 3, 'Burner time heating', UnitMinute)
    burner_drinkwater = IntegerField(22, 3, 'Burner time heating drink water', UnitMinute)


class UbaSetValuesMessage(Message):
    class Meta:
        identification = 0x1a
        length = 4
        write = True

    boiler_temp = IntegerField(0, 1, 'Boiler set temperature', UnitCelsius, None, True)
    heat_power = IntegerField(1, 1, 'Heat circuit power', UnitPercent)
    drinkwater_power = IntegerField(2, 1, 'Requested drink water power', UnitPercent)
    # 1 byte missing


class UbaMaintenanceMessage(Message):
    class Meta:
        identification = 0x1c
        length = 1

    need_maintenance = IntegerField(0, 1, 'Maintenance neccessary', UnitUbaMmNeed)


class UbaFunctionTest(Message):
    class Meta:
        identification = 0x1d
        length = 11

    test_on = BooleanIntegerField(0, 1, 'Test mode activated', UnitOnOff, 0x5a)
    burner_power = IntegerField(1, 1, 'Burner power', UnitPercent)
    # 1 byte missing
    boiler_power = IntegerField(3, 1, 'Boiler power', UnitPercent)
    valve = IntegerField(4, 1, '3-way-valve setting', UnitUbaFtValve)
    pump_on = BooleanIntegerField(5, 1, 'Heat circuit pump', UnitOnOff, 0xff)
    # 5 byte missing


class UbaDrinkwaterParameterMessage(Message):
    class Meta:
        identification = 0x33
        length = 11
        write = True

    installed = BooleanField(0, 1, 'Drink water system installed', UnitYesNo, 3)
    activated = BooleanIntegerField(1, 1, 'Drink water system activated', UnitYesNo, 0xff)
    set_temp = IntegerField(2, 1, 'Drink water set temperature', UnitCelsius, None, True)
    pump_installed = BooleanIntegerField(6, 1, 'Drink water circulation pump installed', UnitYesNo, 0xff)
    pump_cycle = IntegerField(7, 1, 'Drink water circulation pump switch cycle', UnitMinute, 1 / 3)
    desinfection_temp = IntegerField(8, 1, 'Drink water thermal desinfection temperature', UnitCelsius, None, True)
    mode = IntegerField(9, 1, 'Drink water operation mode', UnitDwMode)
    use_valve = IntegerField(10, 1, 'Drink water loading system type', UnitDwLoading)

class UbaDrinkwaterMonitorMessage(Message):
    class Meta:
        identification = 0x34
        length = 16

    set_temp = IntegerField(0, 1, 'Drink water set temperature', UnitCelsius, None, True)
    sensor1_temp = IntegerField(1, 2, 'Drink water sensor 1 temperature', UnitCelsius, 10, True)
    sensor2_temp = IntegerField(3, 2, 'Drink water sensor 2 temperature', UnitCelsius, 10, True)
    day_mode = BooleanField(5, 1, 'Drink water day mode', UnitYesNo, 0)
    oneshot = BooleanField(5, 1, 'Drink water one shot heating', UnitYesNo, 1)
    desinfection = BooleanField(5, 1, 'Drink water thermal desinfection running', UnitYesNo, 2)
    enabled = BooleanField(5, 1, 'Drink water heating enabled', UnitYesNo, 3)
    reheat = BooleanField(5, 1, 'Drink water re-heating', UnitYesNo, 4)
    set_reached = BooleanField(5, 1, 'Drink water set temperature reached', UnitYesNo, 5)
    sens1err = BooleanField(6, 1, 'Drink water sensor 1 error', UnitYesNo, 0)
    sens2err = BooleanField(6, 1, 'Drink water sensor 2 error', UnitYesNo, 1)
    desinfect_error = BooleanField(6, 1, 'Drink water thermal desinfection error', UnitYesNo, 2)
    pump_day = BooleanField(7, 1, 'Drink water ciculation in day mode', UnitYesNo, 3)
    pump_manual = BooleanField(7, 1, 'Drink water circulation in manual mode', UnitYesNo, 4)
    pump_on = BooleanField(7, 1, 'Drink water circulation pump', UnitYesNo, 3)
    heating = BooleanField(7, 1, 'Drink water currently heating', UnitYesNo, 3)
    system_type = IntegerField(8, 1, 'Drink water system type', UnitDwType)
    current_flow = IntegerField(9, 1, 'Drink water current flow', UnitLiterPerMin, 10)
    heating_time = IntegerField(10, 3, 'Drink water total heating time', UnitMinute)
    heating_runs = IntegerField(13, 3, 'Drink water total heating runs')


class FlagsMessage(Message):
    class Meta:
        identification = 0x35
        length = 2

    data1 = IntegerField(0, 1, 'Data 1')
    data2 = IntegerField(0, 1, 'Data 2')


# https://emswiki.thefischer.net/doku.php?id=wiki:ems:telegramme#wwbetriebsart
class HcDrinkwaterParam(Message):
    class Meta:
        identification = 0x37
        length = 10
        write = True

    heating_program = IntegerField(0, 1, 'Drinkwater heating program', UnitHwDcProgram)
    circulation_program = IntegerField(1, 1, 'Drinkwater circulation program', UnitHwDcProgram)
    operation = IntegerField(2, 1, 'Drinkwater operation mode', UnitOffOnAuto)
    pump = IntegerField(3, 1, 'Drinkwater pump operation', UnitOffOnAuto)
    desinfection_on = BooleanIntegerField(4, 1, 'Drinkwater thermal desinfection', UnitOnOff, 0xff)
    desinfection_day = IntegerField(5, 1, 'Drinkwater thermal desinfection week day', UnitWeekDay)
    desinfection_hour = IntegerField(6, 1, 'Drinkwater thermal desinfection hour', UnitHour)
    desinfection_temp = IntegerField(8, 1, 'Drinkwater thermal desinfection maximum temperature', UnitCelsius, None, True)
    one_shot = BooleanIntegerField(9, 1, 'One-shot drinkwater heating', UnitOnOff, 0xff)



class HcParamMessage(Message):
    # 1 byte missing
    install_type = IntegerField(0, 1, 'Installation type', UnitHcInstallation)
    night_temp = IntegerField(1, 1, 'Night temperature', UnitCelsius, 2, True)
    day_temp = IntegerField(2, 1, 'Day temperature', UnitCelsius, 2, True)
    holiday_temp = IntegerField(3, 1, 'Holiday temperature', UnitCelsius, 2, True)
    room_influence_temp = IntegerField(4, 1, 'Room influence temperature', UnitCelsius, 2, True)
    # 1 byte missing
    room_offset_temp = IntegerField(6, 1, 'Room offset temperature', UnitCelsius, 2, True)
    operation = IntegerField(7, 1, 'Operating mode', UnitHcOperation)
    screed_trying = BooleanIntegerField(8, 1, 'Screed drying', UnitOnOff, 0xff)
    # 6 bytes missing
    max_forward_temp = IntegerField(15, 1, 'Max forward flow temperature', UnitCelsius, None, True)
    min_forward_temp = IntegerField(16, 1, 'Min forward flow temperature', UnitCelsius, None, True)
    lay_out_temp = IntegerField(17, 1, 'Lay out temperature', UnitCelsius, None, True)
    # 1 byte missing
    onoff_optimization = BooleanIntegerField(19, 1, 'On/off optimization', UnitOnOff, 0xff)
    summer_threshold = IntegerField(22, 1, 'Summer threshold', UnitCelsius, None, True)
    antifreeze_temp = IntegerField(23, 1, 'Antifreeze temperature', UnitCelsius, None, True)
    # 1 byte missing
    work_mode = IntegerField(25, 1, 'Work mode', UnitHcWorkMode)
    remote = IntegerField(26, 1, 'Remote model', UnitHcRemote)
    # 1 byte missing
    #antifreeze_mode = IntegerField(28, 1, 'Antifreeze mode', None)
    # 3 bytes missing
    #heat_system = IntegerField(32, 1, 'Heat system', None)
    #control_type = IntegerField(33, 1, 'Control type', None)
    # 1 byte missing

    # 2 bytes missing
    # 1 byte missing

class Hc1ParamMessage(HcParamMessage):
    class Meta:
        identification = 0x3D
        length = 27
        write = True
class Hc2ParamMessage(HcParamMessage):
    class Meta:
        identification = 0x47
        length = 27
        write = True
class Hc3ParamMessage(HcParamMessage):
    class Meta:
        identification = 0x51
        length = 27
        write = True
class Hc4ParamMessage(HcParamMessage):
    class Meta:
        identification = 0x5b
        length = 27
        write = True




class HcMonitorMessage(Message):
    optimize_on = BooleanField(0, 1, 'Optimize turn off', UnitYesNo, 0)
    optimize_off = BooleanField(0, 1, 'Optimize turn on', UnitYesNo, 1)
    automatic_mode = BooleanField(0, 1, 'Automatic mode', UnitYesNo, 2)
    drinkwater_preferred = BooleanField(0, 1, 'Drinkwater preferred', UnitYesNo, 3)
    screed_mode = BooleanField(0, 1, 'Screed drying mode', UnitYesNo, 4)
    vacation_mode = BooleanField(0, 1, 'Vacation mode', UnitYesNo, 5)
    frost_protection = BooleanField(0, 1, 'Frost protection', UnitYesNo, 6)
    manual = BooleanField(0, 1, 'Manual mode', UnitYesNo, 7)
    summer_mode = BooleanField(1, 1, 'Summer mode', UnitYesNo, 0)
    day_mode = BooleanField(1, 1, 'Day mode', UnitYesNo, 1)
    remote_offline = BooleanField(1, 1, 'Remote offline', UnitYesNo, 2)
    remote_error = BooleanField(1, 1, 'Remote error', UnitYesNo, 3)
    forward_error = BooleanField(1, 1, 'Forward flow sensor error', UnitYesNo, 4)
    forward_max = BooleanField(1, 1, 'Forward max flow', UnitYesNo, 5)
    external_error = BooleanField(1, 1, 'External error', UnitYesNo, 6)
    party_pause = BooleanField(1, 1, 'Party pause mode', UnitYesNo, 7)
    room_set_temp = IntegerField(2, 1, 'Set room temperature', UnitCelsius, 2, True)
    room_current_temp = IntegerField(3, 2, 'Current room temperature', UnitCelsius, 10, True)
    optimize_on_time = IntegerField(5, 1, 'Optimize turn on time')
    optimize_on_time = IntegerField(6, 1, 'Optimize turn off time')
    curve_plus_10 = IntegerField(7, 1, 'Heating curve at -10 °C', None, None, True)
    curve_plus_0 = IntegerField(8, 1, 'Heating curve at 0 °C', None, None, True)
    curve_minus_10 = IntegerField(9, 1, 'Heating curve at 10 °C', None, None, True)
    room_adaption = IntegerField(10, 2, 'Room temperature adaption speed', None, 100, True)
    boiler_power = IntegerField(12, 1, 'Requested boiler power', UnitPercent)
    party_state = BooleanField(13, 1, 'Party mode', UnitOnOff, 2)
    pause_state = BooleanField(13, 1, 'Pause mode', UnitOnOff, 3)
    vacation_state = BooleanField(13, 1, 'Vacation mode', UnitOnOff, 6)
    holiday_state = BooleanField(13, 1, 'Holiday mode', UnitOnOff, 7)
    forward_temp = IntegerField(14, 1, 'Calculated forward temp', UnitCelsius, None, True)
class Hc1MonitorMessage(HcMonitorMessage):
    class Meta:
        identification = 0x3E
        length = 15
class Hc2MonitorMessage(HcMonitorMessage):
    class Meta:
        identification = 0x48
        length = 15
class Hc3MonitorMessage(HcMonitorMessage):
    class Meta:
        identification = 0x52
        length = 15
class Hc4MonitorMessage(HcMonitorMessage):
    class Meta:
        identification = 0x5c
        length = 15


class RcOutdoorMessage(Message):
    class Meta:
        identification = 0xA3
        length = 3

    damped_temp = IntegerField(0, 1, 'Damped outdoor temperature', UnitCelsius, None, True)
    # 2 bytes missing
