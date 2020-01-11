from lib.i2c_peripherals import PCF8754
import logging
log = logging.getLogger(__name__)


class RelayBox:

    _pcf8754_map = {
        1: 7, 2: 6, 3: 5, 4: 4,
        5: 3, 6: 2, 7: 1, 8: 0
    }

    _default_config = {
        'address': 0x22,
        'DO21': 1, 'DO22': 2, 'DO23': 3, 'DO24': 4,
        'DO25': 5, 'DO26': 6, 'DO27': 7, 'DO28': 8,
    }

    def __init__(self, config=None):
        self._config = self._default_config.copy()
        if isinstance(config, dict):
            self._config.update(config)

        self._output = PCF8754(self._config['address'])
        del self._config['address']

        self._output.set_out(0x00)

    def set_outputs(self, relays=None):
        if not isinstance(relays, dict):
            relays = dict()

        status, error = self._output.get_out()
        status &= 0xFF
        if not error:
            temp_compare = status
            for relay, value in relays.items():
                if relay in self._config:
                    if str(value) == '0':
                        status &= ~(1 << self._pcf8754_map[self._config[relay]])
                    else:
                        status |= (1 << self._pcf8754_map[self._config[relay]])

            status &= 0xFF
            if status != temp_compare:
                self._output.set_out(status)
                log.debug('Relay Box outputs set to: ' + str(bin(status)))

    def get_outputs(self, relays=None):
        if not isinstance(relays, list):
            relays = list()
        dictionary = dict()
        status = ~self._output.get_out() & 0xFF

        for io_item, card_map in self._config.items():
            if (io_item in relays or len(relays) is 0) and io_item.startswith('DO'):
                dictionary[io_item] = status >> self._pcf8754_map[card_map] & 1

        log.debug('Relay box outputs read as: ', str(bin(status)))
        return dictionary
