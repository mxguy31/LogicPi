# LogicPi
A basic RaspberryPi based logic engine which is expandable through a simple API

This engine maintains a database and cycles through the logic and IO modules added by the user. Each module is passed values from the database as defined in the modules.ini file. Each logic module may (or may not) return values to the database. Database entries are simple Key-Value pairs (with access time stamp). 

## Usage
All Logic Modules and IO Modules are sorted and completed in alpha-numeric order.
The following are example function calls that will be used from the main loop.
The calls that should be used must be identified in modules.ini
A MAXIMUM of 10 functions is allowed per logic module.

## Logic modules
```python
<module_name.py>
class <ModuleName>:
    def __init__(self, config_dict):
        # required internal variables can be established here
        # settings from the modules.ini file are passed as a dictionary

    def execute(self, requirements_dict):
        # function to execute, it is a passed a dictionary with the key-value pairs based on modules.ini values
        # must return none, or a dictionary with key-value pairs
```

## IO Modules
```python
<interface_name.py>
class <InterfaceName>:
    def __init__(self, config_dict):
        # required internal variables can be established here
        # settings from the modules.ini file are passed as a dictionary

    def get_inputs(self, *inputs_list):
        # function which gathers the input data and returns it in a dictionary form
        # required IO identifier keys area assigned in the modules.ini file
        # *inputs is a list of requested inputs, a value of none will return all inputs available

    def get_outputs(self, *outputs_list):
        # function which gathers the output status and returns it in a dictionary form
        # required IO identifier keys area assigned in the modules.ini file
        # *outputs_list is a list of requested outputs, a value of none will return all outputs available

    def set_outputs(self, outputs_dict):
        # function which sets the outputs, based on the provided dictionary
        # required IO identifier keys area assigned in the modules.ini file
```

## Suggested IO identifier naming system
```
DOXX - Digital  Output  00 through 99
DIXX - Digital  Input   00 through 99
DSXX - Digital  Sensor  00 through 99
DVXX - Digital  Value   00 through 99
AOXX - Analogue Output  00 through 99
AIXX - Analogue Input   00 through 99
IVXX - Internal Value   00 through 99
```
