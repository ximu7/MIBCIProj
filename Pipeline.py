import numpy as np
from time import strftime, sleep
from BCIEnum import BCIEvent
from utils import PyEventBus
from Processor import Processor
from Stimulator import Stimulator
from NSDataReader import NSDataReader, NSDataReaderRandom
from CueInterface import CueInterface


class Pipeline(object):
    def __init__(self, main_cfg):
        pybus = PyEventBus()
        # self.ns_reader = NSDataReader()
        self.ns_reader = NSDataReaderRandom()
        main_cfg.exo.is_online = main_cfg.is_online
        self.cue = CueInterface(pybus, main_cfg)
        self.stim = Stimulator(pybus, main_cfg.stim_cfg)
        self.processor = Processor(pybus, main_cfg)
        self.save_data_path = main_cfg.subject.get_date_dir()
        self.filename = 'online' if main_cfg.is_online else 'acquire'
        self.stim_cfg = main_cfg.stim_cfg
        pybus.subscribe(self.processor, BCIEvent.readns, self.ns_reader, self.ns_reader.get_signal)
        pybus.subscribe(self.stim, BCIEvent.change_stim, self.processor, self.processor.handle_stim)
        pybus.subscribe(self.stim, BCIEvent.change_stim, self.cue, self.cue.handle_stim)
        pybus.subscribe(self.stim, BCIEvent.change_stim, main_cfg.exo, main_cfg.exo.handle_stim)
        pybus.subscribe(self.processor, BCIEvent.online_predict, self.cue, self.cue.online_feedback)
        pybus.subscribe(self.processor, BCIEvent.online_predict, main_cfg.exo, main_cfg.exo.online_feedback)
        pybus.subscribe(self.cue, BCIEvent.gaze_focus, self.stim, self.stim.get_gaze)
        pybus.subscribe(self.cue, BCIEvent.cue_disconnect, self.stim, self.stim.stop_stim)
        pybus.subscribe(self.stim, BCIEvent.save_data, self, self.save_data)
        pybus.subscribe(self.stim, BCIEvent.save_data, self.processor, self.processor.save_log)

    def start(self):
        self.ns_reader.start()
        self.cue.start()
        sleep(2)
        self.stim.start()
        self.processor.start()

    def save_data(self):
        ns_header = self.ns_reader.get_head_settings()
        signal = self.ns_reader.get_signal()
        data_time = self.ns_reader.data_time
        first_time, last_time = data_time[0], data_time[-1]
        data_time = np.array(np.linspace(0, last_time - first_time, signal.shape[0]))
        class_list = np.array(self.stim.class_list)
        class_list[:, 0] = class_list[:, 0] - first_time
        event_list = np.array(self.stim.event_list)
        event_list[:, 0] = event_list[:, 0] - first_time
        event_id = self.stim_cfg.get_class_dict()
        events = np.zeros([class_list.shape[0], 3])
        events[:, 2] = class_list[:, 1]
        k = 0
        for i in range(class_list.shape[0]):
            for j in range(k, len(data_time)):
                if data_time[j] > class_list[i, 0]:
                    v1 = abs(data_time[j - 1] - class_list[i, 0])
                    v2 = abs(data_time[j] - class_list[i, 0])
                    events[i, 0] = j - 1 if v1 < v2 else j
                    k = j - 1
                    break
        np.savez(strftime(self.save_data_path + "//" + self.filename + "NS_%Y%m%d_%H%M_%S"),
                 signal=signal, ns_header=ns_header, event_id=event_id, events=events,
                 class_list=class_list, event_list=event_list)

