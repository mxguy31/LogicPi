import sqlite3
import time
import os
import logging
log = logging.getLogger(__name__)


class Database:
    ON = '1'
    RUN = ON
    TRUE = ON

    OFF = '0'
    STOP = OFF
    FALSE = OFF

    SYSTEM_STATUS = 'Running'
    PAUSED = '2'

    PARAMETER = 0
    VALUE = 1
    TIMESTAMP = 2

    def __init__(self, location=os.path.dirname(os.path.realpath(__file__))):
        self._dbfile = os.path.join(location, "Pi_PLC.db")
        sql = """ CREATE TABLE IF NOT EXISTS system_status (
                parameter text PRIMARY KEY,
                value text NOT NULL,
                timestamp int NOT NULL
            ); """
        if os.path.exists(self._dbfile):
            log.info('Existing database file found at ' + self._dbfile)
        else:
            log.info('New database file created at ' + self._dbfile)

        self._cursor_ops(sql)

    def _cursor_ops(self, sql, data=None):
        try:
            connection = sqlite3.connect(self._dbfile)
            cursor = connection.cursor()

            if data is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, data)

            row = cursor.fetchone()
            cursor.close()
            if row is None:
                connection.commit()

        except sqlite3.Error as e:
            log.exception('Database error: ' + str(e))
            row = None

        finally:
            if (connection):
                connection.close()

        return row

    def write_data(self, parameter, value):
        data = (str(parameter), str(value), int(time.time()))
        sql = ''' REPLACE INTO system_status (parameter, value, timestamp) VALUES(?,?,?) '''
        self._cursor_ops(sql, data)

    def read_data(self, parameter):
        sql = ''' SELECT * FROM system_status WHERE parameter=? '''
        data = self._cursor_ops(sql, (parameter,))
        return data

    def dump_data(self):
        sql = '''SELECT * FROM system_status'''

        try:
            connection = sqlite3.connect(self._dbfile)
            cursor = connection.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()

        except sqlite3.Error as e:
            log.exception('Database error: ' + str(e))
            results = None

        finally:
            if (connection):
                connection.close()

        return results
