import threading
import time
from utils import RepeatingTimer


class Processor(object):
    def __init__(self):
        self.x = 0
        self.repeat_timer = RepeatingTimer(1, self.run)

    def start(self):
        self.repeat_timer.start()

    def run(self):
        self.result = self.x+1
        print(time.perf_counter(), 'processor data:', self.x, ' result', self.result)
        # time.sleep(5)

    def readns(self, x):
        self.x = x
