# -*- coding: utf-8 -*-
import numpy as np
import random
from utils import bandpass_filter
import matplotlib.pyplot as plt


def loadnpz(filepath):
    """
    读npz文件，生成数据
    filepath: npz文件路径
    data_x: T×N×L ndarray T: 采样点数  N: 通道数  L: 训练数据 trial 总数
    data_y: shape (n_samples,) L 个 trial 对应的标签
    """
    Data, index, fs = load_rawdata_from_npz(filepath)
    cue_list = [769, 770, 775]
    data_x, data_y = epoch_from_cuelist(Data, index, fs, cue_list)
    return data_x, data_y


def load_rawdata_from_npz(filepath):
    # Data (samples, channels)
    # index 第一列 时间idx，第二列 cue
    BPdata = np.load(filepath)
    Fs = BPdata.f.SampleRate
    # FirstTime = BPdata.f.firstsignal - 20 / Fs
    index = BPdata.f.MarkOnSignal
    Data = BPdata.f.signal
    Data = Data[:, 0:-1]
    Fs = np.squeeze(Fs)
    return Data, index, Fs


def epoch_from_cuelist(Data, index, fs, cue_list, before_cue=0):
    # input Data(samples, channels)
    # output data_x(samples, channels, trials)
    index_list = index[:, 1].tolist()
    cue_index = min([index_list.index(cue) for cue in cue_list])
    rest_index = index_list.index(800)
    samples = int(round((index[rest_index, 0] - index[cue_index, 0]) / fs) * fs)
    trial_num = len(np.where(index[:, 1] == 800)[0])
    channal_num = Data.shape[1]
    # trial_num = int(trial_num / 2)
    data_x1, data_y1 = epochbycue(Data, index, cue_list[0], samples, channal_num, trial_num, 0, before_cue)
    data_x = data_x1
    data_y = data_y1
    for i in range(1, len(cue_list)):
        data_x1, data_y1 = epochbycue(Data, index, cue_list[i], samples, channal_num, trial_num, i, before_cue)
        data_x = np.concatenate((data_x, data_x1), axis=2)
        data_y = np.concatenate((data_y, data_y1), axis=0)
    data_x, data_y = disorder(data_x, data_y)
    return data_x, data_y


def disorder(data_x, data_y):
    epoch_num = data_y.shape[0]
    li = list(range(epoch_num))
    random.shuffle(li)
    data_x = data_x[:, :, li]
    data_y = data_y[li]
    return data_x, data_y


def epochbycue(Data, index, cue, samples, channal_num, trial_num, tocue, before_cue=0):
    i, j = 0, 0
    data_x = np.zeros([samples+before_cue*500, channal_num, trial_num])
    data_y = np.zeros(trial_num)
    while i < index.shape[0]:
        if index[i, 1] == cue:
            index_cue = index[i, 0]
            while True:
                i += 1
                if index[i, 1] == 800:
                    data_x[:, :, j] = Data[index_cue-before_cue*500:index_cue+samples, :]
                    data_y[j] = tocue
                    j += 1
                    break
        i += 1
    data_x = data_x[:, :, :j]
    data_y = data_y[:j]
    return data_x, data_y


def epoch_wholeonecue(data_x, data_y, cue_idx):
    # data_x (samples, channels, trials)
    return np.squeeze(data_x[:, :, np.where(data_y == cue_idx)])


