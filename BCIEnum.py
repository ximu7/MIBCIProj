from enum import Enum


class BCIEvent(Enum):
    readns = 1
    change_stim = 2
    online_predict = 3
    gaze_focus = 4
    cue_disconnect = 5
    save_data = 6


classStimList = ('left', 'right', 'rest')


class StimType(Enum):
    # left = 1
    # right = 2
    # rest = 3
    ExperimentStart = 10
    ExperimentStop = 11
    CrossOnScreen = 12
    StartOfTrial = 13
    EndOfTrial = 14
    EyeGaze = 15
    MoveUp = 16
    MoveDown = 17
    Still = 18
    Disconnect = 19
