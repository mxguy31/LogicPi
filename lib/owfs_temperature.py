import ow
import logging
import threading
import time
log = logging.getLogger(__name__)


class OWFSTemperature:

    _default_config = {
        'location': 'localhost:4304',
        'loop_time': 10,
    }

    def __init__(self, config=None):
        self._config = self._default_config.copy()
        if isinstance(config, dict):
            self._config.update(config)

        self._location = self._config['location']
        self._loop_time = int(self._config['loop_time'])
        del self._config['location']
        del self._config['loop_time']

        self._temperature_dict = dict()
        for sensor in self._config.keys():
            self._temperature_dict[sensor] = -300

        self._thread = threading.Thread(target=self._temperature_loop, daemon=True)
        self._thread.start()

    def _temperature_loop(self):
        ow.init(self._location)
        sensorlist = ow.Sensor('/').sensorList()

        while True:
            for ow_sensor in sensorlist:
                for IOPoint in self._config.keys():
                    try:
                        if ow_sensor.alias in self._config[IOPoint]:
                            self._temperature_dict[IOPoint] = ow_sensor.temperature

                    except Exception as e:
                        log.exception('An error occurred while obtaining sensor temperature: ' + str(IOPoint))
                        log.exception(e)
                        raise
            time.sleep(self._loop_time)

    def get_values(self, sensors=None):
        if not isinstance(sensors, list):
            sensors = list()
        temp_dict = {}
        for sensor, value in self._temperature_dict.items():
            if sensor in sensors or len(sensors) is 0:
                temp_dict[sensor] = value
        return temp_dict
