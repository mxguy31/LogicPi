import sys
import os
import time
import logging
from bin.constants import CONST
from datetime import datetime
import bin.utilities as utilities
from bin.datalog import Datalogger
log = logging.getLogger(__name__)


def main_loop():
    config = utilities.get_config(CONST.SYS_CONF_FILE)

    if config is None:
        print(datetime.now(), 'No config file was found, system is shutting down')
        sys.exit(1)

    utilities.setup_logger(config)

    module_config = utilities.get_config(os.path.join(CONST.MOD_CONF_DIR, CONST.MOD_CONF_FILE))
    user_modules = utilities.get_ext_modules(module_config)

    database = utilities.get_database(config)
    database.write_data(database.SYSTEM_STATUS, database.ON)

    Datalogger(config)

    paused_flag = False
    print(datetime.now(), 'PLC Running.')
    log.info('PLC Running.')
    while True:
        start_time_stamp = time.time()

        if database.read_data(database.SYSTEM_STATUS)[database.VALUE] == database.OFF:
            log.info('PLC operation stopped as requested by database flag.')
            break
        elif database.read_data(database.SYSTEM_STATUS)[database.VALUE] == database.PAUSED:
            if not paused_flag:
                log.info('PLC operation paused as requested by database flag.')
                paused_flag = not paused_flag
        else:
            if paused_flag:
                log.info('PLC operation resumed as requested by database flag.')
                paused_flag = not paused_flag
            #  Run the input functions
            utilities.run_ext_modules(database, user_modules, 'Interface', 'Input')

            #  Run the logic functions
            utilities.run_ext_modules(database, user_modules, 'Logic')

            #  Run the output functions
            utilities.run_ext_modules(database, user_modules, 'Interface', 'Output')

        end_timestamp = time.time()
        sleep_time = (start_time_stamp + CONST.MIN_CYC_PERIOD) - end_timestamp
        if CONST.MIN_CYC_PERIOD > sleep_time > 0:
            time.sleep(sleep_time)
        else:
            time.sleep(CONST.MIN_CYC_PERIOD)

    # TODO clean up outputs
    log.info('PLC Stopped.')
    print(datetime.now(), 'PLC Stopped.')


if __name__ == '__main__':
    print(datetime.now(), 'Starting Pi_PLC, please wait.')
    main_loop()
