import csv
import os
import logging
import time
from datetime import datetime
from bin.database import Database
from bin.constants import CONFIG
log = logging.getLogger(__name__)


class Datalogger:
    FILE_NAME = 'Logged Data %s.csv'
    PERIOD = 120

    def __init__(self, config=None):
        if config.has_option('misc', 'log_dir'):
            log_directory = os.path.abspath(config.get('file_system', 'log_dir'))
        else:
            log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG.LOGGING_DIR)

        if config.has_option('misc', 'log_period'):
            self._log_period = float(config.get('misc', 'log_period'))
        else:
            self._log_period = Datalogger.PERIOD

        self._timestamp = time.monotonic()

        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        self.header_row = ['Time', Database.SYSTEM_STATUS]
        for item in config.items('log_points'):
            self.header_row.append(item[0])

        self._log_file = os.path.join(log_directory, Datalogger.FILE_NAME % 0)

        if os.path.exists(self._log_file):
            log.info('Existing log file found at ' + self._log_file)
            file_header = self._get_headers()
            file_header.sort()
            self.header_row.sort()
            if file_header != self.header_row:
                log.info('Existing file headers do not match requested format. Creating new file.')
                i = 0
                while os.path.exists(os.path.join(log_directory, Datalogger.FILE_NAME % i)):
                    i += 1
                self._log_file = os.path.join(log_directory, Datalogger.FILE_NAME % i)
                self._write_data('w', self.header_row)
        else:
            log.info('New log file created at ' + self._log_file)
            self._write_data('w', self.header_row)

    def _write_data(self, mode, data):
        try:
            with open(self._log_file, mode) as file:
                writer = csv.writer(file, dialect='excel')
                writer.writerow(data)
        except OSError:
            log.exception('Failed to read data log file - ' + Datalogger.FILE_NAME)

    def _get_headers(self):
        try:
            with open(self._log_file, 'r') as f:
                reader = csv.DictReader(f)
                return reader.fieldnames
        except OSError:
            log.exception('Failed to read data log file - ' + Datalogger.FILE_NAME)

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
                    if key[Database.PARAMETER] == item:
                        log_entry.append(key[Database.VALUE])
                        appended = True
            if not appended:
                log_entry.append('N/A')

        self._write_data('a', log_entry)
