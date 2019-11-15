from statistics import mean


class TemperatureControl:
    _default_config = {
        'max_drift': .5,
        'max_setpoint': 30,
        'min_setpoint': 20,

    }

    def __init__(self, config=None):
        self._config = self._default_config.copy()
        if isinstance(config, dict):
            self._config.update(config)

        self.max_drift = self._config['max_drift']
        self._values_dict = dict()
        self._average_temp = None
        self._failure = None

    def _find_max(self):
        value = list(self._values_dict.values())
        key = list(self._values_dict.keys())
        return key[value.index(max(value))]

    def _find_min(self):
        value = list(self._values_dict.values())
        key = list(self._values_dict.keys())
        return key[value.index(min(value))]

    def _average(self, removed_key):
        temp = self._values_dict.copy()
        if removed_key is not None:
            del temp[removed_key]
        return mean(temp[key] for key in temp)

    def execute(self, requirements_dict=None):
        if not isinstance(requirements_dict, dict):
            self._values_dict = dict()
        else:
            self._values_dict = requirements_dict
        pass

        maximum = self._find_max()
        minimum = self._find_min()

        low_avg = self._average(maximum)
        high_avg = self._average(minimum)

        if (self._values_dict[maximum] - low_avg) > self.max_drift:
            self._failure = maximum
            self._average_temp = low_avg
        elif (high_avg - self._values_dict[minimum]) > self.max_drift:
            self._failure = minimum
            self._average_temp = high_avg
        else:
            self._failure = None
            self._average_temp = self._average(None)
