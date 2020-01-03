import time
import logging
log = logging.getLogger(__name__)

class HeaterDuty:
    _default_config = {
        'rotate_time': 24
    }

    def __init__(self, config=None):
        # Pull config values set with modules.ini
        self._config = self._default_config.copy()
        if isinstance(config, dict):
            self._config.update(config)
        else:
            return

        self._rotate_time = float(self._config['rotate_time'])
        self._demand = 0
        self._order = [1, 2, 3, 4]
        self._heater_dict = {1: 'DO21', 2: 'DO22', 3: 'DO23', 4: 'DO24'}
        self._epoch = time.monotonic()

    def execute(self, requirements_dict=None):
        if not isinstance(requirements_dict, dict):
            return
        else:
            for key, value in requirements_dict.items():  # Ensure values are floats as the database works in strings
                if key == 'IV05':
                    self._demand = float(value)

        elapsed_time = (time.monotonic() - self._epoch) / 3600
        if elapsed_time > self._rotate_time:
            self._epoch = time.monotonic()
            self._order = self._order[1:] + self._order[:1]
            log.info('Heater duty swap completed: ' + str(self._order))

        return_dict = {'DO21': 0, 'DO22': 0, 'DO23': 0, 'DO24': 0}
        if self._demand > 0:
            return_dict[self._heater_dict[self._order[0]]] = 1
        if self._demand >= 25:
            return_dict[self._heater_dict[self._order[1]]] = 1
        if self._demand >= 50:
            return_dict[self._heater_dict[self._order[2]]] = 1
        if self._demand >= 75:
            return_dict[self._heater_dict[self._order[3]]] = 1

        return return_dict
