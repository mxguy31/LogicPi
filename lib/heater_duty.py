import time
import logging
log = logging.getLogger(__name__)

class HeaterDuty:
    _default_config = {
        'rotate_time': 24,
        'hysteresis': 0
    }

    def __init__(self, config=None):
        # Pull config values set with modules.ini
        self._config = self._default_config.copy()
        if isinstance(config, dict):
            self._config.update(config)
        else:
            return

        self._rotate_time = float(self._config['rotate_time'])
        self._hysteresis = float(self._config['hysteresis'])
        self._order = [1, 2, 3, 4]
        self._heater_dict = {1: 'DO21', 2: 'DO22', 3: 'DO23', 4: 'DO24'}
        self._epoch = time.monotonic()
        self._last_demand = 0
        self._last_step = 0

    def execute(self, requirements_dict=None):
        if not isinstance(requirements_dict, dict):
            return
        else:
            demand = 0
            for key, value in requirements_dict.items():  # Ensure values are floats as the database works in strings
                if key == 'IV05':
                    demand = float(value)

        elapsed_time = (time.monotonic() - self._epoch) / 3600
        if elapsed_time > self._rotate_time:
            self._epoch = time.monotonic()
            self._order = self._order[1:] + self._order[:1]
            log.info('Heater duty swap completed: ' + str(self._order))

        step = 0
        if demand > self._last_demand:
            if demand > 0:
                step = 1
            if demand >= 25 + self._hysteresis:
                step = 2
            if demand >= 50 + self._hysteresis:
                step = 3
            if demand >= 75 + self._hysteresis:
                step = 4
        elif demand < self._last_demand:
            if demand > 0:
                step = 1
            if demand > 25 - self._hysteresis:
                step = 2
            if demand > 50 - self._hysteresis:
                step = 3
            if demand > 75 - self._hysteresis:
                step = 4
        else:
            step = self._last_step

        self._last_demand = demand
        self._last_step = step
        
        return_dict = {'DO21': 0, 'DO22': 0, 'DO23': 0, 'DO24': 0}
        if step > 0:
            return_dict[self._heater_dict[self._order[0]]] = 1
        if step > 1:
            return_dict[self._heater_dict[self._order[1]]] = 1
        if step > 2:
            return_dict[self._heater_dict[self._order[2]]] = 1
        if step > 3:
            return_dict[self._heater_dict[self._order[3]]] = 1

        return return_dict
