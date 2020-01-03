import threading
import time
import datetime
import logging
log = logging.getLogger(__name__)

# I'm not sure where I found this, but it was on the internet somewhere several years ago.
# Credit is given to whoever wrote this module.


class RepeatEvery(threading.Thread):
    def __init__(self, starttime, interval, func, *args, **kwargs):
        threading.Thread.__init__(self)
        if not isinstance(starttime, datetime.datetime):
            starttime = datetime.datetime.now()
        self.starttime = time.mktime(starttime.timetuple())
        self.interval = interval  # seconds between calls
        self.func = func  # function to call
        self.args = args  # optional positional argument(s) for call
        self.kwargs = kwargs  # optional keyword argument(s) for call
        self.running = True

    def run(self):
        try:
            waittime = self.starttime - time.time()
            while self.running:
                while waittime > 0:
                    waittime = self.starttime - time.time()
                    if waittime < 0: waittime = 0
                    if waittime < 1:
                        time.sleep(waittime)
                    else:
                        time.sleep(1)
                        if not self.running: break
                nextrun = time.time() + (self.interval - ((time.time() - self.starttime) % self.interval))
                while time.time() <= nextrun:
                    partime = (self.interval - ((time.time() - self.starttime) % self.interval))
                    if partime < 1:
                        time.sleep(partime)
                    else:
                        time.sleep(1)
                        if not self.running: break
                self.func(*self.args, **self.kwargs)
        except Exception:
            log.exception('An unexpected error occurred')
            raise

    def stop(self):
        self.running = False