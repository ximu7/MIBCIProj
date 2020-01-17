from time import sleep
from utils.PyEventBus import *
from neuroscan import *
from Processor1 import *

pybus = PyEventBus()
param = 5
neuroscan = NS()
processor = Processor()
#  processor事件源  NS监听者
pybus.subscribe(processor, 'a', neuroscan, neuroscan.SendData)
neuroscan.start()
processor.start()
for i in range(10):
    print('publish!')
    data = pybus.publish(processor, 'a', param)
    processor.readns(data)
    sleep(7)

