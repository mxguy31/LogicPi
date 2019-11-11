import bin.utilities
import os

print('Stopping PLC, please wait.')

config = bin.utilities.get_config('config.ini')

if config.has_option('file_system', 'database_dir'):
    database_dir = os.path.abspath(config.get('file_system', 'database_dir'))
    database = bin.utilities.Database(database_dir)
else:
    database = bin.utilities.Database()

database.write_data('Running', 0)
