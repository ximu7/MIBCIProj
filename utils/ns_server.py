# ！/usr/bin/env python
# coding:utf-8
import socket
import numpy as np

ip_port = ('localhost', 1234)
sk = socket.socket()
sk.bind(ip_port)  # 绑定ip端口
sk.listen(1)
while True:
    print('server waiting...')
    conn, addr = sk.accept()
    client_data = conn.recv(1024)
    print(str(client_data, 'utf8'))
    for i in range(90000):
        data = '12345623131'
        conn.sendall(bytes(data, 'utf8'))
    # conn.close()
