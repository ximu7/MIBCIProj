import os
import datetime
import time
import serial

# HERE IS THE Parameters：
#     baudrate：9600
#     LEFT_ELBOW1_ID   1
#     RIGHT_ELBOW1_ID  2
#     LEFT_ELBOW2_ID   3
#     RIGHT_ELBOW2_ID  4
#     LEFT_WRIST_ID    5
#     RIGHT_WRIST_ID   6
#     LEFT_ELBOW1_range   [300, 1300]
#     RIGHT_ELBOW1_range  [1200, 2300]
#     LEFT_ELBOW2_range   [1700, 2500]
#     RIGHT_ELBOW2_range  [200, 1300]
#     LEFT_WRIST_range    [300, 1000]
#     RIGHT_WRIST_range   [1000, 1600] 
#     具体还是看手上标签标注的

#定义外骨骼对应参数-主要是ID
class simple_Exoskeleton(object):
    def __init__(self):
        self.last = 0
        self.count = 0
        self.command_num = 0
        self.last_command = 'stop'
        self.command_num = 0
        self.baud_rate = 9600
        self.Connected = False
        self.exo_type = 'elbow'
        # self.highest_point = 1250
        # self.lowest_point = 250
        # self.velocity = 30 默认都是30
        # self.com_num = com_num #根据计算机的设备管理器给出！！！！！！！
        self.is_exo_feedback = False
        self.is_online = True 
        self.first_stage = True
        # self.set_exo_param()



    # def set_param(self, ID, highest_point, lowest_point, velocity):
    #     self.highest_point[ID] = highest_point
    #     self.lowest_point[ID] = lowest_point
    #     self.velocity[ID] = velocity

# 链接串口
    def connect(self, com_num):
        self.com_num = com_num
        if not self.Connected:
            self.link_to_exoskeleton()
            self.Connected = True
        self.reset_arm()
        # pos = self.read_position()
        # print(pos)

    # def handle_stim(self, stim):
    #     if not self.is_exo_feedback:
    #         return
    #     if stim == StimType.MoveUp:
    #         self.first_stage = True if self.is_online else self.stretch_arm()
    #         return
    #     if stim == StimType.MoveDown:
    #         self.first_stage = False if self.is_online else self.back_arm()
    #         return
    #     if stim == StimType.EndOfTrial:
    #         self.reset_arm()
    #         return
    #     if stim == StimType.ExperimentStop:
    #         self.disconnect_com()

    # def online_feedback(self, predict):
    #     if not self.is_exo_feedback:
    #         return
    #     if predict:
    #         self.back_arm() if self.first_stage else self.stretch_arm()
    #     else:
    #         self.exoskeleton_stop()


    # 连接串口，输入串口号和波特率
    def link_to_exoskeleton(self):
        print('Trying to Connect to com')
        try:
            self.com = serial.Serial('com' + str(self.com_num), self.baud_rate)
            print('Connect to com successfully')
        except Exception as e:
            print('Open serial failed.' + str(e))

    

    # def strategy_reciprocating(self):
    #     now_position = self.read_position()
    #     if abs(self.last - now_position) == 0:
    #         if self.goal == 1:
    #             self.back_arm()
    #             self.goal = 2
    #         else:
    #             self.stretch_arm()
    #             self.goal = 1
    #     self.last = now_position

    # 预览 循环运动
    # def preview_step(self):
    #     try:
    #         if self.exo_type == 'elbow':
    #             i = 0
    #             while i < 30:
    #                 self.strategy_reciprocating()
    #                 time.sleep(0.2)
    #                 print('step')
    #                 i += 1
    #             # self.back_arm()
    #             self.stretch_arm()
    #         else:
    #             time.sleep(1)
    #             reciprocate_command = ''
    #             if self.exo_type == 'forearm':
    #                 reciprocate_command = 'A3V' + self.velocity_str + 'L' + self.lowest_point_str + 'R' + self.highest_point_str + 'E'
    #             elif self.exo_type == 'wrist':
    #                 reciprocate_command = 'A4V' + self.velocity_str + 'L' + self.lowest_point_str + 'R' + self.highest_point_str + 'E'
    #             self.com_write(reciprocate_command)
    #             print(reciprocate_command)
    #             time.sleep(5)
    #     except:
    #         print("Exoskeleton not connected.")

    

    # 展臂动作
    # def stretch_arm(self):
    #     stretch_command = ''
    #     if self.exo_type == 'elbow':
    #         stretch_command = "AI" + str(self.id) + "G" + str(self.lowest_point) + "E"
    #     elif self.exo_type in['forearm', 'wrist']:
    #         if self.exo_type == 'forearm':
    #             stretch_command = 'A1V' + self.velocity_str + 'L' + self.lowest_point_str + 'R00E'
    #         else:
    #             stretch_command = 'A2V' + self.velocity_str + 'L' + self.lowest_point_str + 'R00E'
    #     self.com_write(stretch_command)
    #     print("stretch ", stretch_command)

    # # 收臂动作
    # def back_arm(self):
    #     back_command = ''
    #     if self.exo_type == 'elbow':
    #         back_command = "AI" + str(self.id) + "G" + str(self.highest_point) + "E"
    #     elif self.exo_type in ['forearm', 'wrist']:
    #         if self.exo_type == 'forearm':
    #             back_command = 'A1V' + self.velocity_str + 'L00R' + self.highest_point_str + 'E'
    #         else:
    #             back_command = 'A2V' + self.velocity_str + 'L00R' + self.highest_point_str + 'E'
    #     self.com_write(back_command)
    #     print("back ", back_command)

    # # 快速复位动作
    # def reset_arm(self):
    #     reset_command = ''
    #     if self.exo_type == 'elbow':
    #         reset_command = "AI" + str(self.id) + "G" + str(self.lowest_point) + "E"
    #     elif self.exo_type in ['forearm', 'wrist']:
    #         if self.exo_type == 'forearm':
    #             reset_command = 'A1V' + self.velocity_str + 'L00R01E'
    #         else:
    #             reset_command = 'A2V' + self.velocity_str + 'L00R01E'
    #     self.com_write(reset_command)
    #     print("reset ", reset_command)

# 运动到指定位置
    def go(self, ID, pos):
        self.pos = pos
        go_command = ''
        go_command = "AI" + str(ID) + "G" + str(self.pos) + "E"
        self.com_write(go_command)
        print("go ", reset_command)

# 读取当前位置
    def read_position(self, ID):
        self.com_write("AP" + str(self.id) + "E")
        time.sleep(0.01)
        position = int(self.com.read(4).decode())
        self.com.read_all()
        return position




# 关闭串口
    def disconnect_com(self):
        self.reset_arm()
        self.com.close()
        print("Exoskeleton close successfully")

    def com_write(self, message):
        self.com.write(message.encode())
        time.sleep(0.01)
    
# 停止运动
    def exoskeleton_stop(self):
        stop_command = ''
        position_diff = -20
        position = self.read_position()
        stop_command = "AI" + str(self.id) + "G" + str(position + position_diff) + "E"
        self.com_write(stop_command)
        print("stop")

if __name__ == "__main__":
    Leftarm = simple_Exoskeleton() # 定义外骨骼
    Leftarm.set_param(1300, 600, 20) # 初始化参数
    Leftarm.connect(4) # 打开串口4，根据计算机的设备管理器给出！！！！！！！
    Leftarm.go(1000) # 运动到指定位置
    now_pos = Leftarm.read_position()
    print(now_pos)
    time.sleep(1)
    BCIexo.exoskeleton_stop()

    BCIexo.disconnect_com()




