class LogicOne:
    def __init__(self, config_dict):
        pass
        # required internal variables can be established here
        # settings from the modules.ini file are passed as a dictionary

    def test(self, requirements_dict):
        outputs = dict()
        if requirements_dict['DI01'] == '1':
            outputs['DO00'] = 1
        else:
            outputs['DO00'] = 0

        return outputs
