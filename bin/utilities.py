import os
import re
import importlib
from importlib import util
from datetime import datetime
from bin.database import Database
import configparser
import logging
from bin.constants import CONFIG
log = logging.getLogger(__name__)


# Inspiration from -> https://copyninja.info/blog/dynamic-module-loading.html
def import_module(module_name):
    module = None
    t_name = '.' + module_name
    try:
        if importlib.util.find_spec(t_name, CONFIG.MODULE_FOLDER) is not None:  # Check if module exists first
            module = importlib.import_module(t_name, CONFIG.MODULE_FOLDER)  # Import module
    except ImportError:
        log.error('Failed to load user module: ', module_name)

    return module


def get_ext_modules(config):
    if config is None:
        return None

    module_dict = dict()
    func_string = re.compile(r'f\d_')

    for section in config.sections():
        try:
            if not (config.has_option(section, 'type') and  # Check to ensure minimum information is present
                    config.has_option(section, 'enabled') and
                    config.has_option(section, 'class') and
                    config.getboolean(section, 'enabled')):  # Check if this module is enabled
                continue
        except ValueError:
            continue

        t_module = import_module(section)  # Import the module
        mod_dict = dict()
        t_class = None
        t_mod_config = dict()

        for key, value in config.items(section):  # Iterate through the module parameters and transfer to a local dict()
            if key == 'class':
                t_class = getattr(t_module, value)  # Load the module class
            elif key == 'enabled':
                continue  # Skip this key, it is only used in this function
            elif not (func_string.search(key) or key == 'type'):
                t_mod_config[key] = value  # Transfer user config values to a new dict
            else:
                mod_dict[key] = value  # Else just transfer the config values

        mod_dict['class'] = t_class(t_mod_config)  # Overwrite the class name with the loaded class
        module_dict[section] = mod_dict

    return module_dict


def run_ext_modules(database, user_modules, mod_type, func_type='Logic'):
    for module, mod_info in user_modules.items():
        if mod_info['type'] == mod_type:
            for function in range(0, 10):
                t_func_name = 'f' + str(function) + '_name'
                t_func_type = 'f' + str(function) + '_type'
                t_func_requires = 'f' + str(function) + '_requires'
                if t_func_name in mod_info and mod_info[t_func_type] == func_type:
                    t_requires = dict()
                    if mod_info[t_func_requires] != 'None':
                        t_requires_list = mod_info[t_func_requires].split(",")
                        for item in t_requires_list:
                            temp_data = database.read_data(item)
                            if temp_data is not None:
                                t_requires[item] = temp_data[1]
                    else:
                        t_requires = None

                    return_data = getattr(mod_info['class'], mod_info[t_func_name])(t_requires)
                    if return_data is not None:
                        for key, value in return_data.items():
                            database.write_data(key, value)


def get_config(config_file):
    print(datetime.now(), 'Loading config from ' + str(config_file))
    if not os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)):
        return None
    else:
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file), encoding='utf-8')
        return config


def setup_logger(config):
    log_level = logging.INFO
    if config.has_option('misc', 'log_level'):
        if config.get('misc', 'log_level') == 'DEBUG':
            log_level = logging.DEBUG
        elif config.get('misc', 'log_level') == 'WARNING':
            log_level = logging.WARNING
        elif config.get('misc', 'log_level') == 'ERROR':
            log_level = logging.ERROR
        elif config.get('misc', 'log_level') == 'CRITICAL':
            log_level = logging.CRITICAL

    if config.has_option('file_system', 'log_dir'):
        log_directory = os.path.abspath(config.get('file_system', 'log_dir'))
    else:
        log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG.LOGGING_DIR)

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_name = os.path.join(log_directory, CONFIG.SYSLOG_NAME)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=log_name,
                        level=log_level)


def get_database(config):
    if config.has_option('file_system', 'database_dir'):
        database_dir = os.path.abspath(config.get('file_system', 'database_dir'))
        database = Database(database_dir)
    else:
        database = Database()

    return database
