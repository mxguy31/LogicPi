import sys
import os
import time
import logging
from bin.constants import CONST
from datetime import datetime
from datetime import timedelta
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

    datalog = Datalogger(config)

    paused_flag = False
    print(datetime.now(), 'PLC Running.')
    log.info('PLC Running.')
    while True:
        sleepy = datetime.now().replace(microsecond=0) + timedelta(seconds=CONST.MIN_CYC_FRQ) - datetime.now()
        time.sleep(sleepy.seconds + sleepy.microseconds / 1000000)

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

        datalog.log_data(database.dump_data())

    print(datetime.now(), 'Closing Database.')
    database.close()

    # clean up outputs
    log.info('PLC Stopped.')
    print(datetime.now(), 'PLC Stopped.')


if __name__ == '__main__':
    print(datetime.now(), 'Starting Pi_PLC, please wait.')
    main_loop()
