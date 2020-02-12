import socket
import json
import zmq
from CueInterface import CueInterface

class VRInterface(CueInterface):
    def __init__(self, pybus, main_cfg):
        super(VRInterface, self).__init__(pybus, main_cfg)
        self.PUB_address = 'tcp://*:12345'
        self.REP_address = 'tcp://*:12346'

    def start(self):
        context = zmq.Context()
        self.pub = context.socket(zmq.PUB)
        self.pub.bind(self.PUB_address)
        self.rep = context.socket(zmq.REP)
        self.rep.bind(self.REP_address)
        while True:
            recv_msg = self.rep.recv_string()
            if recv_msg == 'connect request':
                print(recv_msg)
                self.rep.send_string('OK')
                break
