from statistics import mean, median
from lib.PID import PID
from itertools import combinations


class TemperatureControl:
    _default_config = {
        'max_drift': .5,
        'setpoint': 0,
        'p_gain': 0,
        'i_gain': 0,
        'd_gain': 0,
        'multi_fail_mode': 'ON'
    }

    def __init__(self, config=None):
        # Pull config values set with modules.ini
        self._config = self._default_config.copy()
        if isinstance(config, dict):
            self._config.update(config)
        else:
            return

        self._max_drift = float(self._config['max_drift'])
        self._fail_mode = self._config['multi_fail_mode']
        p_gain = float(self._config['p_gain'])
        i_gain = float(self._config['i_gain'])
        d_gain = float(self._config['d_gain'])
        setpoint = float(self._config['setpoint'])

        self._failed_dict = dict()
        self._fail_limit = 6
        self._failed_sensors = list()

        self._pid = PID(p_gain, i_gain, d_gain, setpoint)
        self._pid.sample_time = 5
        self._pid.output_limits = (0, 100)

    def execute(self, requirements_dict=None):
        # Designed for ONLY 3 sensors. drift logic will not work with more or less sensors.
        values_dict = dict()
        if not isinstance(requirements_dict, dict):
            return
        else:
            for key, value in requirements_dict.items():  # Ensure values are floats as the database works in strings
                if 'DS' in key:
                    values_dict[key] = float(value)
                    if key not in self._failed_dict:
                        self._failed_dict[key] = 0
                elif key == 'IV02':
                    if str(value) == 'False':
                        self._pid.set_auto_mode(False)
                    else:
                        self._pid.set_auto_mode(True, requirements_dict['IV05'])
                elif key == 'IV01':
                    self._pid.setpoint = float(value)

        combo_list = list(combinations(values_dict.keys(), 2))
        drift_list = list()
        for sensorA, sensorB in combo_list:
            if abs(values_dict[sensorA] - values_dict[sensorB]) > self._max_drift:
                drift_list.append(sensorA)
                drift_list.append(sensorB)

        # https://www.tutorialspoint.com/python-program-to-print-duplicates-from-a-list-of-integers
        failing_sensors = list()
        self._failed_sensors = list()
        fail_count = dict()
        for x in drift_list:
            if x not in fail_count:
                fail_count[x] = 1
            else:
                if fail_count[x] == 1:
                    failing_sensors.append(x)
                fail_count[x] += 1

        for key in self._failed_dict:
            if key in failing_sensors:
                self._failed_dict[key] += 1
                if self._failed_dict[key] > self._fail_limit:
                    self._failed_dict[key] = self._fail_limit
                    self._failed_sensors.append(key)
            else:
                if self._failed_dict[key] >= 1:
                    self._failed_dict[key] -= 1
                    if self._failed_dict[key] == 0:
                        if key in self._failed_sensors:
                            self._failed_sensors.remove(key)

        if len(self._failed_sensors) == 0:
            failure_flag = False
            calculated_temperature = mean(values_dict[key] for key in values_dict)
        elif len(self._failed_sensors) == 1:
            failure_flag = True
            for key in self._failed_sensors:
                if key in values_dict:
                    del values_dict[key]
            calculated_temperature = mean(values_dict[key] for key in values_dict)
        else:
            failure_flag = True
            if self._fail_mode == 'MEDIAN':
                calculated_temperature = median(values_dict[key] for key in values_dict)
            elif self._fail_mode == 'ON':
                calculated_temperature = -9999
            else:
                calculated_temperature = 9999

        pid_output = self._pid(calculated_temperature)

        ret_dict = {'IV00': failure_flag,
                    'IV03': calculated_temperature,
                    'IV04': self._failed_sensors,
                    'IV05': pid_output}



        return ret_dict