def sliding_window(data_x, data_y=None, filter_bank=False):
    """
       滑窗  trial-->epoch , 乱序

       输入参数
       ----------
       data_x: T×N×L ndarray 或单个trial T×N
            T: 采样点数  N: 通道数  L: 训练数据 trial 总数
       data_y: shape (n_samples,)
            L 个 trial 对应的标签

       返回值
       ----------
       data_x_epoch: T×N×L ndarray
            T: 一个窗采样点数  N: 通道数  L: 训练数据 epoch 总数
       data_y_epoch: shape (n_samples,)
            L 个 epoch 对应的标签
    """
    step = 250  # 步长
    window_size = 250  # 窗的大小
    delay = 0  # Start_Of_Trial后延迟1s
    if filter_bank:
        if len(data_x.shape) == 4:
            samples, channal_num = data_x.shape[0], data_x.shape[1]
            band_num, trial_num = data_x.shape[2], data_x.shape[3]
            window_num = int((samples - delay - window_size) / step + 1)  # 每个trial 滑多少个窗
            epoch_num = trial_num * window_num
            data_y_epoch = np.zeros(epoch_num)
            data_x_epoch = np.zeros([window_size, channal_num, band_num, epoch_num])
            for b in range(band_num):
                epoch_count = 0
                for k in range(trial_num):
                    for i in range(window_num):
                        data_y_epoch[epoch_count] = data_y[k]
                        start = int(i * step + delay)
                        data_x_epoch[:, :, b, epoch_count] = data_x[start:start + window_size, :, b, k]
                        epoch_count = epoch_count + 1
            # 打乱次序
            li = list(range(epoch_num))
            random.shuffle(li)
            data_x_epoch = data_x_epoch[:, :, :, li]
            data_y_epoch = data_y_epoch[li]
            return data_x_epoch, data_y_epoch
        elif len(data_x.shape) == 3:
            samples, channal_num, band_num = data_x.shape[0], data_x.shape[1], data_x.shape[2]
            epoch_num = int((samples - delay - window_size) / step + 1)  # 每个trial 滑多少个窗
            data_x_epoch = np.zeros([window_size, channal_num, band_num, epoch_num])
            for b in range(band_num):
                for i in range(epoch_num):
                    start = int(i * step + delay)
                    data_x_epoch[:, :, b, i] = data_x[start:start + window_size, :, b]
            if data_y is not None:
                data_y_epoch = np.array([data_y, ] * epoch_num)
                return data_x_epoch, data_y_epoch
            else:
                return data_x_epoch
    else:
        if len(data_x.shape) == 3:
            samples, channal_num, trial_num = data_x.shape[0], data_x.shape[1], data_x.shape[2]
            window_num = int((samples - delay - window_size) / step + 1)  # 每个trial 滑多少个窗
            epoch_num = trial_num * window_num
            data_y_epoch = np.zeros(epoch_num)
            data_x_epoch = np.zeros([window_size, channal_num, epoch_num])
            epoch_count = 0
            for k in range(trial_num):
                for i in range(window_num):
                    data_y_epoch[epoch_count] = data_y[k]
                    start = int(i * step + delay)
                    data_x_epoch[:, :, epoch_count] = data_x[start:start + window_size, :, k]
                    epoch_count = epoch_count + 1
            # 打乱次序
            li = list(range(epoch_num))
            random.shuffle(li)
            data_x_epoch = data_x_epoch[:, :, li]
            data_y_epoch = data_y_epoch[li]
            return data_x_epoch, data_y_epoch
        elif len(data_x.shape) == 2:
            samples, channal_num = data_x.shape[0], data_x.shape[1]
            epoch_num = int((samples - delay - window_size) / step + 1)  # 每个trial 滑多少个窗
            data_x_epoch = np.zeros([window_size, channal_num, epoch_num])
            for i in range(epoch_num):
                start = int(i * step + delay)
                data_x_epoch[:, :, i] = data_x[start:start + window_size, :]
            if data_y is not None:
                data_y_epoch = np.array([data_y, ] * epoch_num)
                return data_x_epoch, data_y_epoch
            else:
                return data_x_epoch


