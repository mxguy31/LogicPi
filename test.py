import csv
import lib.owfs_temperature
import time
from datetime import datetime
from datetime import timedelta

temp_getter = lib.owfs_temperature.OWFSTemperature()

test = list()
test.append('DS01')
test.append('DS02')
test.append('DS04')
test.append('DS13')
test.append('DS15')

t = 0
while t < 100:
    sleepy = datetime.now().replace(microsecond=0) + timedelta(seconds=6) - datetime.now()
    time.sleep(sleepy.seconds + sleepy.microseconds / 1000000)
    data = temp_getter.get_values(test,)
    with open('log.log', mode='a') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), data])
    t += 1
