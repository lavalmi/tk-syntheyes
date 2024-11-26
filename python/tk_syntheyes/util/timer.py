import time

class Timer():
    def __init__(self, sleep, timeout):
        self._time = 0
        self._timeout = timeout
        self._sleep = sleep

    def sleep(self, err_msg=""):
        time.sleep(self._sleep)
        self._time += self._sleep
        if self._time > self._timeout:
            raise Exception(err_msg)
        
    def reset(self):
        self._time = 0