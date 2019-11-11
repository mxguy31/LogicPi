from lib.i2c_peripherals import MCP23017
import logging
log = logging.getLogger(__name__)


class CustomIO:

    _mcp23017_map_in = {
        1:  8,  2:  7,  3:  9,  4:  6,
        5:  10, 6:  5,  7:  11, 8:  4,
        9:  12, 10: 3,  11: 13, 12: 2,
        13: 14, 14: 1,  15: 15, 16: 0
    }

    _mcp23017_map_out = {
        0:  8,  1:  7,  2:  9,  3:  6,
        4:  10, 5:  5,  6:  11, 7:  4,
        8:  12, 9:  3,  10: 13, 11: 2,
        12: 14, 13: 1,  14: 15, 15: 0
    }

    _default_config = {
        'address_out': 0x20, 'address_in': 0x21,
        'DI01': 1,  'DI02': 2,  'DI03': 3,  'DI04': 4,
        'DI05': 5,  'DI06': 6,  'DI07': 7,  'DI08': 8,
        'DI09': 9,  'DI10': 10, 'DI11': 11, 'DI12': 12,
        'DI13': 13, 'DI14': 14, 'DI15': 15, 'DI16': 16,
        'DO00': 0,  'DO01': 1,  'DO02': 2,  'DO03': 3,
        'DO04': 4,  'DO05': 5,  'DO06': 6,  'DO07': 7,
        'DO08': 8,  'DO09': 9,  'DO10': 10, 'DO11': 11,
        'DO12': 12, 'DO13': 13, 'DO14': 14, 'DO15': 15
    }

    def __init__(self, config=None):
        self._config = self._default_config.copy()
        if isinstance(config, dict):
            self._config.update(config)

        self._output_driver = MCP23017(self._config['address_out'])
        self._output_driver.set_stat16(0xFFFF)
        self._output_driver.set_dir16(0x0)
        self._input_driver = MCP23017(self._config['address_in'])
        del self._config['address_out']
        del self._config['address_in']

    def get_inputs(self, inputs=None):
        if not isinstance(inputs, list):
            inputs = list()
        dictionary = dict()
        status = self._input_driver.get_stat16() & 0xFFFF

        for io_item, card_map in self._config.items():
            if (io_item in inputs or len(inputs) is 0) and io_item.startswith('DI'):
                dictionary[io_item] = status >> self._mcp23017_map_in[card_map] & 1

        return dictionary

    def set_outputs(self, relays=None):
        if not isinstance(relays, dict):
            relays = dict()

        status = self._output_driver.get_stat16() & 0xFFFF
        temp_compare = status
        for relay, value in relays.items():
            if relay in self._config:
                if str(value) == '1':
                    status &= ~(1 << self._mcp23017_map_out[self._config[relay]])
                else:
                    status |= (1 << self._mcp23017_map_out[self._config[relay]])

        status &= 0xFFFF
        if status != temp_compare:
            self._output_driver.set_stat16(status)

    def get_outputs(self, relays=None):
        if not isinstance(relays, list):
            relays = list()
        dictionary = dict()
        status = ~self._output_driver.get_stat16() & 0xFFFF

        for io_item, card_map in self._config.items():
            if (io_item in relays or len(relays) is 0) and io_item.startswith('DO'):
                dictionary[io_item] = status >> self._mcp23017_map_out[card_map] & 1

        return dictionary
