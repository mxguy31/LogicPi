import sqlite3
import time
import inspect
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
        db_file = os.path.join(location, "Pi_PLC.db")
        sql = """ CREATE TABLE IF NOT EXISTS system_status (
                parameter text PRIMARY KEY,
                value text NOT NULL,
                timestamp int NOT NULL
            ); """

        try:
            if os.path.exists(db_file):
                log.info('Existing database file found at ' + db_file)
            else:
                log.info('New database file created at ' + db_file)

            self._conn = sqlite3.connect(db_file)
            cursor = self._conn.cursor()
            cursor.execute(sql)
            cursor.close()
            self._conn.commit()
            log.debug('Database connection established.')

        except sqlite3.Error as e:
            log.exception('Database error: ' + str(e))
            # print("Database error: " + str(e))

    def _cursor_ops(self, sql, data):
        try:
            cursor = self._conn.cursor()
            cursor.execute(sql, data)
            row = cursor.fetchone()
            cursor.close()
            if row is None:
                self._conn.commit()
            else:
                return row

        except sqlite3.Error as e:
            log.exception('Database error: ' + str(e))
            # print("Database error: " + str(e))

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
        cursor = self._conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    def close(self):
        self._conn.close()
        log.debug('Database connection from ' + inspect.stack()[1][3] + ' closed.')
