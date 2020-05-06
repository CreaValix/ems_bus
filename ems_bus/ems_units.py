'''Unit descriptions for the EMS bus'''

class Unit:
    def __init__(self, value):
        self._value = value

    def __str__(self):
        value = self.value
        sign = self.sign
        return(f'{value} {sign}' if len(sign) > 0 else value)

    def update(self, value):
        self._value = value

    @property
    def value(self):
        values = getattr(self, 'VALUES', None)
        if values is None:
            return(self._value)
        return(values[int(self._value)])

    # Todo: Should be static
    @property
    def sign(self):
        sign = getattr(self, 'SIGN', None)
        return(sign if sign else '')


class UnitDate(Unit):
    @property
    def value(self):
        return(self._value.isoformat())

class UnitDateTime(Unit):
    @property
    def value(self):
        return(self._value.isoformat())

class UnitMinute(Unit):
    SIGN = 'min'
    RANGE = (0, 60)

class UnitHour(Unit):
    SIGN = 'h'
    RANGE = (0, 24)

class UnitYesNo(Unit):
    VALUES = ('No', 'Yes')

class UnitOpenClosed(Unit):
    VALUES = ('Closed', 'Open')

class UnitOnOff(Unit):
    VALUES = ('Off', 'On')

class UnitCelsius(Unit):
    SIGN = '°C'
    RANGE = (0, 80)

class UnitPercent(Unit):
    SIGN = '%'
    RANGE = (0, 100)

class UnitBar(Unit):
    SIGN = 'bar'

class UnitMicroAmpere(Unit):
    SIGN = 'µA'

class UnitLiterPerMin(Unit):
    SIGN = 'l/min'

class UnitWeekDay(Unit):
    VALUES = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Daily')

class UnitOffOnAuto(Unit):
    VALUES = ('Always off', 'Always on', 'Auto')


class UnitDwMode(Unit):
    @property
    def value(self):
        return('ECO' if self._value == 0xDB else 'Comfort')

class UnitDwLoading(Unit):
    @property
    def value(self):
        return('Three way valve' if self._value == 0xFF else 'Pump')

class UnitDwType(Unit):
    VALUES = (
        'No drink water', 'Flow heating', 'Flow heating with small hot water tank', 'Hot water tank'
    )

class UnitDevice(Unit):
    VALUES = ('Present', 'Absent')

class UnitHcInstallation(Unit):
    VALUES = ('(unknown)', 'Radiator', 'Convector', 'Floor heating', 'Room forward flow')

class UnitHcWorkMode(Unit):
    VALUES = ('Off', 'Reduced', 'Room guided', 'Outside guided')

class UnitHcRemote(Unit):
    VALUES = ('(none)', 'RC20', 'RC3x')

class UnitHcOperation(Unit):
    VALUES = ('Night', 'Day', 'Auto')


class UnitUbaMsTimestamp(Unit):
    VALUES = ('None', 'Working hours', 'Date')

class UnitUbaMmNeed(Unit):
    VALUES = ('No', '1', '2', 'Yes, by working hours', '4', '5', '6', '7', 'Yes, by date')

class UnitUbaFtValve(Unit):
    VALUES = ('Heat circuit', 'Drinkwater circuit')

class UnitHwDcProgram(Unit):
    VALUES = ('By heat circuit', 'Separate program')
