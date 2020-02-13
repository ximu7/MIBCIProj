import json
import zmq
from CueInterface import CueInterface
from BCIEnum import StimType, BCIEvent


class VRInterface(CueInterface):
    def __init__(self, pybus, main_cfg):
        super(VRInterface, self).__init__(pybus, main_cfg)
        self.PUB_address = 'tcp://*:12345'
        self.REP_address = 'tcp://*:12346'
        self.connected = False

    def start(self):
        if not self.connected:
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
            self.connected = True

    def handle_stim(self, stim):
        if stim in self.class_list:
            self.class_name = stim
            return
        if stim == StimType.ExperimentStart:
            self.send_message({'Type': 'ExpStart'})
            return
        if stim == StimType.MoveUp:
            self.send_message({'Type': 'MoveUp', 'Side': self.class_name, 'Music': 'move'})
            return
        if stim == StimType.MoveDown:
            self.send_message({'Type': 'MoveDown', 'Side': self.class_name})
            return
        if stim == StimType.Still:
            self.send_message({'Type': 'Still', 'Music': 'relax'})
            return
        if stim == StimType.EyeGaze:
            self.send_focus_request(self.gaze_pos[self.class_name])
            return
        if stim == StimType.EndOfTrial:
            self.send_message({'Type': 'EndTrial', 'Side': self.class_name, 'Music': 'stop'})
            return
        if stim == StimType.ExperimentStop:
            self.send_message({'Type': 'ExpStop'})
            self.pybus.publish(self, BCIEvent.cue_disconnect)
            return

    def send_message(self, message):
        myjson = json.dumps(message)
        self.pub.send_string(myjson)
