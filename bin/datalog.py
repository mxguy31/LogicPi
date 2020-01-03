import csv
import os
import logging
import time
from datetime import datetime
from bin.database import Database
from bin.constants import CONST
log = logging.getLogger(__name__)


class Datalogger:
    def __init__(self, config=None):
        if config.has_option('misc', 'log_dir'):
            log_directory = os.path.abspath(config.get('misc', 'log_dir'))
        else:
            log_directory = CONST.LOGGING_DIR

        if config.has_option('data_log', 'log_period'):
            self._log_period = float(config.get('data_log', 'log_period'))
        else:
            self._log_period = CONST.DATLOG_PERIOD

        self._timestamp = time.monotonic()

        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        header_row = ['Time', Database.SYSTEM_STATUS]
        self.items_ref_dict = {Database.SYSTEM_STATUS: Database.SYSTEM_STATUS}  # Dummy value for system status
        if config.has_option('data_log', 'log_points'):
            for item in config.get('data_log', 'log_points').split(","):
                title = item.split("|")[1].strip()
                dat_point = item.split("|")[0].strip()
                self.items_ref_dict[title] = dat_point
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

    def log_data(self, data=None):
        # Create log item for each database value
        elapsed_time = time.monotonic() - self._timestamp
        if elapsed_time < self._log_period:
            return
        else:
            self._timestamp = time.monotonic()

        if data is None or not isinstance(data, list):
            return
        headers = self._get_headers()

        log_entry = list()
        for item in headers:
            appended = False
            if item == 'Time':
                log_entry.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                appended = True
            else:
                for key in data:
                    if str(key[Database.PARAMETER]) == str(self.items_ref_dict[item]):
                        log_entry.append(key[Database.VALUE])
                        appended = True
            if not appended:
                log_entry.append('N/A')

        self._write_data('a', log_entry)
