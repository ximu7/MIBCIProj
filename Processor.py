import pickle
from time import time, strftime
from BCIEnum import BCIEvent, StimType
from NSDataReader import RepeatingTimer


class Processor(object):
    def __init__(self, pybus, main_cfg):
        self.pybus = pybus
        self.is_online = main_cfg.is_online
        self.class_list = main_cfg.stim_cfg.class_list
        self.model_path = main_cfg.subject.get_model_path()
        self.save_path = main_cfg.subject.get_date_dir()
        self.online_timer = RepeatingTimer(0.1, self.online_run)
        self.signal = None
        self.predict_state = False
        self.is_feedback = False
        self.trial_num = 0
        self.right_num_onerun = []
        self.right_num_all = []
        self.result_log = []

    def start(self):
        if self.is_online:
            file = open(self.model_path, 'rb')
            self.clf = pickle.load(file)
            self.online_timer.start()

    def handle_stim(self, stim):
        if not self.is_online:
            return
        if stim in self.class_list:
            self.label = stim
            self.label_y = self.class_list.index(stim)
            self.is_feedback = False if stim == 'rest' else True
            return
        if stim == StimType.StartOfTrial:
            self.predict_state = True
            return
        if stim == StimType.EndOfTrial:
            self.predict_state = False
            self.get_result_log()
            return
        if stim == StimType.ExperimentStop and self.is_online:
            self.save_log()

    def online_run(self):
        if self.predict_state:
            signal = self.pybus.publish(self, BCIEvent.readns, duration=500)
            result = self.clf.online_predict(signal)
            predict_right = 1 if result == self.label_y else 0
            self.right_num_onerun.append(predict_right)
            if self.is_feedback and (len(self.right_num_onerun) == 1 or self.right_num_onerun[-2] != predict_right):
                self.pybus.publish(self, BCIEvent.online_predict, bool(predict_right))

    def get_result_log(self):
        epoch_num = len(self.right_num_onerun)
        one_run_acc = sum(self.right_num_onerun) / epoch_num
        self.right_num_all.extend(self.right_num_onerun)
        self.right_num_onerun = []
        all_acc = one_run_acc if len(self.right_num_all) == 0 else sum(self.right_num_all) / len(self.right_num_all)
        self.trial_num = self.trial_num + 1
        print('————————————')
        one_run_log = '\ntrial ' + str(self.trial_num) + ':  ' + 'cue:' + str(self.label) + \
                      '\nthis run acc:' + str(one_run_acc) + ', epoch num:' + str(epoch_num) + \
                      '\nall runs acc:' + str(all_acc)
        print(one_run_log)
        self.result_log.append(one_run_log)

    def save_log(self):
        if self.is_online:
            f = open(strftime(self.save_path + "//onlineResult_%Y%m%d_%H%M_%S.txt"), 'a')
            f.writelines(self.result_log)
            f.close()
