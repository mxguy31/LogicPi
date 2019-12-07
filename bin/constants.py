import logging


class CONFIG:
    CONFIG_FILE = 'config.ini'
    MODULE_CONFIG_FILE = '../lib/modules.ini'
    LOG_CONFIG_FILE = 'data_logger.ini'
    BACKUP_DATA = 'backup.db'
    LOGGING_DIR = 'logs'
    SYSLOG_LEVEL = logging.INFO
    SYSLOG_NAME = 'syslog.log'
    DATLOG_NAME = 'data.log'
    MIN_DAT_FRQ = 30
    MIN_CYC_FRQ = 1
    MODULE_FOLDER = '.lib'
