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

# 链接串口
    def connect(self, com_num):
        self.com_num = com_num
        if not self.Connected:
            self.link_to_exoskeleton()
            self.Connected = True
        self.reset_arm()
        # pos = self.read_position()
        # print(pos)



    # 连接串口，输入串口号和波特率
    def link_to_exoskeleton(self):
        print('Trying to Connect to com')
        try:
            self.com = serial.Serial('com' + str(self.com_num), self.baud_rate)
            print('Connect to com successfully')
        except Exception as e:
            print('Open serial failed.' + str(e))


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

# HERE IS THE Parameters Again!：
#     baudrate：9600
#     LEFT_ELBOW1_ID   1
#     RIGHT_ELBOW1_ID  2
#     LEFT_ELBOW2_ID   3  ！！！！
#     RIGHT_ELBOW2_ID  4  ！！！！
#     LEFT_WRIST_ID    5  ！！！！
#     RIGHT_WRIST_ID   6
#     LEFT_ELBOW1_range   [300, 1300]
#     RIGHT_ELBOW1_range  [1200, 2300]
#     LEFT_ELBOW2_range   [1700, 2500] ！！！！
#     RIGHT_ELBOW2_range  [200, 1300]  ！！！！
#     LEFT_WRIST_range    [300, 1000]  ！！！！
#     RIGHT_WRIST_range   [1000, 1600] 
#     具体还是看外骨骼上标签标注的


if __name__ == "__main__":
    Leftcontrol = simple_Exoskeleton() # 实例化左侧外骨骼
    Leftcontrol.connect(4)  # 打开串口4，对应左侧的控制板，根据计算机的设备管理器给出！！！！！！！
    Leftcontrol.go(3, 2000) # 使得左肘外骨骼的运动到指定位置
    Leftcontrol.go(5, 800)  # 使得左腕外骨骼的运动到指定位置
    time.sleep(1000)
    now_pos = Leftcontrol.read_position(3)  # 读取左肘外骨骼的当前位置
    print(now_pos)    #输出当前位置
    now_pos = Leftcontrol.read_position(3)  # 读取左腕外骨骼的当前位置
    print(now_pos)
    time.sleep(1)
    
    Rightcontrol = simple_Exoskeleton() # 定义右侧外骨骼
    Rightcontrol.connect(5)  # 打开串口5，根据计算机的设备管理器给出！！！！！！！
    Rightcontrol.go(4,1000)  # 使得右肘外骨骼运动到指定位置
    now_pos = Rightcontrol.read_position(4) # 读取右肘外骨骼的当前位置
    print(now_pos)
    time.sleep(1)

    Leftcontrol.exoskeleton_stop()
    Rightcontrol.exoskeleton_stop()
    Leftcontrol.disconnect_com()
    Rightcontrol.disconnect_com()



