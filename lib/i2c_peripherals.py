from smbus2 import SMBus
import logging
log = logging.getLogger(__name__)


class MCP23017:
    # MCP23017 Register definitions
    # Interrupts are not included in this driver yet.
    _IODIRA = 0x00
    _IODIRB = 0x01
    _IOPOLA = 0x02
    _IOPOLB = 0x03
    # GPINTENA    = 0x04
    # GPINTENB    = 0x05
    # DEFVALA     = 0x06
    # DEFVALB     = 0x07
    # INTCONA     = 0x08
    # INTCONB     = 0x09
    # IOCON       = 0x0A
    _GPPUA = 0x0C
    _GPPUB = 0x0D
    # INTFA       = 0x0E
    # INTFB       = 0x0F
    # INTCAPA     = 0x10
    # INTCAPB     = 0x11
    _GPIOA = 0x12
    _GPIOB = 0x13
    _OLATA = 0x14
    _OLATB = 0x15

    OUTPUT = 0
    INPUT = 1
    HIGH = 1
    LOW = 0

    def __init__(self, address, busnum=1, iodira=0xFF,
                 iodirb=0xFF, gppua=0, gppub=0,
                 ipola=0, ipolb=0, porta=0, portb=0):
        self._i2c = SMBus(busnum)
        self._address = address

        # Assign values (calls setter arguments and sets the registers as desired)
        self._iodira = iodira
        self._iodirb = iodirb
        self._gppua = gppua
        self._gppub = gppub
        self._ipola = ipola
        self._ipolb = ipolb
        self._porta = porta
        self._portb = portb

        self._access_error = False

    def _setregister(self, register, value):
        try:
            self._i2c.write_byte_data(self._address, register, value)
            self._access_error = False

        except OSError:
            if not self._access_error:
                self._access_error = True
                log.warning('I2C device at address ' + str(hex(self._address)) + ' could not be accessed.')
                # print('I2C device at address ' + str(hex(self._address)) + ' could not be accessed.')

    def _getregister(self, register):
        try:
            value = self._i2c.read_byte_data(self._address, register)
            self._access_error = False
        except OSError:
            if not self._access_error:
                self._access_error = True
                log.warning('I2C device at address ' + str(hex(self._address)) + ' could not be accessed.')
                # print('I2C device at address ' + str(hex(self._address)) + ' could not be accessed.')
            value = 0xFF

        return value

    def _changebit(self, bitmap, bit, value):
        assert value == 1 or value == 0, "Value is %s, it must be 1 or 0" % value
        if value == 0:
            return bitmap & ~(1 << bit)
        elif value == 1:
            return bitmap | (1 << bit)

    def _modifyregister(self, register, bit, value):
        assert 0 <= bit < 8, "Bit number %s is invalid, only 0-7 are valid" % bit
        currvalue = self._getregister(register)
        newvalue = self._changebit(currvalue, bit, value)
        self._setregister(register, newvalue)
        return newvalue

    @property
    def porta(self):
        """8-Bit PortB value, each bit represents one pin, 1 = high, 0 = low"""
        self._porta = self._getregister(self._GPIOA)
        return self._porta

    @porta.setter
    def porta(self, value):
        if value > 255:
            raise ValueError("You can't assign a number greater than 8-bits to a port")
        self._porta = value
        self._setregister(self._OLATA, self._porta)

    @property
    def portb(self):
        """8-Bit PortB value, each bit represents one pin, 1 = high, 0 = low"""
        self._portb = self._getregister(self._GPIOB)
        return self._portb

    @portb.setter
    def portb(self, value):
        if value > 255:
            raise ValueError("You can't assign a number greater than 8-bits to a port")
        self._portb = value
        self._setregister(self._OLATB, self._portb)

    @property
    def iodira(self):
        """8-Bit PortA direction value, each bit represents one pin, 1 = input, 0 = output"""
        self._iodira = self._getregister(self._IODIRA)
        return self._iodira

    @iodira.setter
    def iodira(self, value):
        if value > 255:
            raise ValueError("You can't assign a number greater than 8-bits to a port direction")
        self._iodira = value
        self._setregister(self._IODIRA, self._iodira)

    @property
    def iodirb(self):
        """8-Bit PortB direction value, each bit represents one pin, 1 = input, 0 = output"""
        self._iodirb = self._getregister(self._IODIRB)
        return self._iodirb

    @iodirb.setter
    def iodirb(self, value):
        if value > 255:
            raise ValueError("You can't assign a number greater than 8-bits to a port direction")
        self._iodirb = value
        self._setregister(self._IODIRB, self._iodirb)

    @property
    def gppua(self):
        """8-Bit PortA weak pull-up value, each bit represents one pin, 1 = enabled, 0 = disabled"""
        self._gppua = self._getregister(self._GPPUA)
        return self._gppua

    @gppua.setter
    def gppua(self, value):
        if value > 255:
            raise ValueError("You can't assign a number greater than 8-bits to a port direction")
        self._gppua = value
        self._setregister(self._GPPUA, self._gppua)

    @property
    def gppub(self):
        """8-Bit PortB weak pull-up value, each bit represents one pin, 1 = enabled, 0 = disabled"""
        self._gppub = self._getregister(self._GPPUB)
        return self._gppub

    @gppub.setter
    def gppub(self, value):
        if value > 255:
            raise ValueError("You can't assign a number greater than 8-bits to a port direction")
        self._gppub = value
        self._setregister(self._GPPUB, self._gppub)

    def get_dir16(self):
        return (self.iodirb << 8) | self.iodira, self._access_error

    def set_dir16(self, direction):
        self.iodirb = (direction >> 8) & 0xFF
        self.iodira = direction & 0xFF
        return self._access_error

    def get_stat16(self):
        return (self.portb << 8) | self.porta, self._access_error

    def set_stat16(self, status):
        self.portb = (status >> 8) & 0xFF
        self.porta = status & 0xFF
        return self._access_error


class PCF8754:
    def __init__(self, address, busnum=1):
        self._address = address
        self._i2c = SMBus(busnum)
        self._access_error = False

    def set_out(self, output):
        try:
            self._i2c.write_byte(self._address, (~output & 0xFF))
            self._access_error = False

        except OSError:
            if not self._access_error:
                self._access_error = True
                log.warning('I2C device at address ' + str(hex(self._address)) + ' could not be accessed.')
                # print('I2C device at address ' + str(hex(self._address)) + ' could not be accessed.')

        return self._access_error

    def get_out(self):
        try:
            value = ~self._i2c.read_byte(self._address) & 0xFF
            self._access_error = False

        except OSError:
            if not self._access_error:
                self._access_error = True
                log.warning('I2C device at address ' + str(hex(self._address)) + ' could not be accessed.')
                # print('I2C device at address ' + str(hex(self._address)) + ' could not be accessed.')
            value = 0x00

        return value, self._access_error
