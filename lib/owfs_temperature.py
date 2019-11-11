import os
import glob
import logging
import threading
import time
log = logging.getLogger(__name__)


class OWFSTemperature:

    _owfs_map = {
        1:  0,  2:  1,  3:  2,  4:  3,
        5:  4,  6:  5,  7:  6,  8:  7,
        9:  8,  10: 9,  11: 10, 12: 11,
        13: 12, 14: 13, 15: 14, 16: 15,
        17: 16
    }

    _default_config = {
        'owfs_location': '/mnt/owfs/', 'loop_time': 5,
        'DS01': 1,  'DS02': 2,  'DS03': 3,  'DS04': 4,
        'DS05': 5,  'DS06': 6,  'DS07': 7,  'DS08': 8,
        'DS09': 9,  'DS10': 10, 'DS11': 11, 'DS12': 12,
        'DS13': 13, 'DS14': 14, 'DS15': 15, 'DS16': 16,
        'DS17': 17
    }

    def __init__(self, config=None):
        self._temperature_dict = {
            'DS01': -300, 'DS02': -300, 'DS03': -300, 'DS04': -300,
            'DS05': -300, 'DS06': -300, 'DS07': -300, 'DS08': -300,
            'DS09': -300, 'DS10': -300, 'DS11': -300, 'DS12': -300,
            'DS13': -300, 'DS14': -300, 'DS15': -300, 'DS16': -300,
            'DS17': -300
        }

        self._config = self._default_config.copy()
        if isinstance(config, dict):
            self._config.update(config)

        self._owfs_location = self._config['owfs_location']
        self._loop_time = int(self._config['loop_time'])
        del self._config['owfs_location']
        del self._config['loop_time']

        self._thread = threading.Thread(target=self._temperature_loop, daemon=True)
        self._thread.start()
        print('OWFS Running')

    def _temperature_loop(self):
        while True:
            time.sleep(self._loop_time)
            for sensor, card_map in self._config.items():
                temperature = -300
                if sensor.startswith('DS'):
                    sensor_bus = os.path.join(self._owfs_location,
                                              'bus.' + str(self._owfs_map[card_map]),
                                              '28.*', 'temperature')
                    for sensor_file in glob.glob(sensor_bus):
                        try:
                            with open(sensor_file) as sensor_temperature:
                                temperature = float(sensor_temperature.read())
                                break

                        except OSError:
                            log.warning('Sensor ' + str(sensor) + ' could not be read')
                            print("Sensor " + str(sensor) + " could not be read")

                        except Exception:
                            log.exception('An unforeseen error occurred ' + str(sensor))
                            print('An unforeseen error occurred when reading sensor ' + str(sensor))
                            raise

                    self._temperature_dict[sensor] = temperature

    def get_values(self, sensors=None):
        if not isinstance(sensors, list):
            sensors = list()
        temp_dict = {}
        for sensor, value in self._temperature_dict.items():
            if sensor in sensors or len(sensors) is 0:
                temp_dict[sensor] = value
        return temp_dict