def meanFilter(data_x):
    """
    均值滤波，针对某一通道某一时间段滑窗 x-mean(x)

    输入参数
    data_x: T×N×L ndarray
        T: 采样点数  N: 通道数  L: 训练数据 trial 总数

    返回值
    data_x_AfterFilter: T×N×L ndarray
        T: 采样点数  N: 通道数  L: 训练数据 trial 总数
    """
    import math
    Samples, trial_num = data_x.shape[0], data_x.shape[2]
    window_size = 500  # 窗的大小
    window_num = math.ceil(Samples / window_size + 1)  # 每个trial 滑多少个窗
    data_x_AfterFilter = np.zeros(data_x.shape)
    for k in range(trial_num):
        for i in range(window_num):
            start = i * window_size
            data = data_x[start:start + window_size, :, k]
            data_x_AfterFilter[start:start + window_size, :, k] = data - np.mean(data, axis=0)  # 按列求均值
    return data_x_AfterFilter


def polynomialFilter(data_x, order=1):
    """
    多项式滤波

    输入参数
    data_x: T×N×L ndarray
        T: 采样点数  N: 通道数  L: 训练数据 trial 总数

    返回值
    data_x_AfterFilter: T×N×L ndarray
        T: 采样点数  N: 通道数  L: 训练数据 trial 总数
    """
    channal_num, trial_num = data_x.shape[1], data_x.shape[2]
    data_x_AfterFilter = np.zeros(data_x.shape)
    for i in range(trial_num):
        for j in range(channal_num):
            data = data_x[:, j, i]
            x = np.arange(data.size)
            p = np.poly1d(np.polyfit(x, data, order))
            base = p(x)
            data_x_AfterFilter[:, j, i] = data - base
    return data_x_AfterFilter


def baselineCalibration(data_x):
    # 均值滤波 + 带通滤波 + 多项式拟合
    data_x = meanFilter(data_x)
    data_x = bandpass_filter(data_x, fs=500, filter_low=8, filter_high=30)
    data_x = polynomialFilter(data_x, order=1)
    return data_x


def drawRawEEG(data_x, trial_idx=0):
    """
    输入参数
    data_x: T×N×L ndarray
        T: 采样点数  N: 通道数  L: 训练数据 trial 总数
    trial_idx: 某一个trial
    eg: drawRawEEG(data_x, trial_idx=14)
    """
    t = np.linspace(1, data_x.shape[0], data_x.shape[0])
    plt.figure(1)
    channal_num = data_x.shape[1]
    channels14 = ['cz', 'c2', 'f3', 'fz', 'f4', 'c3', 'c4', 'c1', 'fcz', 'fc1', 'fc2', 'cp3', 'cp4', 'cpz']
    channels8 = ['f3', 'fz', 'f4', 'fc1', 'fc2', 'c3', 'cz', 'c4']
    for i in range(channal_num):
        plt.subplot(channal_num, 1, i + 1)
        if len(data_x.shape) == 3:
            plt.plot(t, data_x[:, i, trial_idx])
        else:
            plt.plot(t, data_x[:, i])
        if channal_num == 14:
            plt.ylabel(channels14[i])
        elif channal_num == 8:
             plt.ylabel(channels8[i])
    plt.show()


if __name__ == "__main__":
    # data_x, data_y = loadnpz(r'D:\Myfiles\PythonProjects\signal\ZJJ\0504\acquireNSsignal_2018_05_04_14_42_10.npz')
    # data_x = CARFilter(data_x)
    # data_x = bandpass_filter(data_x, fs=500, filter_low=8, filter_high=30)
    # drawRawEEG(data_x[0:3000, :, :], trial_idx=14)
    # data_x, data_y = sliding_window(data_x, data_y)
    # sio.savemat('D:\\Myfiles\\PythonProjects\\signal\\ZJJ\\0423\\mat_data\\onlineNSsignal_2018_04_23_15_43_37.mat', {'data_x': data_x, 'data_y': data_y})
    filepath = r'D:\code\PythonProjects_5.1\data_set\98JiangSuqing\98JiangSuqing_20190910\acquireNSsignal_20190910_1520_27.npz'
    Data, index, fs = load_rawdata_from_npz(filepath)
    print(Data.shape)
