# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/19 22:33
"""
# 导入所需模块
import json
import signal  # 用于捕捉信号
import sys
import threading
import time

import requests
from flask import Flask, redirect, url_for, request, render_template

# 创建 Flask 应用
app = Flask(__name__)


# 定义路由和视图函数

# 当访问 /admin 路径时，返回 Hello_Admin.
@app.route('/admin')
def hello_admin():
    return 'Hello_Admin.'


# 当访问 /guest/<guest> 路径时，返回 Hello <guest> as Guest.
@app.route('/guest/<guest>')
def hello_guest(guest):
    return f'Hello {guest} as Guest.'


# 当访问 /user/<name> 路径时，根据名字重定向到不同的页面
@app.route('/user/<name>')
def user(name):
    if name == 'admin':
        return redirect(url_for('hello_admin'))
    else:
        return redirect(url_for('hello_guest', guest=name))


# 当访问 /success/<name> 路径时，返回欢迎信息
@app.route('/success/<name>')
def success(name):
    return f'Welcome {name}.'


# 当访问 /login 路径时，根据请求方法从表单中获取用户名并重定向到欢迎页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['name']
        return redirect(url_for('success', name=user))
    else:
        user = request.args.get('name')
        return redirect(url_for('success', name=user))


# 当访问 /save_info/ 路径时，保存传递的 JSON 数据到文件，并重定向到打印信息的页面
@app.route('/save_info/', methods=['POST'])
def save_info():
    new_pcinfo = request.get_json()
    uid = new_pcinfo['UID']
    mac = new_pcinfo['MAC']
    client_ip = request.remote_addr  # 获取客户端 IP 地址

    pcinfo = {'UID': uid, 'IP': client_ip, 'MAC': mac}
    print(f"Received data: {pcinfo}")

    try:
        with open('pcinfo.json', 'r') as json_file:
            pcinfo_list = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pcinfo_list = []

    # 检查是否存在相同的 UID 和 MAC 地址
    for item in pcinfo_list:
        if item['UID'] == uid and item['MAC'] == mac:
            # 如果 UID 和 MAC 地址相同，则更新 IP 地址
            item['IP'] = client_ip
            break
    else:
        # 如果不存在相同的 UID 和 MAC 地址，则添加新的 PC 信息
        pcinfo_list.append(pcinfo)

    with open('pcinfo.json', 'w') as json_file:
        json.dump(pcinfo_list, json_file)

    return redirect(url_for('print_info'))


# 当访问 /print_info 路径时，从文件中读取保存的信息并在模板中显示
@app.route('/print_info')
def print_info():
    try:
        with open('pcinfo.json', 'r') as file:
            pcinfo = json.load(file)
    except FileNotFoundError:
        pcinfo = []

    return render_template('list.html', data=pcinfo)


# 当访问 /activate/ 路径时，从表单中获取 IP 地址和命令，发送请求给特定 IP 地址，并重定向到结果页面
@app.route('/activate/', methods=['POST'])
def activate():
    ip = request.form['ip']
    cmd = request.form['command']
    # print(ip, cmd)
    if ip and cmd:
        with open('result.txt', 'w') as f:
            f.write('')
        requests.get(f'http://{ip}/cmd/' + cmd)
        return redirect(url_for('result', ip=ip))
    else:
        return "IP or command is missing."


# 当访问 /result/ 路径时，接收来自客户端的数据并重定向到打印结果的页面
@app.route('/result/', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        with open('result.txt', 'a') as f:
            result = request.form['result']
            print(result)
            f.write(result)
    ip = request.args.get('ip')
    return redirect(url_for('print_result', ip=ip))


# 当访问 /print_result 路径时，从文件中读取结果并在模板中显示
@app.route('/print_result/<ip>')
def print_result(ip):
    with open('result.txt') as f:
        content = f.read()
    return render_template('result.html', content=content, ip=ip)


# 当访问根路径 / 时，返回首页
@app.route('/')
def index():
    return render_template('index.html')


# 当访问 /pcinfo 路径时，返回保存的 PC 信息的 JSON 数据
@app.route('/pcinfo', methods=['GET'])
def get_pcinfo():
    try:
        with open('pcinfo.json', 'r') as json_file:
            pcinfo = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pcinfo = []
    return json.dumps(pcinfo)


# 启动 Flask 应用的函数
def run_server():
    app.run('192.168.232.190', 90, False)


# 处理 Ctrl+C 中断信号
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


# 主函数入口
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)  # 捕捉 Ctrl+C 中断信号

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    try:
        while True:
            # print("Main thread is running...")
            time.sleep(1)
    except KeyboardInterrupt:
        print('Main thread interrupted. Exiting...')
        sys.exit(0)
