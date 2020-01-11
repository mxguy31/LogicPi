import csv
import os
import logging
import time
import threading
from datetime import datetime, timedelta
from bin.database import Database
from bin.constants import CONST
log = logging.getLogger(__name__)

# Significant inspiration (plenty of copy/paste) from somewhere on the net several years ago.
# Credit is given to whoever originally wrote that module.

class Datalogger:
    def __init__(self, config=None):
        if config.has_option('misc', 'log_dir'):
            log_directory = os.path.abspath(config.get('misc', 'log_dir'))
        else:
            log_directory = CONST.LOGGING_DIR

        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        if config.has_option('file_system', 'database_dir'):
            self._database_dir = os.path.abspath(config.get('file_system', 'database_dir'))
        else:
            self._database_dir = None

        if config.has_option('data_log', 'log_period'):
            self._log_period = float(config.get('data_log', 'log_period'))
        else:
            self._log_period = CONST.DATLOG_PERIOD

        nextminute = datetime.now().replace(second=0, microsecond=0) + timedelta(seconds=60)
        if nextminute.minute % 2:  # ensure minute is an even amount just for OCD sake.
            starttime = nextminute + timedelta(minutes=1)
        else:
            starttime = nextminute

        self._logstart = time.mktime(starttime.timetuple())

        header_row = ['Time', Database.SYSTEM_STATUS]
        self._items_ref_dict = {Database.SYSTEM_STATUS: Database.SYSTEM_STATUS}  # Dummy value for system status
        if config.has_option('data_log', 'log_points'):
            for item in config.get('data_log', 'log_points').split(","):
                title = item.split("|")[1].strip()
                dat_point = item.split("|")[0].strip()
                self._items_ref_dict[title] = dat_point
                header_row.append(title)

        self._log_file = os.path.join(log_directory, CONST.DATLOG_FILE)

        if os.path.exists(self._log_file):
            log.info('Existing log file found at ' + self._log_file)
            file_header = self._get_headers()
            if file_header != header_row:
                log.exception('Existing, incompatible, log file already exists.')
                raise FileExistsError('Existing, incompatible, log file already exists.')
        else:
            log.info('New log file created at ' + self._log_file)
            self._write_data('w', header_row)

        self._thread = threading.Thread(target=self._log_data, daemon=True)
        self._thread.start()
        log.info('Data logger started')

    def _write_data(self, mode, data):
        try:
            with open(self._log_file, mode) as file:
                writer = csv.writer(file, dialect='excel')
                writer.writerow(data)
        except OSError:
            log.exception('Failed to update data log file - ' + CONST.DATLOG_FILE)

    def _get_headers(self):
        try:
            with open(self._log_file, 'r') as f:
                reader = csv.DictReader(f)
                return reader.fieldnames
        except OSError:
            log.exception('Failed to read data log file - ' + CONST.DATLOG_FILE)

    def _log_data(self):
        if self._database_dir is None:
            database = Database()
        else:
            database = Database(self._database_dir)

        # Create log item for each database value
        waittime = self._logstart - time.time()
        while True:
            while waittime > 0:
                waittime = self._logstart - time.time()
                if waittime < 0: waittime = 0
                if waittime < 1:
                    time.sleep(waittime)
                else:
                    time.sleep(1)
            nextrun = time.time() + (self._log_period - ((time.time() - self._logstart) % self._log_period))
            while time.time() <= nextrun:
                partime = (self._log_period - ((time.time() - self._logstart) % self._log_period))
                if partime < 1:
                    time.sleep(partime)
                else:
                    time.sleep(1)

            data = database.dump_data()
            headers = self._get_headers()

            log_entry = list()
            for item in headers:
                appended = False
                if item == 'Time':
                    log_entry.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    appended = True
                else:
                    for key in data:
                        if str(key[Database.PARAMETER]) == str(self._items_ref_dict[item]):
                            log_entry.append(key[Database.VALUE])
                            appended = True
                if not appended:
                    log_entry.append('N/A')

            self._write_data('a', log_entry)
