import os
import logging


class CONST:
    SYS_CONF_DIR = os.path.dirname(os.path.abspath(__file__))
    SYS_CONF_FILE = 'config.ini'
    MOD_CONF_DIR = os.path.abspath(os.path.join(SYS_CONF_DIR, '../lib'))
    MOD_CONF_FILE = 'modules.ini'
    LOGGING_DIR = os.path.abspath(os.path.join(SYS_CONF_DIR, '../logs'))
    SYSLOG_LEVEL = logging.INFO
    SYSLOG_FILE = 'syslog.log'
    DATLOG_FILE = 'datlog.csv'
    DATLOG_PERIOD = 120
    MIN_CYC_PERIOD = 2
    MODULE_FOLDER = '.lib'
