# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/19 22:33
"""
import json

import requests
from flask import Flask, redirect, url_for, request, render_template

app = Flask(__name__)


# flask中对于变量的使用

@app.route('/admin')
def hello_admin():
    return 'Hello_Admin.'


@app.route('/guest/<guest>')
def hello_guest(guest):
    return f'Hello {guest} as Guest.'


@app.route('/save_info/', methods=['POST', 'GET'])
def save_info():
    new_pcinfo = request.get_json()  # 获取JSON数据
    print(f"Received data: {new_pcinfo}")

    try:
        with open('pcinfo.json', 'r') as json_file:
            pcinfo = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pcinfo = []

    # 检查是否存在相同的 MAC 地址
    mac_exists = False
    for item in pcinfo:
        if item['MAC'] == new_pcinfo['MAC']:
            mac_exists = True
            break

    if not mac_exists:
        pcinfo.append(new_pcinfo)
        with open('pcinfo.json', 'w') as json_file:
            json.dump(pcinfo, json_file)

    return redirect(url_for('print_info'))


@app.route('/print_info')
def print_info():
    try:
        with open('pcinfo.json', 'r') as file:
            pcinfo = json.load(file)
    except FileNotFoundError:
        pcinfo = []

    return render_template('list.html', data=pcinfo)


@app.route('/user/<name>')
def user(name):
    if name == 'admin':
        return redirect(url_for('hello_admin'))
    else:
        return redirect(url_for('hello_guest', guest=name))


@app.route('/success/<name>')
def success(name):
    return f'Welcome {name}.'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['name']
        return redirect(url_for('success', name=user))
    else:
        user = request.args.get('name')
        return redirect(url_for('success', name=user))


@app.route('/activate/', methods=['POST'])
def activate():
    ip = request.form['ip']
    cmd = request.form['command']

    if ip and cmd:
        with open('result.txt', 'w') as f:
            f.write('')
        requests.get(f'http://{ip}/cmd/' + cmd)  # 确保IP地址正确传递到URL中
        return redirect(url_for('result', ip=ip))  # 默认get传输
    else:
        return "IP or command is missing."


@app.route('/result/', methods=['GET', 'POST'])
def result():
    # 接收来自client的数据
    if request.method == 'POST':
        with open('result.txt', 'a') as f:
            result = request.form['result']
            f.write(result)
    ip = request.args.get('ip')
    return redirect(url_for('print_result', ip=ip))


@app.route('/print_result')
def print_result():
    with open('result.txt') as f:
        content = f.read()
    ip = request.args.get('ip')  # 从请求参数中获取IP
    return render_template('result.html', content=content, ip=ip)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pcinfo', methods=['GET'])
def get_pcinfo():
    try:
        with open('pcinfo.json', 'r') as json_file:
            pcinfo = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pcinfo = []
    return json.dumps(pcinfo)


if __name__ == '__main__':
    app.run('127.0.0.1', 90, True)
