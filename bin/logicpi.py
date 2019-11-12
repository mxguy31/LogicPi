import sys
import time
import logging
from pathlib import Path
from bin.constants import CONFIG
from datetime import datetime
from datetime import timedelta
import bin.utilities as utilities
log = logging.getLogger(__name__)


def main_loop():
    log.info('************************************************')
    log.info('*************** Starting Pi_PLC ****************')

    config = utilities.get_config(CONFIG.CONFIG_FILE)
    if config is None:
        print(datetime.now(), 'No config file was found, system is shutting down')
        sys.exit(1)

    module_config = utilities.get_config(Path(CONFIG.MODULE_CONFIG_FILE))
    user_modules = utilities.get_ext_modules(module_config)

    utilities.setup_logger(config)

    database = utilities.get_database(config)
    database.write_data(database.SYSTEM_STATUS, database.ON)

    paused_flag = False
    print(datetime.now(), 'PLC Running.')
    log.info('PLC Running.')
    while True:
        sleepy = datetime.now().replace(microsecond=0) + timedelta(seconds=CONFIG.MIN_CYC_FRQ) - datetime.now()
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

            log.debug('PLC cycle completed')

    print(datetime.now(), 'Closing Database.')
    database.close()

    # clean up outputs
    log.info('PLC Stopped.')
    print(datetime.now(), 'PLC Stopped.')


if __name__ == '__main__':
    print(datetime.now(), 'Starting Pi_PLC, please wait.')
    main_loop()

# This is a test comment to test how github and pycharm version control works.
