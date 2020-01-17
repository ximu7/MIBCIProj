import threading
import time

import queue
from NSDataReader import RepeatingTimer

class NS(object):
    def __init__(self):
        self.x = 0
        self.repeat_timer = RepeatingTimer(1, self.run)

    def start(self):
        self.repeat_timer.start()

    def run(self):
        self.x += 1
        print(time.perf_counter(), 'ns receive data:', self.x)

    def SendData(self,param):
        print(time.perf_counter(), 'ns send data:', self.x + param)
        return self.x + param