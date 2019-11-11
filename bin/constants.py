import logging


class CONFIG:
    CONFIG_FILE = 'config.ini'
    MODULE_CONFIG_FILE = '../lib/modules.ini'
    BACKUP_DATA = 'backup.db'
    LOGGING_DIR = 'logs'
    SYSLOG_LEVEL = logging.INFO
    SYSLOG_NAME = 'syslog.log'
    DATLOG_NAME = 'data.log'
    MIN_DAT_FRQ = 30
    MIN_CYC_FRQ = 1
    MODULE_FOLDER = '.lib'


class DATALOG:
    ZONE_HEADER = ['Time',
                   'Name',
                   'Type',
                   'HVU Mode',
                   'FAN Mode',
                   'Away Mode',
                   'Heat Status',
                   'Fan Status',
                   'Cool Status',
                   'Avg Temp',
                   'Delta Temp',
                   'High Name',
                   'High Value',
                   'Low Name',
                   'Low Value',
                   'Heat Set',
                   'Fan Set',
                   'Cool Set',
                   'Away Heat Set',
                   'Away Fan Set',
                   'Away Cool Set',
                   'Heat Wobble Set',
                   'Fan Wobble Set',
                   'Cool Wobble Set']
