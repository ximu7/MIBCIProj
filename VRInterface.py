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
            self.stim_to_message('ExpStart', '', '', False)
            return
        if stim == StimType.StartOfTrial:
            self.stim_to_message('StartTrial', '', '', False)
            return
        if stim == StimType.MoveUp:
            self.stim_to_message('MoveUp', self.class_name, 'move', self.is_online)
            return
        if stim == StimType.MoveDown:
            self.stim_to_message('MoveDown', self.class_name, '', self.is_online)
            return
        if stim == StimType.Still:
            self.stim_to_message('Still', '', 'relax', False)
            return
        if stim == StimType.EyeGaze:
            self.send_focus_request(self.gaze_pos[self.class_name])
            return
        if stim == StimType.EndOfTrial:
            self.stim_to_message('EndTrial', self.class_name, 'stop', False)
            return
        if stim == StimType.ExperimentStop:
            self.stim_to_message('ExpStop', '', '', False)
            self.pybus.publish(self, BCIEvent.cue_disconnect)
            return

    def stim_to_message(self, stimtype, side, music, online):
        message = {'Type': stimtype, 'Side': side, 'Music': music, 'Online': online}
        self.send_message(message)

    def send_message(self, message):
        myjson = json.dumps(message)
        self.pub.send_string(myjson)
